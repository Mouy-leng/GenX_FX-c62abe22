"""
Model Registry - Advanced model management and versioning
Handles model storage, versioning, and deployment
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_val_score

# Import statements moved to avoid circular imports


class ModelStatus(Enum):
    """Model status"""
    TRAINING = "training"
    VALIDATED = "validated"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"


class ModelType(Enum):
    """Model types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    ENSEMBLE = "ensemble"
    DEEP_LEARNING = "deep_learning"


@dataclass
class ModelMetadata:
    """Model metadata"""
    model_id: str
    name: str
    version: str
    model_type: ModelType
    status: ModelStatus
    created_at: datetime
    updated_at: datetime
    performance_metrics: Dict[str, float]
    feature_importance: Dict[str, float]
    training_data_hash: str
    model_hash: str
    dependencies: List[str]
    tags: List[str]
    description: str = ""


@dataclass
class ModelRegistryConfig:
    """Model registry configuration"""
    storage_path: str = "models"
    max_models_per_type: int = 10
    auto_cleanup: bool = True
    validation_threshold: float = 0.7
    deployment_threshold: float = 0.8
    backup_frequency: int = 3600  # seconds


class ModelRegistry:
    """
    Advanced model registry with versioning and deployment management
    """
    
    def __init__(self, config: ModelRegistryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.metrics = None
        
        # Storage management
        self.storage_path = Path(config.storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Model registry
        self.models = {}
        self.model_metadata = {}
        self.deployed_models = {}
        
        # Performance tracking
        self.model_performance = {}
        self.deployment_history = []
        
        # Background tasks
        self.is_running = False
        
    async def initialize(self, metrics=None) -> bool:
        """Initialize model registry"""
        try:
            self.logger.info("Initializing model registry...")
            
            # Set components if provided
            if metrics:
                self.metrics = metrics
            
            # Load existing models
            await self._load_models()
            
            # Start background tasks
            self.is_running = True
            asyncio.create_task(self._cleanup_loop())
            asyncio.create_task(self._performance_monitoring_loop())
            
            self.logger.info("Model registry initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize model registry: {e}")
            return False
    
    async def register_model(self, model: Any, metadata: ModelMetadata) -> bool:
        """Register a new model"""
        try:
            self.logger.info(f"Registering model: {metadata.model_id}")
            
            # Validate model
            if not await self._validate_model(model, metadata):
                return False
            
            # Save model
            model_path = self.storage_path / f"{metadata.model_id}_{metadata.version}"
            await self._save_model(model, model_path)
            
            # Save metadata
            metadata_path = model_path / "metadata.json"
            await self._save_metadata(metadata, metadata_path)
            
            # Update registry
            self.models[metadata.model_id] = model
            self.model_metadata[metadata.model_id] = metadata
            
            # Record metrics
            await self.metrics.record_model_registration(metadata)
            
            self.logger.info(f"Model registered successfully: {metadata.model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering model: {e}")
            return False
    
    async def load_model(self, model_id: str) -> Optional[Any]:
        """Load a model by ID"""
        try:
            if model_id in self.models:
                return self.models[model_id]
            
            # Load from storage
            model_path = self._find_model_path(model_id)
            if model_path:
                model = await self._load_model_from_path(model_path)
                self.models[model_id] = model
                return model
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading model {model_id}: {e}")
            return None
    
    async def load_scaler(self, scaler_id: str) -> Optional[Any]:
        """Load a scaler by ID"""
        try:
            scaler_path = self.storage_path / f"{scaler_id}.pkl"
            if scaler_path.exists():
                return joblib.load(scaler_path)
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading scaler {scaler_id}: {e}")
            return None
    
    async def save_model(self, model_id: str, model: Any) -> bool:
        """Save a model"""
        try:
            model_path = self.storage_path / f"{model_id}.pkl"
            
            joblib.dump(model, model_path)
            
            self.logger.info(f"Model saved: {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving model {model_id}: {e}")
            return False
    
    async def save_scaler(self, scaler_id: str, scaler: Any) -> bool:
        """Save a scaler"""
        try:
            scaler_path = self.storage_path / f"{scaler_id}.pkl"
            
            joblib.dump(scaler, scaler_path)
            
            self.logger.info(f"Scaler saved: {scaler_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving scaler {scaler_id}: {e}")
            return False
    
    async def get_latest_models(self) -> Dict[str, Any]:
        """Get the latest models by type"""
        try:
            latest_models = {}
            
            # Group models by type
            models_by_type = {}
            for model_id, metadata in self.model_metadata.items():
                model_type = metadata.model_type.value
                if model_type not in models_by_type:
                    models_by_type[model_type] = []
                models_by_type[model_type].append((model_id, metadata))
            
            # Get latest model for each type
            for model_type, model_list in models_by_type.items():
                # Sort by creation date
                model_list.sort(key=lambda x: x[1].created_at, reverse=True)
                
                if model_list:
                    latest_model_id, latest_metadata = model_list[0]
                    latest_model = await self.load_model(latest_model_id)
                    if latest_model:
                        latest_models[model_type] = {
                            'model': latest_model,
                            'metadata': latest_metadata
                        }
            
            return latest_models
            
        except Exception as e:
            self.logger.error(f"Error getting latest models: {e}")
            return {}
    
    async def deploy_model(self, model_id: str) -> bool:
        """Deploy a model for production use"""
        try:
            if model_id not in self.model_metadata:
                self.logger.error(f"Model not found: {model_id}")
                return False
            
            metadata = self.model_metadata[model_id]
            
            # Check deployment criteria
            if not await self._check_deployment_criteria(metadata):
                return False
            
            # Load model
            model = await self.load_model(model_id)
            if not model:
                return False
            
            # Deploy model
            self.deployed_models[model_id] = {
                'model': model,
                'metadata': metadata,
                'deployed_at': datetime.now()
            }
            
            # Update status
            metadata.status = ModelStatus.DEPLOYED
            metadata.updated_at = datetime.now()
            
            # Record deployment
            self.deployment_history.append({
                'model_id': model_id,
                'deployed_at': datetime.now(),
                'performance_metrics': metadata.performance_metrics
            })
            
            # Record metrics
            await self.metrics.record_model_deployment(metadata)
            
            self.logger.info(f"Model deployed: {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deploying model {model_id}: {e}")
            return False
    
    async def undeploy_model(self, model_id: str) -> bool:
        """Undeploy a model"""
        try:
            if model_id in self.deployed_models:
                del self.deployed_models[model_id]
                
                # Update status
                if model_id in self.model_metadata:
                    self.model_metadata[model_id].status = ModelStatus.VALIDATED
                    self.model_metadata[model_id].updated_at = datetime.now()
                
                self.logger.info(f"Model undeployed: {model_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error undeploying model {model_id}: {e}")
            return False
    
    async def get_deployed_models(self) -> Dict[str, Any]:
        """Get currently deployed models"""
        return self.deployed_models.copy()
    
    async def evaluate_model(self, model_id: str, test_data: Tuple[np.ndarray, np.ndarray]) -> Dict[str, float]:
        """Evaluate model performance"""
        try:
            model = await self.load_model(model_id)
            if not model:
                return {}
            
            X_test, y_test = test_data
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            metrics = {}
            
            if hasattr(model, 'predict_proba'):
                y_pred_proba = model.predict_proba(X_test)
                if y_pred_proba.shape[1] == 2:
                    y_pred_proba = y_pred_proba[:, 1]
                
                # Binary classification metrics
                metrics['accuracy'] = accuracy_score(y_test, y_pred)
                metrics['precision'] = precision_score(y_test, y_pred, average='binary')
                metrics['recall'] = recall_score(y_test, y_pred, average='binary')
                metrics['f1_score'] = f1_score(y_test, y_pred, average='binary')
                
                # Cross-validation
                cv_scores = cross_val_score(model, X_test, y_test, cv=5)
                metrics['cv_mean'] = cv_scores.mean()
                metrics['cv_std'] = cv_scores.std()
            
            else:
                # Regression metrics
                from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
                
                metrics['mse'] = mean_squared_error(y_test, y_pred)
                metrics['mae'] = mean_absolute_error(y_test, y_pred)
                metrics['r2'] = r2_score(y_test, y_pred)
            
            # Update model performance
            self.model_performance[model_id] = metrics
            
            # Update metadata
            if model_id in self.model_metadata:
                self.model_metadata[model_id].performance_metrics = metrics
                self.model_metadata[model_id].updated_at = datetime.now()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error evaluating model {model_id}: {e}")
            return {}
    
    async def compare_models(self, model_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple models"""
        try:
            comparison = {}
            
            for model_id in model_ids:
                if model_id in self.model_performance:
                    comparison[model_id] = self.model_performance[model_id]
                else:
                    # Evaluate if not already evaluated
                    model = await self.load_model(model_id)
                    if model:
                        # This would need test data - simplified for now
                        comparison[model_id] = {'status': 'not_evaluated'}
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Error comparing models: {e}")
            return {}
    
    async def _validate_model(self, model: Any, metadata: ModelMetadata) -> bool:
        """Validate model before registration"""
        try:
            # Check model type
            if not isinstance(model, (object,)):
                return False
            
            # Check performance metrics
            if metadata.performance_metrics:
                for metric, value in metadata.performance_metrics.items():
                    if not isinstance(value, (int, float)):
                        return False
            
            # Check required fields
            required_fields = ['model_id', 'name', 'version', 'model_type', 'status']
            for field in required_fields:
                if not hasattr(metadata, field) or getattr(metadata, field) is None:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating model: {e}")
            return False
    
    async def _check_deployment_criteria(self, metadata: ModelMetadata) -> bool:
        """Check if model meets deployment criteria"""
        try:
            # Check status
            if metadata.status != ModelStatus.VALIDATED:
                return False
            
            # Check performance metrics
            if metadata.performance_metrics:
                # Check if metrics meet threshold
                for metric, value in metadata.performance_metrics.items():
                    if metric in ['accuracy', 'precision', 'recall', 'f1_score']:
                        if value < self.config.deployment_threshold:
                            return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking deployment criteria: {e}")
            return False
    
    async def _save_model(self, model: Any, model_path: Path) -> None:
        """Save model to storage"""
        try:
            model_path.mkdir(parents=True, exist_ok=True)
            
            # Save model using joblib (safer than pickle)
            model_file = model_path / "model.pkl"
            joblib.dump(model, model_file)
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            raise
    
    async def _save_metadata(self, metadata: ModelMetadata, metadata_path: Path) -> None:
        """Save model metadata"""
        try:
            metadata_dict = {
                'model_id': metadata.model_id,
                'name': metadata.name,
                'version': metadata.version,
                'model_type': metadata.model_type.value,
                'status': metadata.status.value,
                'created_at': metadata.created_at.isoformat(),
                'updated_at': metadata.updated_at.isoformat(),
                'performance_metrics': metadata.performance_metrics,
                'feature_importance': metadata.feature_importance,
                'training_data_hash': metadata.training_data_hash,
                'model_hash': metadata.model_hash,
                'dependencies': metadata.dependencies,
                'tags': metadata.tags,
                'description': metadata.description
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata_dict, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error saving metadata: {e}")
            raise
    
    async def _load_models(self) -> None:
        """Load models from storage"""
        try:
            for model_dir in self.storage_path.iterdir():
                if model_dir.is_dir():
                    metadata_path = model_dir / "metadata.json"
                    if metadata_path.exists():
                        with open(metadata_path, 'r') as f:
                            metadata_dict = json.load(f)
                        
                        # Convert back to ModelMetadata
                        metadata = ModelMetadata(
                            model_id=metadata_dict['model_id'],
                            name=metadata_dict['name'],
                            version=metadata_dict['version'],
                            model_type=ModelType(metadata_dict['model_type']),
                            status=ModelStatus(metadata_dict['status']),
                            created_at=datetime.fromisoformat(metadata_dict['created_at']),
                            updated_at=datetime.fromisoformat(metadata_dict['updated_at']),
                            performance_metrics=metadata_dict['performance_metrics'],
                            feature_importance=metadata_dict['feature_importance'],
                            training_data_hash=metadata_dict['training_data_hash'],
                            model_hash=metadata_dict['model_hash'],
                            dependencies=metadata_dict['dependencies'],
                            tags=metadata_dict['tags'],
                            description=metadata_dict.get('description', '')
                        )
                        
                        self.model_metadata[metadata.model_id] = metadata
                        
                        # Load model if deployed
                        if metadata.status == ModelStatus.DEPLOYED:
                            model = await self._load_model_from_path(model_dir)
                            if model:
                                self.deployed_models[metadata.model_id] = {
                                    'model': model,
                                    'metadata': metadata,
                                    'deployed_at': metadata.updated_at
                                }
            
            self.logger.info(f"Loaded {len(self.model_metadata)} models")
            
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
    
    async def _load_model_from_path(self, model_path: Path) -> Optional[Any]:
        """Load model from path"""
        try:
            model_file = model_path / "model.pkl"
            if model_file.exists():
                return joblib.load(model_file)
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading model from path: {e}")
            return None
    
    def _find_model_path(self, model_id: str) -> Optional[Path]:
        """Find model path by ID"""
        try:
            for model_dir in self.storage_path.iterdir():
                if model_dir.is_dir() and model_id in model_dir.name:
                    return model_dir
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding model path: {e}")
            return None
    
    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of old models"""
        while self.is_running:
            try:
                if self.config.auto_cleanup:
                    await self._cleanup_old_models()
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_models(self) -> None:
        """Clean up old models"""
        try:
            # Group models by type
            models_by_type = {}
            for model_id, metadata in self.model_metadata.items():
                model_type = metadata.model_type.value
                if model_type not in models_by_type:
                    models_by_type[model_type] = []
                models_by_type[model_type].append((model_id, metadata))
            
            # Clean up excess models
            for model_type, model_list in models_by_type.items():
                if len(model_list) > self.config.max_models_per_type:
                    # Sort by creation date (oldest first)
                    model_list.sort(key=lambda x: x[1].created_at)
                    
                    # Remove oldest models
                    excess_count = len(model_list) - self.config.max_models_per_type
                    for i in range(excess_count):
                        model_id, metadata = model_list[i]
                        await self._remove_model(model_id)
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old models: {e}")
    
    async def _remove_model(self, model_id: str) -> None:
        """Remove a model"""
        try:
            # Remove from registry
            if model_id in self.models:
                del self.models[model_id]
            
            if model_id in self.model_metadata:
                del self.model_metadata[model_id]
            
            if model_id in self.deployed_models:
                del self.deployed_models[model_id]
            
            # Remove from storage
            model_path = self._find_model_path(model_id)
            if model_path and model_path.exists():
                import shutil
                shutil.rmtree(model_path)
            
            self.logger.info(f"Model removed: {model_id}")
            
        except Exception as e:
            self.logger.error(f"Error removing model {model_id}: {e}")
    
    async def _performance_monitoring_loop(self) -> None:
        """Monitor model performance"""
        while self.is_running:
            try:
                # Check deployed models performance
                for model_id, model_info in self.deployed_models.items():
                    if model_id in self.model_performance:
                        performance = self.model_performance[model_id]
                        
                        # Check if performance degraded
                        if 'accuracy' in performance and performance['accuracy'] < self.config.validation_threshold:
                            self.logger.warning(f"Model performance degraded: {model_id}")
                            # Could trigger model retraining or fallback
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(1800)
    
    def get_status(self) -> Dict[str, Any]:
        """Get model registry status"""
        return {
            'total_models': len(self.model_metadata),
            'deployed_models': len(self.deployed_models),
            'models_by_type': {
                model_type.value: len([
                    m for m in self.model_metadata.values() 
                    if m.model_type == model_type
                ]) for model_type in ModelType
            },
            'deployment_history_count': len(self.deployment_history),
            'config': self.config.__dict__
        }
