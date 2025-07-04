import logging
from azion_resources import AzionResource
from akamai.converter import process_resource
from utils import log_conversion_summary
from akamai.utils import extract_edge_hostname, get_main_setting_name, find_origin_hostname

def generate_azion_config(akamai_config: dict) -> dict:
    """
    Converts Akamai configuration to Azion-compatible configuration.

    Args:
        akamai_config (dict): The Akamai configuration to convert.

    Returns:
        dict: The Azion-compatible configuration.
    """
    azion_resources = AzionResource("azion_resources")
    try:
        # Step 1: Extract edge_hostname
        edge_hostname = extract_edge_hostname(akamai_config)
        if not edge_hostname:
            logging.warning("Edge hostname not found. Using placeholder as fallback.")
            edge_hostname = "placeholder.example.com"

        # Step 2: Deduce the main setting name
        main_setting_name = get_main_setting_name(akamai_config)

        # Add environment parameter if not production
        environment = akamai_config.get("context", {}).get("environment", "production")
        if environment != "production":
            main_setting_name = f"{main_setting_name}_{environment}"
        logging.info(f"Main setting name deduced: {main_setting_name}")

        # Step 3: Find origin hostname
        origin_hostname = find_origin_hostname(akamai_config)
        if not origin_hostname:
            logging.warning("Origin hostname not found. Using placeholder as fallback.")
            origin_hostname = "placeholder.example.com"

        # Add global settings
        azion_resources.append({
            "type": "global_settings",
            "name": "global_settings",
            "attributes": {
                "main_setting_name": main_setting_name,
                "edge_hostname": edge_hostname,
                "origin_hostname": origin_hostname,
                "function_map": akamai_config.get("function_map"),
                "environment": environment,
                "context": akamai_config.get("context", {})
            }
        })
        
        # Process resources
        for resource in akamai_config.get("resource", []):
            process_resource(azion_resources, resource)
            
    except Exception as e:
        logging.error(f"Error processing resource: {e}")
        raise
    
    # Log a summary of the generated resources
    log_conversion_summary(azion_resources.get_azion_resources())

    return {"resources": azion_resources.get_azion_resources()}

def akamai_converter(config: dict) -> dict:
    """
    Process Akamai configuration and return Azion-compatible configuration.

    Args:
        config (dict): The Akamai configuration to convert.

    Returns:
        dict: The Azion-compatible configuration.
    """
    logging.info("Converting Akamai configuration.")
    return generate_azion_config(config)
