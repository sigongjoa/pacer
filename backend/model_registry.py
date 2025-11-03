from typing import Dict, Any, Optional

class ModelRegistry:
    _models: Dict[str, Dict[str, Any]] = {}
    _latest_version: Optional[str] = None

    @classmethod
    def register_model(cls, version: str, path: str, metrics: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Registers a new model version in the registry.
        """
        if version in cls._models:
            print(f"Warning: Model version {version} already exists. Overwriting.")
        
        cls._models[version] = {
            "path": path,
            "metrics": metrics,
            "metadata": metadata or {},
            "registered_at": "<timestamp_placeholder>" # In a real system, use datetime
        }
        cls._latest_version = version
        print(f"Model version {version} registered successfully.")

    @classmethod
    def get_model(cls, version: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific model version.
        """
        return cls._models.get(version)

    @classmethod
    def get_latest_model(cls) -> Optional[Dict[str, Any]]:
        """
        Retrieves the latest registered model.
        """
        if cls._latest_version:
            return cls._models.get(cls._latest_version)
        return None

    @classmethod
    def list_models(cls) -> Dict[str, Dict[str, Any]]:
        """
        Lists all registered models.
        """
        return cls._models

# Example Usage (for demonstration)
if __name__ == "__main__":
    registry = ModelRegistry()
    registry.register_model("v1.0", "/models/v1.0", {"accuracy": 0.85, "f1": 0.82})
    registry.register_model("v1.1", "/models/v1.1", {"accuracy": 0.87, "f1": 0.84}, {"trained_on": "2023-10-26"})

    print("\nLatest model:", registry.get_latest_model())
    print("\nModel v1.0:", registry.get_model("v1.0"))
    print("\nAll models:", registry.list_models())
