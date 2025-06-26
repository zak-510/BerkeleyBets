#!/usr/bin/env python3
"""
Verify NBA Models Have No Data Leakage
Tests that predictions vary appropriately and don't match exact 2023-24 averages
"""

import json
import subprocess
import numpy as np

def test_predictions():
    """Test that predictions are realistic but not exact matches to known averages"""
    
    # Known 2023-24 averages for comparison
    known_averages = {
        'Luka Dončić': 32.4,
        'Joel Embiid': 34.7,
        'Giannis Antetokounmpo': 30.4,
        'Nikola Jokić': 26.4,
        'LeBron James': 25.7,
        'Jayson Tatum': 26.9,
        'Anthony Davis': 24.7,
        'Shai Gilgeous-Alexander': 30.1
    }
    
    print("TESTING NBA MODELS FOR DATA LEAKAGE")
    print("=" * 60)
    
    # Run get_top_players.py to get predictions
    try:
        result = subprocess.run(['python3', 'scripts/get_top_players.py', 'ALL', '50'], 
                              capture_output=True, text=True, cwd='..')
        
        if result.returncode != 0:
            print(f"Error running predictions: {result.stderr}")
            return False
            
        data = json.loads(result.stdout)
        players = data.get('players', [])
        
        if not players:
            print("No players returned from model")
            return False
            
        # Check for exact matches and patterns
        exact_matches = 0
        close_matches = 0  # Within 0.1
        unique_predictions = set()
        
        print("\nPlayer Predictions vs Known Averages:")
        print("-" * 60)
        
        for player in players:
            name = player['player_name']
            predicted = player['predicted_points']
            
            # Track unique predictions
            unique_predictions.add(predicted)
            
            if name in known_averages:
                actual = known_averages[name]
                diff = abs(predicted - actual)
                
                if diff < 0.01:  # Exact match
                    exact_matches += 1
                    status = "EXACT MATCH (LEAKAGE!)"
                elif diff < 0.1:  # Very close
                    close_matches += 1
                    status = "Very Close"
                elif diff < 2.0:  # Reasonable
                    status = "Good"
                else:
                    status = "OK"
                    
                print(f"{name:25} | Pred: {predicted:5.1f} | Actual: {actual:5.1f} | "
                      f"Diff: {diff:4.1f} | {status}")
        
        print("-" * 60)
        
        # Statistical analysis
        all_points = [p['predicted_points'] for p in players]
        all_rebounds = [p['predicted_rebounds'] for p in players]
        all_assists = [p['predicted_assists'] for p in players]
        
        print(f"\nSTATISTICAL ANALYSIS:")
        print(f"Total Players: {len(players)}")
        print(f"Unique Point Predictions: {len(unique_predictions)} "
              f"({len(unique_predictions)/len(players)*100:.1f}%)")
        print(f"Exact Matches to 2023-24: {exact_matches}")
        print(f"Very Close Matches (<0.1): {close_matches}")
        
        print(f"\nPREDICTION RANGES:")
        print(f"Points: {min(all_points):.1f} - {max(all_points):.1f} "
              f"(avg: {np.mean(all_points):.1f})")
        print(f"Rebounds: {min(all_rebounds):.1f} - {max(all_rebounds):.1f} "
              f"(avg: {np.mean(all_rebounds):.1f})")
        print(f"Assists: {min(all_assists):.1f} - {max(all_assists):.1f} "
              f"(avg: {np.mean(all_assists):.1f})")
        
        # Variance check
        points_std = np.std(all_points)
        print(f"\nVariance (Std Dev): {points_std:.2f}")
        
        # Final verdict
        print("\n" + "=" * 60)
        print("VERDICT:")
        
        if exact_matches > 2:
            print("FAIL: Too many exact matches - likely data leakage!")
            return False
        elif close_matches > 5:
            print("WARNING: Many very close matches - possible leakage")
            return False
        elif len(unique_predictions) < len(players) * 0.8:
            print("FAIL: Too many duplicate predictions")
            return False
        elif points_std < 2.0:
            print("FAIL: Insufficient variance in predictions")
            return False
        else:
            print("PASS: Models appear to be making genuine predictions!")
            print("No evidence of data leakage detected")
            return True
            
    except Exception as e:
        print(f"Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_predictions()
    exit(0 if success else 1) 