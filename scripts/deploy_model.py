import argparse
import logging

# Conceptual MLflow client (replace with actual mlflow import in a real project)
class ConceptualMlflowClient:
    def transition_model_version_stage(self, name, version, stage):
        logging.info(f"[MLflowClient] Transitioning model '{name}' version {version} to stage '{stage}'.")
        # In a real scenario, this would update the MLflow Model Registry
        from backend.model_registry import ModelRegistry
        registry = ModelRegistry()
        registry.set_model_production_status(version, stage.lower()) # Map MLflow stages to our conceptual statuses

conceptual_mlflow_client = ConceptualMlflowClient()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def deploy_model(model_name: str, version: str, stage: str):
    """
    Simulates the deployment of a specific model version by transitioning its stage in MLflow Model Registry.
    """
    logging.info(f"\n--- Simulating Deployment of Model '{model_name}' Version {version} to {stage.upper()} ---")
    
    try:
        conceptual_mlflow_client.transition_model_version_stage(name=model_name, version=version, stage=stage)
        logging.info(f"Model '{model_name}' version {version} successfully transitioned to {stage} stage.")
        logging.info(f"The serving endpoint would now use model version {version} for {stage} traffic.")
    except Exception as e:
        logging.error(f"Failed to deploy model '{model_name}' version {version}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate LLM model deployment.")
    parser.add_argument("--model_name", type=str, required=True,
                        help="The name of the model in MLflow Model Registry.")
    parser.add_argument("--version", type=str, required=True,
                        help="The version of the model to deploy (e.g., v1.0).")
    parser.add_argument("--stage", type=str, default="Production",
                        choices=["None", "Staging", "Production"],
                        help="The MLflow stage to set for the model version.")
    args = parser.parse_args()

    deploy_model(args.model_name, args.version, args.stage)
