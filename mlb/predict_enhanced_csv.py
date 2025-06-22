#!/usr/bin/env python3
"""
Enhanced MLB Predictions from CSV
Predicts both fantasy points and individual player statistics from CSV data
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

class EnhancedMLBPredictor:
    """Enhanced predictor for both fantasy points and individual stats"""
    
    def __init__(self, models_dir="models", stat_models_dir=None):
        self.models_dir = models_dir
        self.stat_models_dir = stat_models_dir or self._find_latest_stat_models()
        
        # Fantasy point models
        self.fantasy_models = {}
        self.fantasy_scalers = {}
        self.fantasy_performance = {}
        
        # Individual stat models
        self.stat_models = {}
        self.stat_scalers = {}
        self.stat_performance = {}
        
        self.load_models()
    
    def _find_latest_stat_models(self):
        """Find the latest individual stat models directory"""
        try:
            dirs = [d for d in os.listdir('.') if d.startswith('individual_stat_models_')]
            if dirs:
                latest = max(dirs, key=lambda x: x.split('_')[-2] + x.split('_')[-1])
                return latest
        except:
            pass
        return None
    
    def _find_latest_rate_models(self):
        """Find the latest rate-based models directory"""
        try:
            dirs = [d for d in os.listdir('.') if d.startswith('rate_based_batter_models_')]
            if dirs:
                latest = max(dirs, key=lambda x: x.split('_')[-2] + x.split('_')[-1])
                return latest
        except:
            pass
        return None
    
    def load_models(self):
        """Load both fantasy and stat models"""
        # Load fantasy point models
        try:
            perf_file = os.path.join(self.models_dir, 'model_performance.json')
            with open(perf_file, 'r') as f:
                self.fantasy_performance = json.load(f)
            
            positions = ['C', '1B', '2B', '3B', 'SS', 'OF', 'P']
            for position in positions:
                try:
                    model_file = os.path.join(self.models_dir, f'mlb_{position.lower()}_model.pkl')
                    scaler_file = os.path.join(self.models_dir, f'mlb_{position.lower()}_scaler.pkl')
                    
                    if os.path.exists(model_file) and os.path.exists(scaler_file):
                        self.fantasy_models[position] = joblib.load(model_file)
                        self.fantasy_scalers[position] = joblib.load(scaler_file)
                        
                except Exception as e:
                    print(f"⚠️ Failed to load fantasy model for {position}: {e}")
            
            print(f"✅ Loaded {len(self.fantasy_models)} fantasy point models")
            
        except Exception as e:
            print(f"❌ Failed to load fantasy models: {e}")
        
        # Load individual stat models
        if self.stat_models_dir and os.path.exists(self.stat_models_dir):
            try:
                perf_file = os.path.join(self.stat_models_dir, 'individual_stat_performance.json')
                with open(perf_file, 'r') as f:
                    self.stat_performance = json.load(f)
                
                for model_name in self.stat_performance.keys():
                    try:
                        model_file = os.path.join(self.stat_models_dir, f'{model_name}_model.pkl')
                        scaler_file = os.path.join(self.stat_models_dir, f'{model_name}_scaler.pkl')
                        
                        if os.path.exists(model_file) and os.path.exists(scaler_file):
                            self.stat_models[model_name] = joblib.load(model_file)
                            self.stat_scalers[model_name] = joblib.load(scaler_file)
                            
                    except Exception as e:
                        print(f"⚠️ Failed to load stat model {model_name}: {e}")
                
                print(f"✅ Loaded {len(self.stat_models)} individual stat models")
                
            except Exception as e:
                print(f"❌ Failed to load stat models: {e}")
        else:
            print("⚠️ No individual stat models found - will only predict fantasy points")
    
    def validate_csv_format(self, df):
        """Validate CSV has required columns"""
        required_cols = [
            'player_name',
            'avg_fantasy_points_L15',
            'avg_fantasy_points_L10', 
            'avg_fantasy_points_L5',
            'games_since_last_good_game',
            'trend_last_5_games',
            'consistency_score'
        ]
        
        missing_required = [col for col in required_cols if col not in df.columns]
        
        if missing_required:
            print(f"❌ Missing required columns: {missing_required}")
            print(f"📋 Required columns: {required_cols}")
            return False
        
        print(f"✅ CSV format validation passed")
        print(f"📊 Input data: {len(df)} players")
        return True
    
    def predict_from_csv(self, csv_file, output_file=None):
        """Run enhanced predictions for all players in CSV file"""
        try:
            # Load CSV data
            print(f"📊 Loading data from: {csv_file}")
            df = pd.read_csv(csv_file)
            
            # Validate format
            if not self.validate_csv_format(df):
                return None
            
            # Add default position if missing
            if 'position' not in df.columns:
                df['position'] = 'OF'
                print("📋 No position column found, defaulting all players to OF")
            
            print(f"🎯 Processing {len(df)} players for enhanced predictions...")
            
            # Prepare features
            feature_cols = [
                'avg_fantasy_points_L15',
                'avg_fantasy_points_L10', 
                'avg_fantasy_points_L5',
                'games_since_last_good_game',
                'trend_last_5_games',
                'consistency_score'
            ]
            
            # Initialize results
            results = []
            
            # Predict for each player
            for idx, row in df.iterrows():
                try:
                    player_name = row['player_name']
                    position = row['position']
                    
                    # Prepare features
                    features = row[feature_cols].values.reshape(1, -1)
                    features = np.nan_to_num(features, nan=0.0)
                    
                    # Predict fantasy points
                    fantasy_result = self._predict_fantasy_points(features, position)
                    
                    # Predict individual stats
                    individual_stats = self._predict_individual_stats(features, position)
                    
                    # Create result record
                    result_record = {
                        'player_name': player_name,
                        'position': position,
                        'predicted_fantasy_points': fantasy_result['predicted'],
                        'fantasy_confidence': fantasy_result['confidence'],
                        'fantasy_model_r2': fantasy_result.get('model_r2', 0),
                        'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Add individual stat predictions
                    for stat_name, stat_data in individual_stats.items():
                        result_record[stat_name] = stat_data.get('value', 0)
                        result_record[f'{stat_name}_confidence'] = stat_data.get('confidence', 0)
                    
                    results.append(result_record)
                    
                    print(f"✅ {player_name} ({position}): {fantasy_result['predicted']:.2f} fantasy points")
                    
                except Exception as e:
                    print(f"❌ Failed to predict for {row.get('player_name', 'Unknown')}: {e}")
                    continue
            
            # Create results DataFrame
            results_df = pd.DataFrame(results)
            
            if len(results_df) == 0:
                print("❌ No successful predictions generated")
                return None
            
            # Save results
            if output_file is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f'enhanced_predictions_{timestamp}.csv'
            
            results_df.to_csv(output_file, index=False)
            
            # Summary
            print(f"\n📊 ENHANCED PREDICTION SUMMARY:")
            print(f"{'='*60}")
            print(f"📋 Total players processed: {len(df)}")
            print(f"✅ Successful predictions: {len(results_df)}")
            print(f"📁 Output file: {output_file}")
            
            # Performance by position
            print(f"\n📈 Predictions by position:")
            for pos in results_df['position'].unique():
                pos_data = results_df[results_df['position'] == pos]
                avg_fantasy = pos_data['predicted_fantasy_points'].mean()
                print(f"  {pos}: {len(pos_data)} players, avg {avg_fantasy:.2f} fantasy points")
            
            # Show sample individual stats
            if len(self.stat_models) > 0:
                print(f"\n📈 Sample individual stat predictions:")
                sample_player = results_df.iloc[0]
                player_type = 'pitcher' if sample_player['position'] == 'P' else 'batter'
                
                if player_type == 'batter':
                    stat_cols = ['predicted_hits', 'predicted_home_runs', 'predicted_walks', 'predicted_strikeouts']
                else:
                    stat_cols = ['predicted_innings_pitched', 'predicted_strikeouts', 'predicted_hits_allowed']
                
                for stat_col in stat_cols:
                    if stat_col in sample_player:
                        print(f"  {sample_player['player_name']} {stat_col}: {sample_player[stat_col]}")
            
            print(f"\n✅ Enhanced predictions saved to: {output_file}")
            return results_df
            
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
            return None
    
    def _predict_fantasy_points(self, features, position):
        """Predict fantasy points"""
        try:
            # Use OF model if specific position model not available
            model_position = position if position in self.fantasy_models else 'OF'
            
            if model_position not in self.fantasy_models:
                return {'predicted': 0, 'confidence': 0, 'error': 'No model available'}
            
            # Scale and predict
            features_scaled = self.fantasy_scalers[model_position].transform(features)
            prediction = self.fantasy_models[model_position].predict(features_scaled)[0]
            
            # Calculate confidence
            model_r2 = self.fantasy_performance[model_position]['r2']
            confidence = min(0.9, max(0.3, model_r2))
            
            return {
                'predicted': round(prediction, 2),
                'confidence': round(confidence, 2),
                'model_r2': round(model_r2, 3)
            }
            
        except Exception as e:
            return {'predicted': 0, 'confidence': 0, 'error': str(e)}
    
    def _predict_individual_stats(self, features, position):
        """Predict individual stats"""
        predictions = {}
        
        if len(self.stat_models) == 0:
            return predictions
        
        # Determine player type
        player_type = 'pitcher' if position == 'P' else 'batter'
        
        # Define stats to predict based on player type
        if player_type == 'batter':
            stat_names = ['hits', 'doubles', 'triples', 'home_runs', 'walks', 
                         'strikeouts', 'runs', 'rbis', 'stolen_bases']
        else:
            stat_names = ['innings_pitched', 'strikeouts', 'hits_allowed', 
                         'walks_allowed', 'home_runs_allowed', 'earned_runs']
        
        # Predict each stat
        for stat_name in stat_names:
            model_key = f"{player_type}_{stat_name}"
            
            if model_key in self.stat_models:
                try:
                    # Scale and predict
                    features_scaled = self.stat_scalers[model_key].transform(features)
                    prediction = self.stat_models[model_key].predict(features_scaled)[0]
                    
                    # Ensure non-negative for count stats
                    if stat_name != 'innings_pitched':
                        prediction = max(0, prediction)
                    
                    # Round appropriately
                    if stat_name == 'innings_pitched':
                        prediction = round(prediction, 1)
                    else:
                        prediction = round(prediction)
                    
                    # Get model performance
                    model_r2 = self.stat_performance[model_key]['r2']
                    confidence = min(0.9, max(0.1, model_r2))
                    
                    predictions[f'predicted_{stat_name}'] = {
                        'value': prediction,
                        'confidence': round(confidence, 2)
                    }
                    
                except Exception as e:
                    predictions[f'predicted_{stat_name}'] = {
                        'value': 0,
                        'confidence': 0
                    }
            else:
                predictions[f'predicted_{stat_name}'] = {
                    'value': 0,
                    'confidence': 0
                }
        
        return predictions

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Enhanced MLB Predictions from CSV (Fantasy Points + Individual Stats)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CSV Format Requirements:
  Required columns:
    - player_name: Player name
    - avg_fantasy_points_L15: Average fantasy points last 15 games
    - avg_fantasy_points_L10: Average fantasy points last 10 games  
    - avg_fantasy_points_L5: Average fantasy points last 5 games
    - games_since_last_good_game: Games since >10 fantasy points
    - trend_last_5_games: Trend in last 5 games (positive = improving)
    - consistency_score: Performance consistency (0-1, higher = more consistent)
  
  Optional columns:
    - position: Player position (C, 1B, 2B, 3B, SS, OF, P) - defaults to OF

Output includes:
  - Fantasy points prediction with confidence
  - Individual stat predictions (hits, HRs, strikeouts, etc.)
  - Confidence scores for each prediction

Examples:
  python predict_enhanced_csv.py players.csv
  python predict_enhanced_csv.py players.csv --output enhanced_results.csv
  python predict_enhanced_csv.py players.csv --models custom_models/ --stat-models custom_stats/
        """
    )
    
    parser.add_argument('csv_file', help='Input CSV file with player data')
    parser.add_argument('--output', '-o', help='Output CSV file (auto-generated if not specified)')
    parser.add_argument('--models', '-m', default='models', help='Fantasy models directory (default: models)')
    parser.add_argument('--stat-models', '-s', help='Individual stat models directory (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.csv_file):
        print(f"❌ Input file not found: {args.csv_file}")
        sys.exit(1)
    
    # Initialize predictor
    print("🚀 ENHANCED MLB PREDICTION FROM CSV")
    print("=" * 60)
    print(f"📊 Input file: {args.csv_file}")
    print(f"🎯 Fantasy models: {args.models}")
    print(f"📈 Stat models: {args.stat_models or 'auto-detect'}")
    
    predictor = EnhancedMLBPredictor(models_dir=args.models, stat_models_dir=args.stat_models)
    
    # Run predictions
    results = predictor.predict_from_csv(args.csv_file, args.output)
    
    if results is not None:
        print(f"\n🎉 Enhanced predictions completed successfully!")
    else:
        print(f"\n❌ Enhanced predictions failed")
        sys.exit(1)

if __name__ == "__main__":
    main()