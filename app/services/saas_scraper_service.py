import logging
from scrapegraphai.graphs import DepthSearchGraph
from app.core.config import settings
from app.schemas import schemas
import anyio # Import anyio
from app.core.cqrs import CommandBus, QueryBus
from app.core.dependencies import AsyncSessionLocal, create_command_bus, create_query_bus
from app.commands.saas_info_commands import CreateSaaSInfoCommand, UpdateSaaSInfoCommand
from app.commands.feature_commands import CreateFeatureCommand, DeleteFeatureCommand
from app.commands.pricing_plan_commands import CreatePricingPlanCommand, DeletePricingPlanCommand
from app.queries.saas_info_queries import GetSaaSInfoByNameQuery
from app.queries.feature_queries import ListFeaturesQuery
from app.queries.pricing_plan_queries import ListPricingPlansQuery

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def perform_saas_scrape(
    url: str,
    command_bus: CommandBus | None = None,
    query_bus: QueryBus | None = None,
) -> None:
    if command_bus is None or query_bus is None:
        async with AsyncSessionLocal() as session:
            local_command_bus = create_command_bus(session)
            local_query_bus = create_query_bus(session)
            await _perform_saas_scrape(url, local_command_bus, local_query_bus)
    else:
        await _perform_saas_scrape(url, command_bus, query_bus)

async def _perform_saas_scrape(url: str, command_bus: CommandBus, query_bus: QueryBus) -> None:
    logging.info(f"Starting SaaS scrape for URL: {url}")

    graph_config = {
        "llm": {
            "api_key": settings.NVIDIA_KEY,
            "model": "nvidia/mistralai/mistral-nemotron",
            "temperature": 0,
            "format": "json",
        },
        "verbose": True,
        "headless": True,
        "depth": 2,
        "only_inside_links": True,
    }

    enhanced_prompt = """
    {
      "instruction": "Extract the name, a one-liner description, target segments, features, and pricing plans of the SaaS product from the given website. Ensure all extracted data strictly conforms to the SaaSInfo Pydantic model schema. If a field is not found, return it as null or an empty list as appropriate.",
      "fields_to_extract": {
        "name": "The official name of the SaaS product.",
        "one_liner": "A concise, single-sentence description of what the SaaS product does.",
        "target_segments": "A list of target customer segments or industries for the SaaS product. Return as an empty list if not found.",
        "features": "A list of key features offered by the SaaS product. Each feature should have a 'name' and 'description'. Return as an empty list if not found.",
        "pricing": "A list of pricing plans for the SaaS product. Each plan should have 'plan_name', 'price', 'features' (as a string or list of strings), and an optional 'link'. Return as an empty list if not found."
      },
      "output_format": "JSON, strictly adhering to the SaaSInfo Pydantic model structure, including 'name', 'one_liner', 'target_segments', 'features', and 'pricing' fields."
    }
    """

    search_graph = DepthSearchGraph(
        prompt=enhanced_prompt,
        source=url,
        schema=schemas.SaaSInfoCreate,  # Use the Pydantic schema for validation
        config=graph_config,
    )

    try:
        result = await anyio.to_thread.run_sync(search_graph.run)  # Run in a separate thread
        logging.info(f"SaaS scrape completed for URL: {url}")

        if result:
            logging.info(f"Scraped data: {result}")
            try:
                saas_info_create_schema = schemas.SaaSInfoCreate(**result)

                existing_saas_info = await query_bus.dispatch(GetSaaSInfoByNameQuery(name=saas_info_create_schema.name))

                saas_info_id = None
                db_saas_info = None

                if existing_saas_info:
                    saas_info_id = existing_saas_info.id
                    update_command = UpdateSaaSInfoCommand(
                        saas_info_id=existing_saas_info.id,
                        payload=saas_info_create_schema.model_dump()
                    )
                    db_saas_info = await command_bus.dispatch(update_command)
                    if db_saas_info:
                        saas_info_id = db_saas_info.id
                        logging.info(f"SaaS Info '{db_saas_info.name}' updated in database with ID: {db_saas_info.id}")
                    else:
                        logging.warning(
                            "SaaS Info update command returned no object for '%s'. Proceeding with existing ID.",
                            saas_info_create_schema.name,
                        )
                else:
                    create_command = CreateSaaSInfoCommand(
                        payload=saas_info_create_schema.model_dump()
                    )
                    db_saas_info = await command_bus.dispatch(create_command)
                    saas_info_id = db_saas_info.id
                    logging.info(f"SaaS Info '{db_saas_info.name}' saved to database with ID: {db_saas_info.id}")

                saas_info_id = saas_info_id or (db_saas_info.id if db_saas_info else None)
                if not saas_info_id:
                    raise ValueError("Unable to determine SaaS Info ID after scrape")

                await _sync_features(
                    saas_info_id=saas_info_id,
                    features=saas_info_create_schema.features or [],
                    command_bus=command_bus,
                    query_bus=query_bus,
                )

                await _sync_pricing_plans(
                    saas_info_id=saas_info_id,
                    pricing_plans=saas_info_create_schema.pricing or [],
                    command_bus=command_bus,
                    query_bus=query_bus,
                )
            except Exception as e:
                logging.error(f"Error validating, creating or updating SaaS Info from scrape result: {e} - Data: {result}")
        else:
            logging.error(f"No data scraped from URL: {url}")

    except Exception as e:
        logging.error(f"Error during SaaS scrape for URL {url}: {e}")

async def _sync_features(
    saas_info_id: int,
    features: list[schemas.FeatureCreate],
    command_bus: CommandBus,
    query_bus: QueryBus,
) -> None:
    existing_features = await query_bus.dispatch(
        ListFeaturesQuery(saas_info_id=saas_info_id, skip=0, limit=1000)
    )

    for feature in existing_features:
        await command_bus.dispatch(DeleteFeatureCommand(feature_id=feature.id))

    for feature in features:
        await command_bus.dispatch(
            CreateFeatureCommand(
                name=feature.name,
                description=feature.description,
                saas_info_id=saas_info_id,
            )
        )

async def _sync_pricing_plans(
    saas_info_id: int,
    pricing_plans: list[schemas.PricingPlanCreate],
    command_bus: CommandBus,
    query_bus: QueryBus,
) -> None:
    existing_pricing_plans = await query_bus.dispatch(
        ListPricingPlansQuery(saas_info_id=saas_info_id, skip=0, limit=1000)
    )

    for plan in existing_pricing_plans:
        await command_bus.dispatch(DeletePricingPlanCommand(pricing_plan_id=plan.id))

    for plan in pricing_plans:
        await command_bus.dispatch(
            CreatePricingPlanCommand(
                plan_name=plan.plan_name,
                price=plan.price,
                features=plan.features if plan.features is not None else [],
                link=plan.link,
                saas_info_id=saas_info_id,
            )
        )
