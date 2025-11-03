import argparse
import logging
from backend.model_registry import ModelRegistry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def deploy_model(version: str, status: str):
    """
    Simulates the deployment of a specific model version by setting its production status.
    In a real scenario, this would involve updating a model serving endpoint
    to use the specified model version, potentially with traffic splitting.
    """
    registry = ModelRegistry()
    model_info = registry.get_model(version)
    if not model_info:
        logging.error(f"Error: Model version {version} not found in registry. Cannot deploy.")
        return

    logging.info(f"\n--- Simulating Deployment of Model Version {version} to {status.upper()} ---")
    success = registry.set_model_production_status(version, status)
    
    if success:
        logging.info(f"Model {version} successfully marked as {status}.")
        logging.info(f"The serving endpoint would now use model version {version} for {status} traffic.")
    else:
        logging.error(f"Failed to set production status for model {version}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate LLM model deployment.")
    parser.add_argument("--version", type=str, required=True,
                        help="The version of the model to deploy (e.g., v1.0).")
    parser.add_argument("--status", type=str, default="production",
                        choices=["inactive", "staging", "production"],
                        help="The production status to set for the model.")
    args = parser.parse_args()

    deploy_model(args.version, args.status)