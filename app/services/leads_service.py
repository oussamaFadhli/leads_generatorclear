import json
import logging
import anyio
from scrapegraphai.graphs import SearchGraph
from app.core.config import settings
from app.schemas import schemas
from app.core.cqrs import CommandBus, QueryBus
from app.core.dependencies import AsyncSessionLocal, create_command_bus, create_query_bus
from app.commands.lead_commands import CreateLeadCommand
from app.queries.saas_info_queries import GetSaaSInfoByIdQuery

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def perform_leads_search(
    saas_info_id: int,
    command_bus: CommandBus | None = None,
    query_bus: QueryBus | None = None,
):
    if command_bus is None or query_bus is None:
        async with AsyncSessionLocal() as session:
            local_command_bus = create_command_bus(session)
            local_query_bus = create_query_bus(session)
            return await _perform_leads_search(saas_info_id, local_command_bus, local_query_bus)
    return await _perform_leads_search(saas_info_id, command_bus, query_bus)

async def _perform_leads_search(saas_info_id: int, command_bus: CommandBus, query_bus: QueryBus):
    logging.info(f"--- Entering perform_leads_search for SaaS Info ID: {saas_info_id} ---")
    logging.info(f"Starting lead search for SaaS Info ID: {saas_info_id}")
    saas_info_db = await query_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if not saas_info_db:
        logging.error(f"SaaS Info with ID {saas_info_id} not found.")
        return

    # Convert Pydantic model to a dictionary for the prompt
    saas_info_dict = {
        "name": saas_info_db.name,
        "one_liner": saas_info_db.one_liner,
        "features": [{"name": f.name, "desc": f.description} for f in saas_info_db.features],
        "pricing": [{"plan_name": p.plan_name, "price": p.price, "features": p.features, "link": p.link} for p in saas_info_db.pricing],
        "target_segments": saas_info_db.target_segments
    }
    logging.info(f"SaaS Info Dict for prompt: {json.dumps(saas_info_dict, indent=2)}")

    prompt_dict = f"""
    Based on the following SaaS project information, search the internet for:
    1. Competitors: Identify a list of key competitors in the market (at least 3, up to 8).
    2. Strengths and Weaknesses: For each competitor, list their main strengths and weaknesses as a list of strings.
    3. Related Subreddits: Find the best subreddits related to the project's interests.

    SaaS Project Information:
    {json.dumps(saas_info_dict, indent=2)}

    IMPORTANT: Return the output as a JSON object with the following structure:
    {{
        "competitors": [
            {{
                "name": "Name of the competitor",
                "strengths": ["strength1", "strength2"],
                "weaknesses": ["weakness1", "weakness2"]
            }},
            {{
                "name": "Another competitor",
                "strengths": ["strength1", "strength2"],
                "weaknesses": ["weakness1", "weakness2"]
            }}
        ],
        "related_subreddits": ["subreddit1", "subreddit2", "subreddit3"]
    }}

    Return ONLY the JSON object, no additional text or markdown formatting.
    """

    graph_config = {
        "llm": {
            "api_key": settings.NVIDIA_KEY,
            "model": "nvidia/mistralai/mistral-nemotron",
            "temperature": 0,
            "format": "json",
        },
        "max_results": 7,
        "loader_kwargs": {"slow_mo": 10000},
        "verbose": True,
        "headless": True,
    }

    search_graph = SearchGraph(
        prompt=prompt_dict, config=graph_config
    )

    try:
        raw_output = await anyio.to_thread.run_sync(search_graph.run)
        logging.info(f"Lead search completed for SaaS Info ID: {saas_info_id}")
        logging.info(f"Raw output from search_graph.run(): {raw_output}")
        logging.info(f"Raw output type: {type(raw_output)}")

        processed_result = None
        
        # Handle string output
        if isinstance(raw_output, str):
            try:
                processed_result = json.loads(raw_output)
                logging.info(f"Parsed JSON from string. Result type: {type(processed_result)}")
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse SearchGraph result as JSON: {e}")
                logging.error(f"Raw output was: {raw_output}")
                return
        else:
            processed_result = raw_output
            logging.info(f"Using raw output directly. Type: {type(processed_result)}")

        # Log the structure of processed_result
        if isinstance(processed_result, dict):
            logging.info(f"Processed result is a dict with keys: {processed_result.keys()}")
        else:
            logging.error(f"Unexpected format: {type(processed_result)}. Expected a dictionary.")
            return

        if "competitors" not in processed_result or not isinstance(processed_result["competitors"], list):
            logging.error("Processed result does not contain a 'competitors' list.")
            return

        if "related_subreddits" not in processed_result:
            logging.warning("Processed result does not contain 'related_subreddits'. Using empty list.")
            all_related_subreddits = []
        else:
            all_related_subreddits = processed_result["related_subreddits"]
            if isinstance(all_related_subreddits, str):
                try:
                    all_related_subreddits = json.loads(all_related_subreddits)
                except json.JSONDecodeError:
                    logging.error(f"Could not parse top-level related_subreddits as JSON: {all_related_subreddits}")
                    all_related_subreddits = []
            if not isinstance(all_related_subreddits, list):
                logging.error(f"Top-level related_subreddits is not a list: {type(all_related_subreddits)}")
                all_related_subreddits = []

        logging.info(f"Processing {len(processed_result['competitors'])} competitors")

        created_leads = []
        for idx, competitor_item in enumerate(processed_result["competitors"]):
            logging.info(f"Processing competitor {idx + 1}/{len(processed_result['competitors'])}")
            
            if not isinstance(competitor_item, dict):
                logging.error(f"Competitor item is not a dict: {type(competitor_item)} - {competitor_item}")
                continue
                
            required_fields = ["name", "strengths", "weaknesses"]
            missing_fields = [f for f in required_fields if f not in competitor_item]
            
            if missing_fields:
                logging.error(f"Competitor item missing required fields: {missing_fields}")
                logging.error(f"Available keys: {competitor_item.keys()}")
                continue
            
            try:
                lead_data = {
                    "competitor_name": competitor_item["name"],
                    "strengths": competitor_item.get("strengths", []),
                    "weaknesses": competitor_item.get("weaknesses", []),
                    "related_subreddits": all_related_subreddits # Associate top-level subreddits with each lead
                }

                # Ensure strengths and weaknesses are lists of strings
                for key in ["strengths", "weaknesses"]:
                    if isinstance(lead_data[key], str):
                        try:
                            lead_data[key] = json.loads(lead_data[key])
                        except json.JSONDecodeError:
                            logging.error(f"Could not parse {key} as JSON for {lead_data['competitor_name']}: {lead_data[key]}")
                            lead_data[key] = []
                    if not isinstance(lead_data[key], list):
                        logging.error(f"{key} is not a list for {lead_data['competitor_name']}: {type(lead_data[key])}")
                        lead_data[key] = []

                logging.info(f"Creating lead with data: {lead_data}")
                create_command = CreateLeadCommand(
                    competitor_name=lead_data["competitor_name"],
                    strengths=lead_data["strengths"],
                    weaknesses=lead_data["weaknesses"],
                    related_subreddits=lead_data["related_subreddits"],
                    saas_info_id=saas_info_id
                )
                created_lead = await command_bus.dispatch(create_command)
                created_leads.append(created_lead)
                logging.info(f"Successfully created lead with ID: {created_lead.id if hasattr(created_lead, 'id') else 'unknown'}")
                
            except Exception as e:
                logging.error(f"Error validating or creating lead: {e}")
                logging.error(f"Lead data was: {lead_data}")
                import traceback
                logging.error(f"Traceback: {traceback.format_exc()}")
        
        # Return the list of created leads (or a simplified representation)
        return {"competitors": [schemas.Lead.model_validate(lead).model_dump() for lead in created_leads], "related_subreddits": all_related_subreddits}

    except Exception as e:
        logging.error(f"Error during lead search for SaaS Info ID {saas_info_id}: {e}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
