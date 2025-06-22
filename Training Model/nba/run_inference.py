#!/usr/bin/env python3
"""
NBA Player Inference Script - Using Fixed Leakage-Free Model

Runs predictions on all active NBA players using the truly leakage-free model
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
import time

# Import the fixed model
try:
    from nba_model_fixed import NBAPlayerProjectionModelFixed
except ImportError:
    print("❌ Error: Cannot import nba_model_fixed. Make sure nba_model_fixed.py is available.")
    sys.exit(1)

def run_all_player_inference():
    """Run inference on all active NBA players"""
    
    print("🏀 NBA PLAYER INFERENCE - LEAKAGE-FREE MODEL")
    print("=" * 60)
    print("🔒 Using ONLY historical averages from previous games")
    print("🎯 Zero data leakage - truly predictive model")
    print()
    
    # Initialize the fixed model
    model = NBAPlayerProjectionModelFixed()
    
    # Check if models exist
    try:
        model.load_models()
        print("✅ Loaded fixed leakage-free models successfully")
    except Exception as e:
        print(f"❌ Error loading models: {str(e)}")
        print("💡 Run 'python nba_model_fixed.py' first to train the models")
        return
    
    print(f"📊 Available models: {list(model.models.keys())}")
    print()
    
    # Fetch real NBA data for inference
    print("📊 STEP 1: Fetching Active NBA Player Data")
    print("-" * 40)
    
    try:
        # Use the model's data fetching capability
        print("🏀 Fetching real NBA player data for inference...")
        
        # Fetch data for a larger set of players for inference
        df_raw = model.fetch_player_data(max_players=100)  # Get more players for inference
        
        if df_raw is None or len(df_raw) == 0:
            print("❌ No NBA data available. Check your internet connection.")
            return
            
        print(f"✅ Successfully fetched data for {df_raw['player_name'].nunique()} players")
        print(f"📊 Total games: {len(df_raw)}")
        
    except Exception as e:
        print(f"❌ Error fetching NBA data: {str(e)}")
        return
    
    # Clean and prepare data
    print("\n📊 STEP 2: Preparing Data for Inference")
    print("-" * 40)
    
    try:
        # Clean and engineer historical features
        df_clean = model.clean_and_engineer_features(df_raw)
        
        if len(df_clean) == 0:
            print("❌ No valid data after cleaning")
            return
            
        print(f"✅ Prepared {len(df_clean)} games from {df_clean['player_name'].nunique()} players")
        
    except Exception as e:
        print(f"❌ Error preparing data: {str(e)}")
        return
    
    # Run inference on latest games for each player
    print("\n🎯 STEP 3: Running Inference on Latest Player Data")
    print("-" * 40)
    
    inference_results = []
    players_processed = 0
    successful_predictions = 0
    
    # Get the most recent game for each player (for inference)
    latest_games = df_clean.groupby('player_name').tail(1).reset_index(drop=True)
    
    print(f"🎯 Running inference on {len(latest_games)} players...")
    
    for idx, row in latest_games.iterrows():
        try:
            player_name = row['player_name']
            position = row['position']
            
            # Create feature dict for prediction
            player_features = {
                'position': position,
                'hist_fg_pct': row['hist_fg_pct'],
                'hist_fg3_pct': row['hist_fg3_pct'],
                'hist_ft_pct': row['hist_ft_pct'],
                'hist_min_avg': row['hist_min_avg'],
                'hist_usage_rate': row['hist_usage_rate']
            }
            
            # Make prediction
            prediction = model.predict_player_performance(player_features)
            
            if prediction is not None:
                inference_results.append({
                    'player_name': player_name,
                    'position': position,
                    'hist_fg_pct': row['hist_fg_pct'],
                    'hist_fg3_pct': row['hist_fg3_pct'],
                    'hist_ft_pct': row['hist_ft_pct'],
                    'hist_min_avg': row['hist_min_avg'],
                    'hist_usage_rate': row['hist_usage_rate'],
                    'predicted_pts': prediction['pts'],
                    'predicted_reb': prediction['reb'],
                    'predicted_ast': prediction['ast'],
                    'predicted_fantasy_points': prediction['fantasy_points'],
                    'inference_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                successful_predictions += 1
                
                if successful_predictions % 10 == 0:
                    print(f"✅ Processed {successful_predictions} players...")
            
            players_processed += 1
            
        except Exception as e:
            print(f"⚠️  Error processing {row.get('player_name', 'Unknown')}: {str(e)}")
            continue
    
    if not inference_results:
        print("❌ No successful predictions generated")
        return
    
    # Convert to DataFrame and save results
    print("\n💾 STEP 4: Saving Inference Results")
    print("-" * 40)
    
    results_df = pd.DataFrame(inference_results)
    
    # Sort by predicted fantasy points (descending)
    results_df = results_df.sort_values('predicted_fantasy_points', ascending=False)
    
    # Save to CSV
    output_file = f"nba_player_inference_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    results_df.to_csv(output_file, index=False)
    
    print(f"✅ Saved inference results to: {output_file}")
    print(f"📊 Total predictions: {len(results_df)}")
    print(f"👥 Players analyzed: {results_df['player_name'].nunique()}")
    
    # Display top performers
    print("\n🏆 TOP 20 PREDICTED PERFORMERS (Fantasy Points)")
    print("=" * 80)
    print(f"{'Rank':<4} {'Player':<25} {'Pos':<3} {'PTS':<5} {'REB':<5} {'AST':<5} {'Fantasy':<8}")
    print("-" * 80)
    
    for i, (_, row) in enumerate(results_df.head(20).iterrows(), 1):
        print(f"{i:<4} {row['player_name']:<25} {row['position']:<3} "
              f"{row['predicted_pts']:<5.1f} {row['predicted_reb']:<5.1f} "
              f"{row['predicted_ast']:<5.1f} {row['predicted_fantasy_points']:<8.1f}")
    
    # Show position breakdown
    print(f"\n📊 PREDICTIONS BY POSITION:")
    print("-" * 40)
    position_stats = results_df.groupby('position').agg({
        'predicted_pts': 'mean',
        'predicted_reb': 'mean', 
        'predicted_ast': 'mean',
        'predicted_fantasy_points': 'mean',
        'player_name': 'count'
    }).round(1)
    
    position_stats.columns = ['Avg_PTS', 'Avg_REB', 'Avg_AST', 'Avg_Fantasy', 'Count']
    print(position_stats)
    
    # Show feature ranges used
    print(f"\n🔍 HISTORICAL FEATURE RANGES USED:")
    print("-" * 40)
    feature_stats = results_df[['hist_fg_pct', 'hist_fg3_pct', 'hist_ft_pct', 'hist_min_avg']].describe()
    print(feature_stats.round(3))
    
    print(f"\n✅ INFERENCE COMPLETE!")
    print(f"🔒 All predictions based on historical averages only")
    print(f"📊 Results saved to: {output_file}")
    print(f"🎯 {successful_predictions}/{players_processed} successful predictions")

if __name__ == "__main__":
    run_all_player_inference() 