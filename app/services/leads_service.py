import json
from sqlalchemy.orm import Session
from scrapegraphai.graphs import SearchGraph
from app.core.config import settings
from app.models import models
from app.crud import crud
from app.schemas import schemas
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def perform_leads_search(saas_info_id: int, db: Session):
    logging.info(f"Starting lead search for SaaS Info ID: {saas_info_id}")
    saas_info_db = crud.get_saas_info(db, saas_info_id)
    if not saas_info_db:
        logging.error(f"SaaS Info with ID {saas_info_id} not found.")
        return

    # Convert SQLAlchemy model to a dictionary for the prompt
    saas_info_dict = {
        "name": saas_info_db.name,
        "one_liner": saas_info_db.one_liner,
        "features": [{"name": f.name, "desc": f.description} for f in saas_info_db.features],
        "pricing": [{"plan_name": p.plan_name, "price": p.price, "features": p.features, "link": p.link} for p in saas_info_db.pricing],
        "target_segments": saas_info_db.target_segments
    }

    prompt_dict = f"""
    Based on the following SaaS project information, search the internet for:
    1. A famous competitor: Identify a key competitor in the market.
    2. Strengths and Weaknesses: For this competitor, list their main strengths and weaknesses.
    3. Related Subreddits: Find the best subreddits related to the project's interests.

    SaaS Project Information:
    {json.dumps(saas_info_dict, indent=2)}

    Please provide the output in a JSON format that matches the Pydantic schema for a single Lead, including sources:
    {{
        "competitor_name": "string",
        "strength": "string",
        "weakness": "string",
        "related_subreddits": ["string", "string"],
        "sources": ["string", "string"]
    }}
    """

    graph_config = {
        "llm": {
            "api_key": settings.NVIDIA_KEY,
            "model": "nvidia/mistralai/mistral-nemotron",
            "temperature": 0,
            "format": "json",
            # "backend": "undetected_chromedriver"
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
        result = search_graph.run()
        logging.info(f"Lead search completed for SaaS Info ID: {saas_info_id}")

        # The result is a dictionary containing 'competitor_name', 'strength', 'weakness', 'related_subreddits', and 'sources'
        if isinstance(result, dict) and "competitor_name" in result and "related_subreddits" in result:
            try:
                lead_data = result.copy() # Make a copy to modify
                # Ensure related_subreddits is a list for Pydantic validation
                if "related_subreddits" in lead_data and not isinstance(lead_data["related_subreddits"], list):
                    # If it's a string, try to parse it as JSON, otherwise default to an empty list
                    try:
                        lead_data["related_subreddits"] = json.loads(lead_data["related_subreddits"])
                    except (json.JSONDecodeError, TypeError):
                        lead_data["related_subreddits"] = []
                elif "related_subreddits" not in lead_data:
                    lead_data["related_subreddits"] = []
                
                # Remove 'sources' as it's not part of the LeadCreate schema
                lead_data.pop("sources", None)

                lead_schema = schemas.LeadCreate(**lead_data)
                crud.create_lead(db, lead_schema, saas_info_id)
            except Exception as e:
                logging.error(f"Error validating or creating lead from search result: {e} - Data: {lead_data}")
        else:
            logging.error(f"Unexpected format from SearchGraph.run(): {result}")

    except Exception as e:
        logging.error(f"Error during lead search for SaaS Info ID {saas_info_id}: {e}")
