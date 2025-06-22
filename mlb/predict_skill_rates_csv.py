#!/usr/bin/env python3
"""
MLB Skill Rate Prediction from CSV
Predicts underlying player skill rates (BA, OBP, SLG, etc.) rather than per-game stats
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SkillRatePredictor:
    """Predict underlying player skill rates from CSV data"""
    
    def __init__(self, fantasy_models_dir="models", rate_models_dir=None, stat_models_dir=None):
        self.fantasy_models_dir = fantasy_models_dir
        self.rate_models_dir = rate_models_dir or self._find_latest_rate_models()
        self.stat_models_dir = stat_models_dir or self._find_latest_stat_models()
        
        # Models
        self.fantasy_models = {}
        self.fantasy_scalers = {}
        self.fantasy_performance = {}
        
        self.rate_models = {}
        self.rate_scalers = {}
        self.rate_performance = {}
        
        self.pitcher_stat_models = {}
        self.pitcher_stat_scalers = {}
        self.pitcher_stat_performance = {}
        
        self.load_models()
    
    def _find_latest_rate_models(self):
        """Find latest rate-based models directory"""
        try:
            dirs = [d for d in os.listdir('.') if d.startswith('rate_based_batter_models_')]
            if dirs:
                return max(dirs, key=lambda x: x.split('_')[-2] + x.split('_')[-1])
        except:
            pass
        return None
    
    def _find_latest_stat_models(self):
        """Find latest individual stat models directory"""
        try:
            dirs = [d for d in os.listdir('.') if d.startswith('individual_stat_models_')]
            if dirs:
                return max(dirs, key=lambda x: x.split('_')[-2] + x.split('_')[-1])
        except:
            pass
        return None
    
    def load_models(self):
        """Load all model types"""
        # Load fantasy models
        try:
            perf_file = os.path.join(self.fantasy_models_dir, 'model_performance.json')
            with open(perf_file, 'r') as f:
                self.fantasy_performance = json.load(f)
            
            for position in ['C', '1B', '2B', '3B', 'SS', 'OF', 'P']:
                try:
                    model_file = os.path.join(self.fantasy_models_dir, f'mlb_{position.lower()}_model.pkl')
                    scaler_file = os.path.join(self.fantasy_models_dir, f'mlb_{position.lower()}_scaler.pkl')
                    
                    if os.path.exists(model_file) and os.path.exists(scaler_file):
                        self.fantasy_models[position] = joblib.load(model_file)
                        self.fantasy_scalers[position] = joblib.load(scaler_file)
                except Exception as e:
                    print(f"⚠️ Failed to load fantasy model for {position}: {e}")
            
            print(f"✅ Loaded {len(self.fantasy_models)} fantasy models")
            
        except Exception as e:
            print(f"❌ Failed to load fantasy models: {e}")
        
        # Load rate models for batters
        if self.rate_models_dir and os.path.exists(self.rate_models_dir):
            try:
                perf_file = os.path.join(self.rate_models_dir, 'rate_based_performance.json')
                with open(perf_file, 'r') as f:
                    self.rate_performance = json.load(f)
                
                for model_name in self.rate_performance.keys():
                    try:
                        model_file = os.path.join(self.rate_models_dir, f"{model_name}_model.pkl")
                        scaler_file = os.path.join(self.rate_models_dir, f"{model_name}_scaler.pkl")
                        
                        if os.path.exists(model_file) and os.path.exists(scaler_file):
                            self.rate_models[model_name] = joblib.load(model_file)
                            self.rate_scalers[model_name] = joblib.load(scaler_file)
                    except Exception as e:
                        print(f"⚠️ Failed to load rate model {model_name}: {e}")
                
                print(f"✅ Loaded {len(self.rate_models)} rate-based batter models")
                
            except Exception as e:
                print(f"❌ Failed to load rate models: {e}")
        
        # Load pitcher stat models
        if self.stat_models_dir and os.path.exists(self.stat_models_dir):
            try:
                perf_file = os.path.join(self.stat_models_dir, 'individual_stat_performance.json')
                with open(perf_file, 'r') as f:
                    all_performance = json.load(f)
                
                # Only load pitcher models
                for model_name, perf in all_performance.items():
                    if model_name.startswith('pitcher_'):
                        try:
                            model_file = os.path.join(self.stat_models_dir, f'{model_name}_model.pkl')
                            scaler_file = os.path.join(self.stat_models_dir, f'{model_name}_scaler.pkl')
                            
                            if os.path.exists(model_file) and os.path.exists(scaler_file):
                                self.pitcher_stat_models[model_name] = joblib.load(model_file)
                                self.pitcher_stat_scalers[model_name] = joblib.load(scaler_file)
                                self.pitcher_stat_performance[model_name] = perf
                        except Exception as e:
                            print(f"⚠️ Failed to load pitcher model {model_name}: {e}")
                
                print(f"✅ Loaded {len(self.pitcher_stat_models)} pitcher stat models")
                
            except Exception as e:
                print(f"❌ Failed to load pitcher stat models: {e}")
    
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
            return False
        
        print(f"✅ CSV format validation passed")
        return True
    
    def predict_from_csv(self, csv_file, output_file=None):
        """Predict skill rates from CSV file"""
        try:
            print(f"📊 Loading data from: {csv_file}")
            df = pd.read_csv(csv_file)
            
            if not self.validate_csv_format(df):
                return None
            
            # Add default position if missing
            if 'position' not in df.columns:
                df['position'] = 'OF'
                print("📋 No position column found, defaulting all players to OF")
            
            print(f"🎯 Processing {len(df)} players for skill rate predictions...")
            
            results = []
            
            for idx, row in df.iterrows():
                try:
                    player_name = row['player_name']
                    position = row['position']
                    
                    # Prepare features
                    feature_cols = [
                        'avg_fantasy_points_L15',
                        'avg_fantasy_points_L10', 
                        'avg_fantasy_points_L5',
                        'games_since_last_good_game',
                        'trend_last_5_games',
                        'consistency_score'
                    ]
                    
                    features = row[feature_cols].values.reshape(1, -1)
                    features = np.nan_to_num(features, nan=0.0)
                    
                    # Create result record
                    result_record = {
                        'player_name': player_name,
                        'position': position,
                        'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Predict fantasy points
                    fantasy_result = self._predict_fantasy_points(features, position)
                    result_record.update({
                        'predicted_fantasy_points': fantasy_result['predicted'],
                        'fantasy_confidence': fantasy_result['confidence'],
                        'fantasy_model_r2': fantasy_result.get('model_r2', 0)
                    })
                    
                    if position == 'P':
                        # Pitcher: Use individual stat models
                        pitcher_stats = self._predict_pitcher_stats(features)
                        result_record.update(pitcher_stats)
                    else:
                        # Batter: Use skill rate models
                        batter_skills = self._predict_batter_skill_rates(features)
                        result_record.update(batter_skills)
                    
                    results.append(result_record)
                    print(f"✅ {player_name} ({position}): Fantasy {fantasy_result['predicted']:.2f}")
                    
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
                output_file = f'skill_rate_predictions_{timestamp}.csv'
            
            results_df.to_csv(output_file, index=False)
            
            # Summary
            print(f"\n📊 SKILL RATE PREDICTION SUMMARY:")
            print(f"{'='*60}")
            print(f"📋 Total players processed: {len(df)}")
            print(f"✅ Successful predictions: {len(results_df)}")
            print(f"📁 Output file: {output_file}")
            
            # Separate batters and pitchers
            batters = results_df[results_df['position'] != 'P']
            pitchers = results_df[results_df['position'] == 'P']
            
            if len(batters) > 0:
                print(f"\n⚾ BATTER SKILL RATES ({len(batters)} players):")
                if 'batting_average_skill' in batters.columns:
                    avg_ba = batters['batting_average_skill'].mean()
                    avg_obp = batters['on_base_percentage_skill'].mean()
                    avg_slg = batters['slugging_percentage_skill'].mean()
                    print(f"  Average Batting Average Skill: {avg_ba:.3f}")
                    print(f"  Average On-Base Percentage Skill: {avg_obp:.3f}")
                    print(f"  Average Slugging Percentage Skill: {avg_slg:.3f}")
            
            if len(pitchers) > 0:
                print(f"\n🥎 PITCHER STATS ({len(pitchers)} players):")
                if 'predicted_innings_pitched' in pitchers.columns:
                    avg_ip = pitchers['predicted_innings_pitched'].mean()
                    avg_k = pitchers['predicted_strikeouts'].mean()
                    print(f"  Average Innings Pitched: {avg_ip:.1f}")
                    print(f"  Average Strikeouts: {avg_k:.1f}")
            
            print(f"\n✅ Skill rate predictions saved to: {output_file}")
            return results_df
            
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
            return None
    
    def _predict_fantasy_points(self, features, position):
        """Predict fantasy points"""
        try:
            model_position = position if position in self.fantasy_models else 'OF'
            
            if model_position not in self.fantasy_models:
                return {'predicted': 0, 'confidence': 0, 'error': 'No model available'}
            
            features_scaled = self.fantasy_scalers[model_position].transform(features)
            prediction = self.fantasy_models[model_position].predict(features_scaled)[0]
            
            model_r2 = self.fantasy_performance[model_position]['r2']
            confidence = min(0.9, max(0.3, model_r2))
            
            return {
                'predicted': round(prediction, 2),
                'confidence': round(confidence, 2),
                'model_r2': round(model_r2, 3)
            }
            
        except Exception as e:
            return {'predicted': 0, 'confidence': 0, 'error': str(e)}
    
    def _predict_batter_skill_rates(self, features):
        """Predict batter skill rates"""
        skill_predictions = {}
        
        if not self.rate_models:
            # Fallback estimates if no rate models
            return {
                'batting_average_skill': 0.250,
                'batting_average_skill_confidence': 0.1,
                'on_base_percentage_skill': 0.320,
                'on_base_percentage_skill_confidence': 0.1,
                'slugging_percentage_skill': 0.400,
                'slugging_percentage_skill_confidence': 0.1,
                'walk_rate_skill': 0.08,
                'walk_rate_skill_confidence': 0.1,
                'strikeout_rate_skill': 0.22,
                'strikeout_rate_skill_confidence': 0.1,
                'power_rate_skill': 0.03,
                'power_rate_skill_confidence': 0.1
            }
        
        # Default player features for rate prediction
        default_features = {
            'player_age': 28,
            'age_factor': 1.0,
            'games_played': 140,
            'playing_time_factor': 0.86,
            'G': 140,
            'AB': 500,
            'PA': 600,
            'season': 2024,
            'tier_above_average': 0,
            'tier_average': 1,
            'tier_below_average': 0,
            'tier_elite': 0
        }
        
        # Map rate models to skill names
        rate_mapping = {
            'rate_on_base_pct': 'on_base_percentage_skill',
            'rate_slugging_pct': 'slugging_percentage_skill', 
            'rate_walk_rate': 'walk_rate_skill',
            'rate_strikeout_rate': 'strikeout_rate_skill',
            'rate_home_run_rate': 'power_rate_skill'
        }
        
        for rate_name, model in self.rate_models.items():
            if rate_name in rate_mapping:
                try:
                    expected_features = self.rate_performance[rate_name]['features']
                    feature_vector = [default_features.get(f, 0) for f in expected_features]
                    feature_array = np.array(feature_vector).reshape(1, -1)
                    
                    scaled_features = self.rate_scalers[rate_name].transform(feature_array)
                    prediction = model.predict(scaled_features)[0]
                    confidence = self.rate_performance[rate_name]['r2']
                    
                    skill_name = rate_mapping[rate_name]
                    skill_predictions[skill_name] = round(prediction, 3)
                    skill_predictions[f'{skill_name}_confidence'] = round(confidence, 3)
                    
                except Exception as e:
                    skill_name = rate_mapping[rate_name]
                    skill_predictions[skill_name] = 0.250
                    skill_predictions[f'{skill_name}_confidence'] = 0.1
        
        # Estimate batting average from OBP and slugging if not directly available
        if 'batting_average_skill' not in skill_predictions:
            obp = skill_predictions.get('on_base_percentage_skill', 0.320)
            slg = skill_predictions.get('slugging_percentage_skill', 0.400)
            # Rough estimate: BA is typically 85-90% of OBP for most players
            estimated_ba = max(0.180, min(0.400, obp * 0.875))
            skill_predictions['batting_average_skill'] = round(estimated_ba, 3)
            skill_predictions['batting_average_skill_confidence'] = round(
                (skill_predictions.get('on_base_percentage_skill_confidence', 0.1) + 
                 skill_predictions.get('slugging_percentage_skill_confidence', 0.1)) / 2, 3
            )
        
        return skill_predictions
    
    def _predict_pitcher_stats(self, features):
        """Predict pitcher stats using individual stat models"""
        predictions = {}
        
        stat_names = ['innings_pitched', 'strikeouts', 'hits_allowed', 
                     'walks_allowed', 'home_runs_allowed', 'earned_runs']
        
        for stat_name in stat_names:
            model_key = f"pitcher_{stat_name}"
            
            if model_key in self.pitcher_stat_models:
                try:
                    scaled_features = self.pitcher_stat_scalers[model_key].transform(features)
                    prediction = self.pitcher_stat_models[model_key].predict(scaled_features)[0]
                    
                    if stat_name != 'innings_pitched':
                        prediction = max(0, prediction)
                    
                    if stat_name == 'innings_pitched':
                        prediction = round(prediction, 1)
                    else:
                        prediction = round(prediction)
                    
                    model_r2 = self.pitcher_stat_performance[model_key]['r2']
                    confidence = min(0.9, max(0.1, model_r2))
                    
                    predictions[f'predicted_{stat_name}'] = prediction
                    predictions[f'predicted_{stat_name}_confidence'] = round(confidence, 3)
                    
                except Exception as e:
                    predictions[f'predicted_{stat_name}'] = 0
                    predictions[f'predicted_{stat_name}_confidence'] = 0
            else:
                predictions[f'predicted_{stat_name}'] = 0
                predictions[f'predicted_{stat_name}_confidence'] = 0
        
        return predictions

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='MLB Skill Rate Predictions from CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Predicts underlying player skill rates from CSV data:

BATTER SKILL RATES:
  • batting_average_skill: True BA ability (target R² = 60-70%)
  • on_base_percentage_skill: True OBP ability (target R² = 65-75%)
  • slugging_percentage_skill: True SLG ability (target R² = 70-85%)
  • walk_rate_skill: BB/PA rate (target R² = 70-80%)
  • strikeout_rate_skill: SO/PA rate (target R² = 75-85%)
  • power_rate_skill: HR/AB rate (target R² = 75-85%)

PITCHER STATS (existing models):
  • predicted_innings_pitched, predicted_strikeouts, etc.

CSV Format:
  player_name,position,avg_fantasy_points_L15,avg_fantasy_points_L10,avg_fantasy_points_L5,games_since_last_good_game,trend_last_5_games,consistency_score
  Aaron Judge,OF,8.5,9.2,7.8,2,0.5,0.75
  Gerrit Cole,P,12.8,13.2,11.9,1,0.8,0.85

Examples:
  python predict_skill_rates_csv.py players.csv
  python predict_skill_rates_csv.py players.csv --output skill_rates.csv
        """
    )
    
    parser.add_argument('csv_file', help='Input CSV file with player data')
    parser.add_argument('--output', '-o', help='Output CSV file (auto-generated if not specified)')
    parser.add_argument('--fantasy-models', '-f', default='models', help='Fantasy models directory')
    parser.add_argument('--rate-models', '-r', help='Rate models directory (auto-detected if not specified)')
    parser.add_argument('--stat-models', '-s', help='Stat models directory (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv_file):
        print(f"❌ Input file not found: {args.csv_file}")
        return False
    
    print("🚀 MLB SKILL RATE PREDICTION FROM CSV")
    print("=" * 60)
    print(f"📊 Input file: {args.csv_file}")
    print(f"🎯 Fantasy models: {args.fantasy_models}")
    print(f"📈 Rate models: {args.rate_models or 'auto-detect'}")
    print(f"⚾ Stat models: {args.stat_models or 'auto-detect'}")
    
    predictor = SkillRatePredictor(
        fantasy_models_dir=args.fantasy_models,
        rate_models_dir=args.rate_models,
        stat_models_dir=args.stat_models
    )
    
    results = predictor.predict_from_csv(args.csv_file, args.output)
    
    if results is not None:
        print(f"\n🎉 Skill rate predictions completed successfully!")
        return True
    else:
        print(f"\n❌ Skill rate predictions failed")
        return False

if __name__ == "__main__":
    main()