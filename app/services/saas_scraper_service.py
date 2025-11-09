import logging
from sqlalchemy.orm import Session
from scrapegraphai.graphs import DepthSearchGraph
from app.core.config import settings
from app.models import models
from app.crud import crud
from app.schemas import schemas
import anyio # Import anyio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def perform_saas_scrape(url: str, db: Session):
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
        "depth": 1,
        "only_inside_links": False,
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
        schema=schemas.SaaSInfoCreate, # Use the Pydantic schema for validation
        config=graph_config,
    )

    try:
        result = await anyio.to_thread.run_sync(search_graph.run) # Run in a separate thread
        logging.info(f"SaaS scrape completed for URL: {url}")

        if result:
            logging.info(f"Scraped data: {result}")
            try:
                saas_info_create_schema = schemas.SaaSInfoCreate(**result)
                
                existing_saas_info = crud.get_saas_info_by_name(db, saas_info_create_schema.name)
                if existing_saas_info:
                    db_saas_info = crud.update_saas_info(db, existing_saas_info.id, saas_info_create_schema)
                    logging.info(f"SaaS Info '{db_saas_info.name}' updated in database with ID: {db_saas_info.id}")
                else:
                    db_saas_info = crud.create_saas_info(db, saas_info_create_schema)
                    logging.info(f"SaaS Info '{db_saas_info.name}' saved to database with ID: {db_saas_info.id}")
            except Exception as e:
                logging.error(f"Error validating, creating or updating SaaS Info from scrape result: {e} - Data: {result}")
        else:
            logging.error(f"No data scraped from URL: {url}")

    except Exception as e:
        logging.error(f"Error during SaaS scrape for URL {url}: {e}")
    finally:
        db.close()
