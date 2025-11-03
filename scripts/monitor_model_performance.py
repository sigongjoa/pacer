import argparse
import random
import logging
from backend.model_registry import ModelRegistry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def monitor_model_performance(version: str):
    """
    Simulates monitoring the performance of a deployed model version.
    In a real scenario, this would involve collecting metrics from production
    traffic, analyzing them, and potentially triggering alerts or further actions.
    """
    registry = ModelRegistry()
    model_info = registry.get_model(version)
    if not model_info:
        logging.error(f"Error: Model version {version} not found in registry. Cannot monitor.")
        return

    logging.info(f"\n--- Monitoring Performance of Model Version {version} ---")
    logging.info(f"Deployed model path: {model_info['path']}")
    logging.info(f"Baseline metrics: {model_info['metrics']}")
    logging.info(f"Production Status: {model_info.get('production_status', 'unknown')}")

    # Simulate collecting live production metrics, including feedback rates
    simulated_live_accuracy = round(model_info['metrics'].get("accuracy", 0) * (1 + random.uniform(-0.02, 0.03)), 3)
    simulated_live_f1 = round(model_info['metrics'].get("f1_score", 0) * (1 + random.uniform(-0.01, 0.02)), 3)
    simulated_good_feedback_rate = round(random.uniform(0.75, 0.95), 3) # Percentage of GOOD feedback
    simulated_bad_feedback_rate = round(1 - simulated_good_feedback_rate, 3) # Percentage of BAD feedback

    logging.info(f"\nSimulated Live Metrics (Production):")
    logging.info(f"  Accuracy: {simulated_live_accuracy}")
    logging.info(f"  F1 Score: {simulated_live_f1}")
    logging.info(f"  Good Feedback Rate: {simulated_good_feedback_rate}")
    logging.info(f"  Bad Feedback Rate: {simulated_bad_feedback_rate}")

    # Simple alert conditions based on simulated metrics
    if simulated_bad_feedback_rate > 0.15: # If more than 15% feedback is bad
        logging.warning("\n!!! ALERT: High bad feedback rate detected for this model version. Investigation needed. !!!")
    elif simulated_live_accuracy < model_info['metrics'].get("accuracy", 0) * 0.90: # 10% drop in accuracy
        logging.warning("\n!!! ALERT: Significant accuracy drop detected. Investigation needed. !!!")
    else:
        logging.info("\nModel performance is within acceptable bounds.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate LLM model performance monitoring.")
    parser.add_argument("--version", type=str, required=True,
                        help="The version of the model to monitor (e.g., v1.0).")
    args = parser.parse_args()

    monitor_model_performance(args.version)