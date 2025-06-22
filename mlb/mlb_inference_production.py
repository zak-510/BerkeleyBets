#!/usr/bin/env python3
"""
MLB Production Inference System
Production-ready interface for MLB fantasy predictions with comprehensive error handling
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from src.data_collection import MLBDataCollector
from src.position_mapping import PositionMapper
from src.temporal_validation import TemporalValidator


class MLBProductionInference:
    """Production-ready MLB fantasy prediction system"""
    
    def __init__(self, models_dir: str = None, data_dir: str = "mlb_data"):
        """
        Initialize production inference system
        
        Args:
            models_dir: Directory containing trained models (auto-detected if None)
            data_dir: Directory for data caching
        """
        self.models_dir = models_dir or self._find_latest_models_dir()
        self.data_dir = data_dir
        self.models = {}
        self.scalers = {}
        self.performance_metrics = {}
        self.feature_configs = {}
        
        # Initialize components
        self.data_collector = MLBDataCollector(cache_dir=data_dir)
        self.position_mapper = PositionMapper(cache_dir=data_dir)
        self.temporal_validator = TemporalValidator()
        
        # Status tracking
        self.system_status = {
            'models_loaded': False,
            'last_error': None,
            'initialization_time': datetime.now().isoformat(),
            'total_predictions': 0,
            'successful_predictions': 0
        }
        
        # Load models and validate system
        self._initialize_system()
    
    def _find_latest_models_dir(self, base_path: str = ".") -> str:
        """Find the most recent models directory"""
        pattern = re.compile(r"models_\d{8}_\d{6}")
        try:
            dirs = [d for d in os.listdir(base_path) if pattern.match(d)]
            if dirs:
                # Sort by timestamp in directory name
                latest = max(dirs, key=lambda x: x.split('_')[1] + x.split('_')[2])
                print(f"🔍 Auto-detected latest models directory: {latest}")
                return latest
            else:
                print("⚠️ No timestamped model directories found, using 'models'")
                return "models"
        except Exception as e:
            print(f"❌ Error finding models directory: {e}")
            return "models"
    
    def _initialize_system(self) -> bool:
        """Initialize and validate the production system"""
        try:
            print("🚀 Initializing MLB Production Inference System")
            print("=" * 60)
            
            # Load models
            success = self._load_models()
            if not success:
                self.system_status['last_error'] = "Failed to load models"
                return False
            
            # Validate system readiness
            validation_result = self._validate_system()
            if not validation_result['is_ready']:
                self.system_status['last_error'] = f"System validation failed: {validation_result['issues']}"
                return False
            
            self.system_status['models_loaded'] = True
            print("✅ Production system initialized successfully")
            return True
            
        except Exception as e:
            error_msg = f"System initialization failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.system_status['last_error'] = error_msg
            return False
    
    def _load_models(self) -> bool:
        """Load all trained models and metadata"""
        if not os.path.exists(self.models_dir):
            print(f"❌ Models directory not found: {self.models_dir}")
            return False
        
        try:
            # Load performance metrics
            metrics_file = os.path.join(self.models_dir, "model_performance.json")
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r') as f:
                    self.performance_metrics = json.load(f)
                print(f"📊 Loaded performance metrics for {len(self.performance_metrics)} positions")
            
            # Load models and scalers
            loaded_count = 0
            positions = ['C', '1B', '2B', '3B', 'SS', 'OF', 'P']
            
            for position in positions:
                model_file = os.path.join(self.models_dir, f"mlb_{position.lower()}_model.pkl")
                scaler_file = os.path.join(self.models_dir, f"mlb_{position.lower()}_scaler.pkl")
                
                if os.path.exists(model_file) and os.path.exists(scaler_file):
                    try:
                        self.models[position] = joblib.load(model_file)
                        self.scalers[position] = joblib.load(scaler_file)
                        
                        # Store feature configuration
                        perf = self.performance_metrics.get(position, {})
                        self.feature_configs[position] = perf.get('features', [])
                        
                        # Handle different R² field names
                        r2 = perf.get('cv_r2_mean', perf.get('r2', 'N/A'))
                        if isinstance(r2, (int, float)):
                            r2_str = f"{r2:.3f}"
                            # Add warning for terrible performance
                            if r2 < 0:
                                r2_str += " ⚠️ POOR"
                            elif r2 < 0.2:
                                r2_str += " ⚠️ LOW"
                        else:
                            r2_str = str(r2)
                        print(f"✅ Loaded {position} model (R²={r2_str})")
                        loaded_count += 1
                        
                    except Exception as e:
                        print(f"⚠️ Error loading {position} model: {e}")
            
            print(f"📈 Successfully loaded {loaded_count}/{len(positions)} models")
            return loaded_count > 0
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            return False
    
    def _validate_system(self) -> Dict:
        """Validate system readiness for production"""
        validation = {
            'is_ready': True,
            'issues': [],
            'warnings': [],
            'model_count': len(self.models),
            'positions_available': list(self.models.keys())
        }
        
        # Check minimum model requirements
        if len(self.models) < 2:
            validation['is_ready'] = False
            validation['issues'].append(f"Insufficient models loaded: {len(self.models)} (minimum 2)")
        
        # Check data collection system
        try:
            cache_stats = self.data_collector.get_cache_stats()
            validation['cache_stats'] = cache_stats
        except Exception as e:
            validation['warnings'].append(f"Cache validation failed: {e}")
        
        # Validate feature configurations
        for position, features in self.feature_configs.items():
            if not features:
                validation['warnings'].append(f"No features configured for {position}")
        
        return validation
    
    def predict_player(self, player_name: str, date_range: Tuple[str, str] = None, 
                      position_hint: str = None) -> Dict:
        """
        Predict fantasy points for a specific player
        
        Args:
            player_name: Full player name (e.g., "Aaron Judge")
            date_range: Tuple of (start_date, end_date) for data collection
            position_hint: Expected position to help with lookup
            
        Returns:
            Dictionary with prediction results and metadata
        """
        start_time = datetime.now()
        self.system_status['total_predictions'] += 1
        
        prediction_result = {
            'player_name': player_name,
            'success': False,
            'predictions': [],
            'metadata': {
                'prediction_time': start_time.isoformat(),
                'processing_time_ms': None,
                'position': None,
                'model_performance': None,
                'data_range': date_range,
                'errors': []
            }
        }
        
        try:
            print(f"\n🎯 PRODUCTION PREDICTION: {player_name}")
            print("=" * 50)
            
            # Set default date range if not provided
            if date_range is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
                date_range = (start_date, end_date)
            
            prediction_result['metadata']['data_range'] = date_range
            
            # Parse player name
            name_parts = player_name.strip().split()
            if len(name_parts) < 2:
                raise ValueError(f"Invalid player name format: '{player_name}' (expected 'First Last')")
            
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
            
            # Get player ID
            print(f"🔍 Looking up player ID...")
            player_id = self.data_collector.get_player_id(last_name, first_name)
            if player_id is None:
                raise ValueError(f"Player not found: {player_name}")
            
            prediction_result['metadata']['player_id'] = player_id
            
            # Determine position
            position = self.position_mapper.get_player_position(player_id, player_name, position_hint)
            if position is None:
                raise ValueError(f"Could not determine position for {player_name}")
            
            prediction_result['metadata']['position'] = position
            print(f"🏷️ Position: {position}")
            
            # Check if we have a model for this position
            if position not in self.models:
                available_positions = list(self.models.keys())
                raise ValueError(f"No model available for position {position}. Available: {available_positions}")
            
            # Collect player data
            print(f"📊 Collecting game data...")
            player_data = self._collect_player_data_safe(player_id, date_range, position)
            
            if player_data is None or len(player_data) == 0:
                raise ValueError(f"No game data found for {player_name} in date range {date_range}")
            
            # Generate historical features
            print(f"🔧 Generating features...")
            featured_data = self.temporal_validator.generate_historical_features(player_data)
            
            if len(featured_data) == 0:
                raise ValueError("Failed to generate historical features")
            
            # Make predictions
            predictions = self._make_predictions_safe(featured_data, position)
            
            if not predictions:
                raise ValueError("Failed to generate predictions")
            
            prediction_result['predictions'] = predictions
            prediction_result['success'] = True
            prediction_result['metadata']['model_performance'] = self.performance_metrics.get(position, {})
            
            self.system_status['successful_predictions'] += 1
            
            # Display results
            self._display_prediction_results(prediction_result)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Prediction failed: {error_msg}")
            prediction_result['metadata']['errors'].append(error_msg)
        
        finally:
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            prediction_result['metadata']['processing_time_ms'] = round(processing_time, 2)
        
        return prediction_result
    
    def _collect_player_data_safe(self, player_id: int, date_range: Tuple[str, str], position: str) -> Optional[pd.DataFrame]:
        """Safely collect player data with proper error handling"""
        try:
            # Try both batter and pitcher data collection
            for player_type in ['b', 'p']:
                try:
                    game_data = self.data_collector.get_game_data(
                        player_id, date_range[0], date_range[1], player_type
                    )
                    
                    if game_data and len(game_data) > 0:
                        df = pd.DataFrame(game_data)
                        print(f"✅ Collected {len(df)} games for player {player_id}")
                        return df
                        
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Data collection error: {e}")
            return None
    
    def _make_predictions_safe(self, featured_data: pd.DataFrame, position: str) -> List[Dict]:
        """Safely make predictions with comprehensive error handling"""
        try:
            model = self.models[position]
            scaler = self.scalers[position]
            features = self.feature_configs[position]
            
            if not features:
                raise ValueError(f"No feature configuration for position {position}")
            
            # Prepare feature matrix
            available_features = [f for f in features if f in featured_data.columns]
            if len(available_features) == 0:
                raise ValueError(f"No features available for {position}")
            
            X = featured_data[available_features].fillna(0)
            
            # Scale features
            X_scaled = scaler.transform(X)
            
            # Make predictions
            predictions_raw = model.predict(X_scaled)
            
            # Prepare results
            predictions = []
            for i, (idx, row) in enumerate(featured_data.iterrows()):
                # Handle datetime formatting safely
                game_date = row['game_date']
                if isinstance(game_date, str):
                    game_date_str = game_date
                else:
                    try:
                        game_date_str = pd.to_datetime(game_date).strftime('%Y-%m-%d')
                    except:
                        game_date_str = str(game_date)
                
                pred = {
                    'game_date': game_date_str,
                    'predicted_fantasy_points': round(float(predictions_raw[i]), 2),
                    'actual_fantasy_points': float(row.get('fantasy_points', 0)) if pd.notna(row.get('fantasy_points')) else None,
                    'confidence_score': self._calculate_confidence(position),
                    'features_used': len(available_features)
                }
                predictions.append(pred)
            
            return predictions
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return []
    
    def _calculate_confidence(self, position: str) -> float:
        """Calculate prediction confidence based on model performance"""
        perf = self.performance_metrics.get(position, {})
        r2 = perf.get('cv_r2_mean', perf.get('r2', 0))
        
        # Handle negative R² values (worse than random)
        if r2 < -0.5:
            return 0.1  # Very low confidence - model is terrible
        elif r2 < 0:
            return 0.2  # Low confidence - worse than baseline
        elif r2 < 0.2:
            return 0.4  # Fair confidence - barely better than baseline
        elif r2 < 0.5:
            return 0.6  # Medium confidence
        elif r2 < 0.7:
            return 0.8  # Good confidence
        else:
            return 0.9  # High confidence
    
    def _display_prediction_results(self, result: Dict):
        """Display prediction results in a user-friendly format"""
        if not result['success']:
            return
        
        predictions = result['predictions']
        metadata = result['metadata']
        
        print(f"\n📈 PREDICTION RESULTS:")
        print("-" * 40)
        
        for pred in predictions:
            actual_str = f" (Actual: {pred['actual_fantasy_points']:.1f})" if pred['actual_fantasy_points'] is not None else ""
            confidence_str = f"{pred['confidence_score']:.1f}"
            print(f"  {pred['game_date']}: {pred['predicted_fantasy_points']:.1f} points{actual_str} [Confidence: {confidence_str}]")
        
        if predictions:
            avg_prediction = np.mean([p['predicted_fantasy_points'] for p in predictions])
            print(f"\n📊 Average Predicted Points: {avg_prediction:.1f}")
        
        print(f"⏱️ Processing Time: {metadata['processing_time_ms']:.0f}ms")
        print(f"🎯 Position: {metadata['position']}")
        
        # Show model performance
        perf = metadata.get('model_performance', {})
        if perf:
            r2 = perf.get('cv_r2_mean', 'N/A')
            mae = perf.get('cv_mae_mean', 'N/A')
            r2_str = f"{r2:.3f}" if isinstance(r2, (int, float)) else str(r2)
            mae_str = f"{mae:.2f}" if isinstance(mae, (int, float)) else str(mae)
            print(f"🏆 Model Performance: R²={r2_str}, MAE={mae_str}")
    
    def batch_predict(self, player_list: List[str], date_range: Tuple[str, str] = None) -> Dict:
        """
        Make predictions for multiple players
        
        Args:
            player_list: List of player names
            date_range: Date range for data collection
            
        Returns:
            Dictionary with batch results
        """
        print(f"\n🎯 BATCH PRODUCTION PREDICTIONS: {len(player_list)} players")
        print("=" * 60)
        
        batch_result = {
            'total_players': len(player_list),
            'successful_predictions': 0,
            'failed_predictions': 0,
            'results': {},
            'summary': {},
            'processing_time_ms': 0
        }
        
        start_time = datetime.now()
        
        for i, player_name in enumerate(player_list, 1):
            print(f"\n[{i}/{len(player_list)}] Processing {player_name}...")
            
            result = self.predict_player(player_name, date_range)
            batch_result['results'][player_name] = result
            
            if result['success']:
                batch_result['successful_predictions'] += 1
            else:
                batch_result['failed_predictions'] += 1
        
        # Calculate total processing time
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        batch_result['processing_time_ms'] = round(total_time, 2)
        
        # Generate summary
        success_rate = batch_result['successful_predictions'] / len(player_list) * 100
        batch_result['summary'] = {
            'success_rate': round(success_rate, 1),
            'avg_processing_time_per_player': round(total_time / len(player_list), 2),
            'total_processing_time': round(total_time / 1000, 2)
        }
        
        print(f"\n📊 BATCH SUMMARY:")
        print(f"✅ Successful: {batch_result['successful_predictions']}/{len(player_list)} ({success_rate:.1f}%)")
        print(f"❌ Failed: {batch_result['failed_predictions']}/{len(player_list)}")
        print(f"⏱️ Total Time: {batch_result['summary']['total_processing_time']:.1f}s")
        
        return batch_result
    
    def get_system_status(self) -> Dict:
        """Get current system status and health metrics"""
        return {
            **self.system_status,
            'models_loaded': len(self.models),
            'available_positions': list(self.models.keys()),
            'success_rate': (self.system_status['successful_predictions'] / 
                           max(1, self.system_status['total_predictions']) * 100),
            'models_directory': self.models_dir,
            'cache_directory': self.data_dir
        }
    
    def validate_production_readiness(self) -> Dict:
        """Comprehensive production readiness check"""
        validation = {
            'is_production_ready': True,
            'checks': {},
            'warnings': [],
            'critical_issues': []
        }
        
        # Check model availability
        validation['checks']['models_loaded'] = len(self.models) > 0
        validation['checks']['minimum_positions'] = len(self.models) >= 3
        
        # Check system components
        validation['checks']['data_collector_ready'] = self.data_collector is not None
        validation['checks']['temporal_validator_ready'] = self.temporal_validator is not None
        
        # Check performance metrics
        if self.performance_metrics:
            avg_r2 = np.mean([p.get('cv_r2_mean', 0) for p in self.performance_metrics.values() 
                             if isinstance(p.get('cv_r2_mean'), (int, float))])
            validation['checks']['acceptable_performance'] = avg_r2 > 0.2
        else:
            validation['checks']['acceptable_performance'] = False
            validation['warnings'].append("No performance metrics available")
        
        # Determine production readiness
        critical_checks = ['models_loaded', 'data_collector_ready', 'temporal_validator_ready']
        for check in critical_checks:
            if not validation['checks'].get(check, False):
                validation['is_production_ready'] = False
                validation['critical_issues'].append(f"Failed check: {check}")
        
        return validation


def main():
    """Main function for testing the production system"""
    print("⚾ MLB PRODUCTION INFERENCE SYSTEM TEST")
    print("=" * 50)
    
    # Initialize system
    production_system = MLBProductionInference()
    
    # Check system status
    status = production_system.get_system_status()
    print(f"\n📊 System Status:")
    print(f"Models loaded: {status['models_loaded']}")
    print(f"Available positions: {status['available_positions']}")
    print(f"Success rate: {status['success_rate']:.1f}%")
    
    # Validate production readiness
    readiness = production_system.validate_production_readiness()
    print(f"\n🚀 Production Ready: {readiness['is_production_ready']}")
    
    if readiness['critical_issues']:
        print("❌ Critical Issues:")
        for issue in readiness['critical_issues']:
            print(f"  • {issue}")
    
    # Test prediction if system is ready
    if readiness['is_production_ready']:
        print("\n🧪 Testing prediction system...")
        test_result = production_system.predict_player("Aaron Judge")
        
        if test_result['success']:
            print("✅ Test prediction successful!")
        else:
            print("❌ Test prediction failed")


if __name__ == "__main__":
    main()