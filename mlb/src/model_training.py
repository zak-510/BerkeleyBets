#!/usr/bin/env python3
"""
Position-Specific Model Training
Builds separate models for each position with proper validation
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler
import joblib
import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from .feature_config import MLBFeatureConfig
from .temporal_validation import TemporalValidator

class PositionSpecificModelTrainer:
    """Train separate models for each position with temporal validation"""
    
    def __init__(self, features_file: str):
        self.features_file = features_file
        self.data = None
        self.models = {}
        self.scalers = {}
        self.performance_metrics = {}
        self.feature_importance = {}
        
        # Position groupings
        self.position_groups = {
            'C': ['C'],
            '1B': ['1B'],
            '2B': ['2B'],
            '3B': ['3B'],
            'SS': ['SS'],
            'OF': ['OF'],
            'P': ['P']
        }
        
        # Initialize feature configuration and temporal validator
        self.feature_config = MLBFeatureConfig()
        self.temporal_validator = TemporalValidator()
    
    def load_and_prepare_data(self) -> bool:
        """Load and prepare the features dataset"""
        try:
            print("📊 Loading dataset...")
            self.data = pd.read_csv(self.features_file)
            
            # Convert date column
            self.data['game_date'] = pd.to_datetime(self.data['game_date'])
            
            # Remove rows with NaN target
            initial_rows = len(self.data)
            self.data = self.data.dropna(subset=['fantasy_points'])
            final_rows = len(self.data)
            
            print(f"✅ Loaded {final_rows} rows ({initial_rows - final_rows} removed due to missing targets)")
            print(f"📅 Date range: {self.data['game_date'].min()} to {self.data['game_date'].max()}")
            print(f"👥 Players: {self.data['player_id'].nunique()}")
            print(f"🏟️ Positions: {sorted(self.data['position'].unique())}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def get_position_data(self, position_group: str) -> pd.DataFrame:
        """Get data for a specific position group"""
        positions = self.position_groups[position_group]
        position_data = self.data[self.data['position'].isin(positions)].copy()
        
        # Sort by player and date for temporal validation
        position_data = position_data.sort_values(['player_id', 'game_date'])
        
        return position_data
    
    def select_features(self, position_group: str, data: pd.DataFrame) -> List[str]:
        """Select appropriate features for a position using centralized config"""
        # Get features from centralized configuration
        candidate_features = self.feature_config.get_features_for_position(position_group)
        
        # Only use features that exist and have sufficient data
        available_features = []
        for feature in candidate_features:
            if feature in data.columns:
                # Require at least 70% non-null values
                non_null_pct = (1 - data[feature].isnull().sum() / len(data)) * 100
                if non_null_pct >= 70:
                    available_features.append(feature)
        
        # Validate using feature config
        validation = self.feature_config.validate_features(position_group, available_features)
        if not validation['is_valid']:
            print(f"⚠️ {position_group} features don't meet minimum requirements: {validation['coverage_percentage']:.1f}% coverage")
        
        return available_features
    
    def create_temporal_splits_validated(self, data: pd.DataFrame, 
                                        train_ratio: float = 0.8, 
                                        temporal_gap_days: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Create validated temporal train/test splits with proper gap to prevent leakage
        
        Args:
            data: Position-specific data to split
            train_ratio: Ratio of data for training
            temporal_gap_days: Number of days gap between train and test
            
        Returns:
            Tuple of (train_data, test_data)
        """
        print(f"🕐 Creating temporal splits with {temporal_gap_days}-day gap...")
        
        # Sort by date first
        data_sorted = data.sort_values(['player_id', 'game_date']).reset_index(drop=True)
        
        # Use temporal validator to create basic splits
        train_data, test_data = self.temporal_validator.create_temporal_splits(data_sorted, train_ratio)
        
        if len(train_data) == 0 or len(test_data) == 0:
            print("❌ Failed to create temporal splits")
            return pd.DataFrame(), pd.DataFrame()
        
        # Add temporal gap by removing data too close to the split point
        train_end_date = train_data['game_date'].max()
        gap_start_date = train_end_date + pd.Timedelta(days=1)
        gap_end_date = train_end_date + pd.Timedelta(days=temporal_gap_days)
        
        # Remove test data within the gap period
        test_data_filtered = test_data[test_data['game_date'] > gap_end_date].copy()
        
        # Validate the split integrity
        validation_result = self.temporal_validator.validate_temporal_integrity(
            pd.concat([train_data, test_data_filtered])
        )
        
        if not validation_result.get('chronological_order', True):
            print("⚠️ Temporal split validation failed - chronological order issue")
        
        if validation_result.get('leakage_detected', False):
            print("⚠️ Potential data leakage detected in temporal split")
        
        print(f"✅ Temporal split: {len(train_data)} train, {len(test_data_filtered)} test (gap: {temporal_gap_days} days)")
        
        return train_data, test_data_filtered
    
    def train_position_model(self, position_group: str) -> Dict:
        """Train a model for a specific position"""
        print(f"\n🎯 Training {position_group} model...")
        
        # Get position data
        position_data = self.get_position_data(position_group)
        
        if len(position_data) < 10:
            print(f"❌ Insufficient data for {position_group}: {len(position_data)} rows (minimum 10)")
            return {'error': 'Insufficient data'}
        
        print(f"📊 {position_group} data: {len(position_data)} games, {position_data['player_id'].nunique()} players")
        
        # Select features
        features = self.select_features(position_group, position_data)
        
        if len(features) < 2:
            print(f"❌ Insufficient features for {position_group}: {features}")
            return {'error': 'Insufficient features'}
        
        print(f"🎛️ Using {len(features)} features: {features[:5]}{'...' if len(features) > 5 else ''}")
        
        # Prepare feature matrix and target
        X = position_data[features].copy()
        y = position_data['fantasy_points'].copy()
        
        # Create proper temporal splits with validation
        train_data, test_data = self.create_temporal_splits_validated(position_data, 
                                                                     train_ratio=0.8, 
                                                                     temporal_gap_days=5)
        
        if len(train_data) < 5 or len(test_data) < 2:
            print(f"❌ Insufficient data after temporal validation: train={len(train_data)}, test={len(test_data)}")
            return {'error': 'Insufficient data for temporal split'}
        
        # Prepare feature matrices
        X_train = train_data[features].fillna(0)
        X_test = test_data[features].fillna(0)
        y_train = train_data['fantasy_points']
        y_test = test_data['fantasy_points']
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Predict and evaluate
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        cv_scores = {
            'mae': [mae],
            'r2': [r2], 
            'rmse': [rmse]
        }
        
        # Train final model on all position data (after validation passed)
        X_all = position_data[features].fillna(0)
        y_all = position_data['fantasy_points']
        X_all_scaled = scaler.fit_transform(X_all)
        model.fit(X_all_scaled, y_all)
        
        # Calculate feature importance
        feature_importance = dict(zip(features, model.feature_importances_))
        
        # Performance metrics
        performance = {
            'position': position_group,
            'n_samples': len(position_data),
            'n_players': position_data['player_id'].nunique(),
            'n_features': len(features),
            'features': features,
            'cv_mae_mean': np.mean(cv_scores['mae']),
            'cv_mae_std': np.std(cv_scores['mae']),
            'cv_r2_mean': np.mean(cv_scores['r2']),
            'cv_r2_std': np.std(cv_scores['r2']),
            'cv_rmse_mean': np.mean(cv_scores['rmse']),
            'cv_rmse_std': np.std(cv_scores['rmse']),
            'feature_importance': feature_importance
        }
        
        # Store model and scaler
        self.models[position_group] = model
        self.scalers[position_group] = scaler
        self.performance_metrics[position_group] = performance
        self.feature_importance[position_group] = feature_importance
        
        print(f"✅ {position_group} model trained:")
        print(f"   MAE: {performance['cv_mae_mean']:.2f} ± {performance['cv_mae_std']:.2f}")
        print(f"   R²: {performance['cv_r2_mean']:.3f} ± {performance['cv_r2_std']:.3f}")
        print(f"   RMSE: {performance['cv_rmse_mean']:.2f} ± {performance['cv_rmse_std']:.2f}")
        
        return performance
    
    def train_all_models(self) -> Dict:
        """Train models for all positions"""
        print("🚀 TRAINING POSITION-SPECIFIC MODELS")
        print("=" * 50)
        
        if not self.load_and_prepare_data():
            return {'error': 'Data loading failed'}
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_samples': len(self.data),
            'total_players': self.data['player_id'].nunique(),
            'models_trained': {},
            'overall_performance': {},
            'errors': []
        }
        
        successful_models = 0
        
        for position_group in self.position_groups.keys():
            try:
                performance = self.train_position_model(position_group)
                
                if 'error' not in performance:
                    results['models_trained'][position_group] = performance
                    successful_models += 1
                else:
                    results['errors'].append(f"{position_group}: {performance['error']}")
                    
            except Exception as e:
                error_msg = f"{position_group}: {str(e)}"
                print(f"❌ Error training {position_group}: {str(e)}")
                results['errors'].append(error_msg)
        
        # Calculate overall performance
        if successful_models > 0:
            all_mae = [perf['cv_mae_mean'] for perf in results['models_trained'].values()]
            all_r2 = [perf['cv_r2_mean'] for perf in results['models_trained'].values()]
            all_rmse = [perf['cv_rmse_mean'] for perf in results['models_trained'].values()]
            
            results['overall_performance'] = {
                'models_successful': successful_models,
                'models_total': len(self.position_groups),
                'avg_mae': np.mean(all_mae),
                'avg_r2': np.mean(all_r2),
                'avg_rmse': np.mean(all_rmse),
                'mae_range': [min(all_mae), max(all_mae)],
                'r2_range': [min(all_r2), max(all_r2)]
            }
        
        print(f"\n🎉 MODEL TRAINING COMPLETE!")
        print(f"✅ Successful models: {successful_models}/{len(self.position_groups)}")
        
        if successful_models > 0:
            overall = results['overall_performance']
            print(f"📊 Overall Performance:")
            print(f"   Average MAE: {overall['avg_mae']:.2f}")
            print(f"   Average R²: {overall['avg_r2']:.3f}")
            print(f"   MAE Range: {overall['mae_range'][0]:.2f} - {overall['mae_range'][1]:.2f}")
            print(f"   R² Range: {overall['r2_range'][0]:.3f} - {overall['r2_range'][1]:.3f}")
        
        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"   • {error}")
        
        return results
    
    def save_models(self) -> str:
        """Save all trained models and metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create models directory
        models_dir = f"models_{timestamp}"
        os.makedirs(models_dir, exist_ok=True)
        
        # Save individual models
        for position, model in self.models.items():
            model_file = os.path.join(models_dir, f"mlb_{position.lower()}_model.pkl")
            joblib.dump(model, model_file)
            
            scaler_file = os.path.join(models_dir, f"mlb_{position.lower()}_scaler.pkl")
            joblib.dump(self.scalers[position], scaler_file)
        
        # Save performance metrics
        performance_file = os.path.join(models_dir, "model_performance.json")
        with open(performance_file, 'w') as f:
            json.dump(self.performance_metrics, f, indent=2, default=str)
        
        # Save feature importance
        importance_file = os.path.join(models_dir, "feature_importance.json")
        with open(importance_file, 'w') as f:
            json.dump(self.feature_importance, f, indent=2, default=str)
        
        print(f"💾 Models saved to: {models_dir}")
        return models_dir
    
    def predict_fantasy_points(self, player_data: Dict, position: str) -> Tuple[float, float]:
        """Make a prediction for a single player"""
        if position not in self.models:
            raise ValueError(f"No model available for position {position}")
        
        model = self.models[position]
        scaler = self.scalers[position]
        
        # Get features for this position
        features = self.select_features(position, self.data)
        
        # Extract feature values
        feature_values = []
        for feature in features:
            value = player_data.get(feature, 0)
            feature_values.append(value)
        
        # Scale and predict
        X = np.array(feature_values).reshape(1, -1)
        X_scaled = scaler.transform(X)
        
        prediction = model.predict(X_scaled)[0]
        
        # Calculate confidence based on model performance
        performance = self.performance_metrics[position]
        confidence = max(0, min(1, 1 - (performance['cv_mae_mean'] / 20)))  # Rough confidence measure
        
        return prediction, confidence

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python model_training.py <features_file.csv>")
        sys.exit(1)
    
    features_file = sys.argv[1]
    
    if not os.path.exists(features_file):
        print(f"❌ Features file not found: {features_file}")
        sys.exit(1)
    
    trainer = PositionSpecificModelTrainer(features_file)
    results = trainer.train_all_models()
    
    if 'error' not in results:
        models_dir = trainer.save_models()
        print(f"\n✅ Training complete! Models saved to: {models_dir}")
    else:
        print(f"\n❌ Training failed: {results['error']}") 