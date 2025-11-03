import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

REGISTRY_FILE = "model_registry.json"

class ModelRegistry:
    _models: Dict[str, Dict[str, Any]] = {}
    _active_production_model: Optional[str] = None

    def __init__(self):
        self._load_registry()

    def _load_registry(self):
        if os.path.exists(REGISTRY_FILE):
            try:
                with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._models = data.get("models", {})
                    self._active_production_model = data.get("active_production_model")
            except json.JSONDecodeError:
                print(f"Warning: Could not decode {REGISTRY_FILE}. Starting with empty registry.")
        else:
            print(f"Info: {REGISTRY_FILE} not found. Starting with empty registry.")

    def _save_registry(self):
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump({"models": self._models, "active_production_model": self._active_production_model}, f, indent=4, ensure_ascii=False)

    def register_model(self, version: str, path: str, metrics: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Registers a new model version in the registry.
        """
        if version in self._models:
            print(f"Warning: Model version {version} already exists. Overwriting.")
        
        self._models[version] = {
            "path": path,
            "metrics": metrics,
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "production_status": "inactive" # Can be 'inactive', 'staging', 'production'
        }
        self._save_registry()
        print(f"Model version {version} registered successfully.")

    def get_model(self, version: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific model version.
        """
        return self._models.get(version)

    def get_latest_model(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves the latest registered model based on registration time.
        """
        if not self._models:
            return None
        
        latest_version = None
        latest_timestamp = ""
        for version, info in self._models.items():
            if info["registered_at"] > latest_timestamp:
                latest_timestamp = info["registered_at"]
                latest_version = version
        return self._models.get(latest_version)

    def set_model_production_status(self, version: str, status: str) -> bool:
        """
        Sets the production status of a specific model version.
        Valid statuses: 'inactive', 'staging', 'production'.
        Only one model can be 'production' at a time.
        """
        if version not in self._models:
            print(f"Error: Model version {version} not found.")
            return False
        
        if status == "production":
            # Deactivate current production model if any
            if self._active_production_model and self._active_production_model in self._models:
                self._models[self._active_production_model]["production_status"] = "inactive"
            self._active_production_model = version
        
        self._models[version]["production_status"] = status
        self._save_registry()
        print(f"Model {version} production status set to {status}.")
        return True

    def get_active_production_model(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves the model currently marked as 'production'.
        """
        if self._active_production_model and self._active_production_model in self._models:
            return self._models[self._active_production_model]
        return None

    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Lists all registered models.
        """
        return self._models

    def list_production_models(self) -> List[Dict[str, Any]]:
        """
        Lists models currently in production or staging.
        """
        return [info for info in self._models.values() if info["production_status"] in ["staging", "production"]]

# Example Usage (for demonstration)
if __name__ == "__main__":
    registry = ModelRegistry()
    registry.register_model("v1.0", "/models/v1.0", {"accuracy": 0.85, "f1": 0.82})
    registry.register_model("v1.1", "/models/v1.1", {"accuracy": 0.87, "f1": 0.84}, {"trained_on": "2023-10-26"})

    print("\nAll models:", registry.list_models())
    print("\nLatest model:", registry.get_latest_model())

    registry.set_model_production_status("v1.0", "production")
    print("\nActive production model:", registry.get_active_production_model())

    registry.register_model("v1.2", "/models/v1.2", {"accuracy": 0.88, "f1": 0.86})
    registry.set_model_production_status("v1.2", "staging")
    print("\nProduction/Staging models:", registry.list_production_models())