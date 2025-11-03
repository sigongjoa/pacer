import argparse
import random
from backend.model_registry import ModelRegistry

def monitor_model_performance(version: str):
    """
    Simulates monitoring the performance of a deployed model version.
    In a real scenario, this would involve collecting metrics from production
    traffic, analyzing them, and potentially triggering alerts or further actions.
    """
    model_info = ModelRegistry.get_model(version)
    if not model_info:
        print(f"Error: Model version {version} not found in registry. Cannot monitor.")
        return

    print(f"\n--- Monitoring Performance of Model Version {version} ---")
    print(f"Deployed model path: {model_info['path']}")
    print(f"Baseline metrics: {model_info['metrics']}")

    # Simulate collecting live production metrics
    simulated_live_accuracy = round(model_info['metrics']["accuracy"] * (1 + random.uniform(-0.02, 0.03)), 3)
    simulated_live_f1 = round(model_info['metrics']["f1"] * (1 + random.uniform(-0.01, 0.02)), 3)
    simulated_bad_feedback_rate = round(random.uniform(0.05, 0.15), 3)

    print(f"\nSimulated Live Metrics (Production):")
    print(f"  Accuracy: {simulated_live_accuracy}")
    print(f"  F1 Score: {simulated_live_f1}")
    print(f"  Bad Feedback Rate: {simulated_bad_feedback_rate}")

    # Simple alert condition
    if simulated_bad_feedback_rate > 0.12:
        print("\n!!! ALERT: High bad feedback rate detected for this model version. Investigation needed. !!!")
    elif simulated_live_accuracy < model_info['metrics']["accuracy"] * 0.95:
        print("\n!!! ALERT: Significant accuracy drop detected. Investigation needed. !!!")
    else:
        print("\nModel performance is within acceptable bounds.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate LLM model performance monitoring.")
    parser.add_argument("--version", type=str, required=True,
                        help="The version of the model to monitor (e.g., v1.0).")
    args = parser.parse_args()

    # For demonstration, ensure some models are registered
    if not ModelRegistry.get_model("v1.0"):
        ModelRegistry.register_model("v1.0", "/models/v1.0", {"accuracy": 0.85, "f1": 0.82})
    if not ModelRegistry.get_model("v1.1"):
        ModelRegistry.register_model("v1.1", "/models/v1.1", {"accuracy": 0.87, "f1": 0.84})

    monitor_model_performance(args.version)
