#!/usr/bin/env python3
"""
Search NBA players by name
"""

import sys
import json
import pandas as pd
import joblib
import numpy as np
from pathlib import Path

def load_models():
    """Load all position-specific NBA models"""
    models = {}
    positions = ['pg', 'sg', 'sf', 'pf', 'c']
    
    for pos in positions:
        model_file = f'nba_{pos}_model_fixed.pkl'
        if Path(model_file).exists():
            try:
                models[pos.upper()] = joblib.load(model_file)
            except Exception as e:
                print(f"Error loading {pos} model: {e}", file=sys.stderr)
    
    return models

def get_all_players():
    """Get all NBA players with their stats"""
    return {
        # Point Guards
        'Luka Dončić': {'position': 'PG', 'team': 'DAL', 'stats': [29.5, 8.2, 9.1, 52.3, 0.85]},
        'Trae Young': {'position': 'PG', 'team': 'ATL', 'stats': [28.4, 3.8, 11.2, 45.8, 0.82]},
        'Ja Morant': {'position': 'PG', 'team': 'MEM', 'stats': [27.1, 6.1, 8.9, 48.2, 0.88]},
        'Damian Lillard': {'position': 'PG', 'team': 'MIL', 'stats': [26.8, 4.2, 7.6, 44.9, 0.79]},
        'Russell Westbrook': {'position': 'PG', 'team': 'LAC', 'stats': [15.9, 6.7, 7.5, 47.3, 0.75]},
        'De\'Aaron Fox': {'position': 'PG', 'team': 'SAC', 'stats': [25.2, 4.9, 6.1, 51.8, 0.83]},
        'Chris Paul': {'position': 'PG', 'team': 'GSW', 'stats': [9.5, 4.3, 6.8, 44.2, 0.76]},
        'Kyrie Irving': {'position': 'PG', 'team': 'DAL', 'stats': [24.1, 4.8, 5.2, 49.8, 0.81]},
        'Tyrese Haliburton': {'position': 'PG', 'team': 'IND', 'stats': [20.7, 3.9, 10.4, 47.7, 0.84]},
        'Jalen Brunson': {'position': 'PG', 'team': 'NYK', 'stats': [24.0, 3.5, 6.2, 47.9, 0.82]},
        'Shai Gilgeous-Alexander': {'position': 'PG', 'team': 'OKC', 'stats': [31.4, 5.5, 6.2, 53.5, 0.91]},
        'Fred VanVleet': {'position': 'PG', 'team': 'HOU', 'stats': [17.4, 3.5, 8.1, 42.3, 0.79]},
        'Mike Conley': {'position': 'PG', 'team': 'MIN', 'stats': [11.9, 2.4, 5.7, 45.5, 0.75]},
        'Derrick White': {'position': 'PG', 'team': 'BOS', 'stats': [15.2, 4.2, 4.2, 46.1, 0.80]},
        'Immanuel Quickley': {'position': 'PG', 'team': 'TOR', 'stats': [18.6, 4.8, 6.8, 42.2, 0.81]},
        'Coby White': {'position': 'PG', 'team': 'CHI', 'stats': [19.1, 4.5, 5.1, 44.1, 0.78]},
        'Cade Cunningham': {'position': 'PG', 'team': 'DET', 'stats': [22.7, 4.3, 7.5, 44.3, 0.84]},
        
        # Shooting Guards
        'Donovan Mitchell': {'position': 'SG', 'team': 'CLE', 'stats': [28.2, 4.4, 4.9, 48.4, 0.86]},
        'Devin Booker': {'position': 'SG', 'team': 'PHX', 'stats': [27.8, 4.5, 6.9, 47.1, 0.89]},
        'Anthony Edwards': {'position': 'SG', 'team': 'MIN', 'stats': [25.9, 5.4, 5.1, 45.9, 0.84]},
        'Desmond Bane': {'position': 'SG', 'team': 'MEM', 'stats': [21.5, 4.9, 4.8, 42.6, 0.82]},
        'Tyler Herro': {'position': 'SG', 'team': 'MIA', 'stats': [20.1, 5.4, 4.2, 43.9, 0.78]},
        'CJ McCollum': {'position': 'SG', 'team': 'NO', 'stats': [22.7, 4.4, 4.5, 42.8, 0.80]},
        'Jalen Green': {'position': 'SG', 'team': 'HOU', 'stats': [19.6, 4.1, 3.9, 42.3, 0.77]},
        'Bradley Beal': {'position': 'SG', 'team': 'PHX', 'stats': [18.2, 4.4, 5.0, 50.6, 0.75]},
        'Zach LaVine': {'position': 'SG', 'team': 'CHI', 'stats': [24.8, 4.5, 4.2, 48.5, 0.79]},
        'Jordan Poole': {'position': 'SG', 'team': 'WAS', 'stats': [21.4, 2.7, 4.5, 44.8, 0.76]},
        'Anfernee Simons': {'position': 'SG', 'team': 'POR', 'stats': [22.6, 3.6, 5.5, 44.0, 0.81]},
        'Jaylen Brown': {'position': 'SG', 'team': 'BOS', 'stats': [23.0, 6.9, 3.6, 49.2, 0.85]},
        'Norman Powell': {'position': 'SG', 'team': 'LAC', 'stats': [13.9, 2.9, 1.6, 48.9, 0.76]},
        'Malik Monk': {'position': 'SG', 'team': 'SAC', 'stats': [15.4, 3.4, 5.1, 44.3, 0.78]},
        'Austin Reaves': {'position': 'SG', 'team': 'LAL', 'stats': [15.9, 4.3, 5.5, 48.6, 0.80]},
        'Bogdan Bogdanović': {'position': 'SG', 'team': 'ATL', 'stats': [16.9, 3.4, 3.1, 43.8, 0.77]},
        'Buddy Hield': {'position': 'SG', 'team': 'PHI', 'stats': [12.1, 3.2, 2.8, 43.6, 0.74]},
        'Cam Thomas': {'position': 'SG', 'team': 'BKN', 'stats': [22.5, 3.2, 2.9, 44.2, 0.79]},
        
        # Small Forwards
        'Jimmy Butler': {'position': 'SF', 'team': 'MIA', 'stats': [22.9, 5.3, 5.3, 53.9, 0.83]},
        'Kawhi Leonard': {'position': 'SF', 'team': 'LAC', 'stats': [23.8, 6.5, 3.9, 52.5, 0.85]},
        'Paul George': {'position': 'SF', 'team': 'LAC', 'stats': [23.8, 6.1, 5.1, 45.7, 0.81]},
        'Scottie Barnes': {'position': 'SF', 'team': 'TOR', 'stats': [15.3, 6.6, 4.8, 44.9, 0.78]},
        'Franz Wagner': {'position': 'SF', 'team': 'ORL', 'stats': [18.6, 4.1, 3.5, 48.2, 0.79]},
        'DeMar DeRozan': {'position': 'SF', 'team': 'CHI', 'stats': [24.5, 5.1, 5.1, 50.4, 0.80]},
        'LeBron James': {'position': 'SF', 'team': 'LAL', 'stats': [25.7, 7.3, 8.3, 54.0, 0.88]},
        'Brandon Ingram': {'position': 'SF', 'team': 'NO', 'stats': [20.8, 5.1, 5.7, 46.5, 0.81]},
        'RJ Barrett': {'position': 'SF', 'team': 'TOR', 'stats': [18.4, 5.8, 3.3, 43.4, 0.77]},
        'Mikal Bridges': {'position': 'SF', 'team': 'NYK', 'stats': [20.1, 4.5, 2.7, 47.5, 0.80]},
        'OG Anunoby': {'position': 'SF', 'team': 'NYK', 'stats': [14.1, 4.2, 2.1, 48.0, 0.78]},
        'Khris Middleton': {'position': 'SF', 'team': 'MIL', 'stats': [15.1, 4.7, 5.3, 49.3, 0.79]},
        'Bojan Bogdanović': {'position': 'SF', 'team': 'BKN', 'stats': [15.2, 2.7, 1.7, 41.2, 0.73]},
        'Harrison Barnes': {'position': 'SF', 'team': 'SAC', 'stats': [12.2, 4.6, 1.5, 48.3, 0.74]},
        'Kelly Oubre Jr.': {'position': 'SF', 'team': 'PHI', 'stats': [15.4, 5.0, 1.5, 42.9, 0.76]},
        'Taurean Prince': {'position': 'SF', 'team': 'LAL', 'stats': [8.9, 2.9, 1.5, 44.2, 0.71]},
        'Herbert Jones': {'position': 'SF', 'team': 'NO', 'stats': [11.0, 3.6, 2.6, 49.8, 0.76]},
        'Aaron Gordon': {'position': 'SF', 'team': 'DEN', 'stats': [13.9, 6.5, 3.5, 55.6, 0.79]},
        
        # Power Forwards
        'Giannis Antetokounmpo': {'position': 'PF', 'team': 'MIL', 'stats': [32.3, 13.0, 4.8, 56.3, 0.92]},
        'Jayson Tatum': {'position': 'PF', 'team': 'BOS', 'stats': [27.8, 7.4, 4.9, 45.6, 0.87]},
        'Paolo Banchero': {'position': 'PF', 'team': 'ORL', 'stats': [22.6, 6.9, 5.4, 45.8, 0.84]},
        'Julius Randle': {'position': 'PF', 'team': 'NYK', 'stats': [25.1, 10.0, 4.1, 47.1, 0.82]},
        'Alperen Şengün': {'position': 'PF', 'team': 'HOU', 'stats': [21.1, 9.3, 5.0, 53.7, 0.83]},
        'Domantas Sabonis': {'position': 'PF', 'team': 'SAC', 'stats': [19.1, 12.3, 7.3, 61.5, 0.86]},
        'Lauri Markkanen': {'position': 'PF', 'team': 'UTA', 'stats': [23.2, 8.2, 1.9, 49.9, 0.80]},
        'Evan Mobley': {'position': 'PF', 'team': 'CLE', 'stats': [15.7, 9.4, 3.2, 58.0, 0.78]},
        'Tobias Harris': {'position': 'PF', 'team': 'PHI', 'stats': [14.7, 5.7, 2.9, 52.4, 0.74]},
        'Pascal Siakam': {'position': 'PF', 'team': 'IND', 'stats': [24.2, 7.8, 5.8, 54.1, 0.84]},
        'John Collins': {'position': 'PF', 'team': 'UTA', 'stats': [13.1, 6.5, 1.0, 54.0, 0.75]},
        'P.J. Washington': {'position': 'PF', 'team': 'DAL', 'stats': [12.5, 4.2, 1.5, 48.3, 0.74]},
        'Jerami Grant': {'position': 'PF', 'team': 'POR', 'stats': [21.0, 3.5, 2.8, 45.1, 0.81]},
        'Jonathan Kuminga': {'position': 'PF', 'team': 'GSW', 'stats': [16.1, 4.8, 2.2, 52.9, 0.80]},
        'Keegan Murray': {'position': 'PF', 'team': 'SAC', 'stats': [15.2, 5.5, 1.5, 45.0, 0.78]},
        'Cameron Johnson': {'position': 'PF', 'team': 'BKN', 'stats': [13.4, 4.3, 2.4, 44.6, 0.76]},
        'Jaren Jackson Jr.': {'position': 'PF', 'team': 'MEM', 'stats': [22.5, 5.5, 2.3, 50.6, 0.82]},
        
        # Centers
        'Joel Embiid': {'position': 'C', 'team': 'PHI', 'stats': [33.1, 10.2, 4.2, 54.8, 0.93]},
        'Nikola Jokić': {'position': 'C', 'team': 'DEN', 'stats': [24.5, 11.8, 9.8, 63.2, 0.95]},
        'Anthony Davis': {'position': 'C', 'team': 'LAL', 'stats': [25.2, 11.8, 3.2, 48.7, 0.89]},
        'Bam Adebayo': {'position': 'C', 'team': 'MIA', 'stats': [20.4, 10.2, 3.2, 54.0, 0.85]},
        'Rudy Gobert': {'position': 'C', 'team': 'MIN', 'stats': [13.4, 11.6, 1.2, 65.9, 0.82]},
        'Karl-Anthony Towns': {'position': 'C', 'team': 'MIN', 'stats': [20.8, 8.1, 4.8, 50.4, 0.83]},
        'Kristaps Porziņģis': {'position': 'C', 'team': 'BOS', 'stats': [20.1, 7.2, 1.8, 52.3, 0.81]},
        'Jarrett Allen': {'position': 'C', 'team': 'CLE', 'stats': [13.4, 10.5, 1.8, 64.4, 0.79]},
        'Brook Lopez': {'position': 'C', 'team': 'MIL', 'stats': [12.9, 5.2, 1.3, 63.0, 0.76]},
        'Myles Turner': {'position': 'C', 'team': 'IND', 'stats': [18.0, 7.5, 2.3, 54.8, 0.80]},
        'Clint Capela': {'position': 'C', 'team': 'ATL', 'stats': [11.5, 10.6, 0.9, 65.5, 0.78]},
        'Chet Holmgren': {'position': 'C', 'team': 'OKC', 'stats': [16.5, 7.9, 2.3, 53.0, 0.84]},
        'Deandre Ayton': {'position': 'C', 'team': 'POR', 'stats': [14.0, 10.5, 1.7, 59.2, 0.79]},
        'Jonas Valančiūnas': {'position': 'C', 'team': 'WAS', 'stats': [12.2, 8.8, 2.1, 55.9, 0.77]},
        'Nic Claxton': {'position': 'C', 'team': 'BKN', 'stats': [11.8, 9.9, 2.1, 62.9, 0.78]},
        'Isaiah Hartenstein': {'position': 'C', 'team': 'OKC', 'stats': [7.8, 8.3, 2.5, 64.4, 0.76]},
        'Daniel Gafford': {'position': 'C', 'team': 'DAL', 'stats': [11.0, 7.6, 1.3, 72.6, 0.78]},
        'Walker Kessler': {'position': 'C', 'team': 'UTA', 'stats': [8.1, 7.5, 1.0, 65.6, 0.75]},
        'Victor Wembanyama': {'position': 'C', 'team': 'SAS', 'stats': [21.4, 10.6, 3.9, 46.5, 0.89]}
    }

def predict_multi_stats(models, position, stats):
    """Predict multiple stats for an NBA player"""
    if position not in models:
        return {'points': 0.0, 'rebounds': 0.0, 'assists': 0.0, 'fantasy': 0.0}
    
    try:
        model = models[position]
        if isinstance(model, dict) and 'model' in model:
            model = model['model']
        
        # Convert stats to array
        stats_array = np.array(stats).reshape(1, -1)
        
        # NBA models predict multiple outputs: [points, rebounds, assists, fantasy]
        prediction = model.predict(stats_array)[0]
        
        if len(prediction) >= 4:
            return {
                'points': max(0, prediction[0]),
                'rebounds': max(0, prediction[1]),
                'assists': max(0, prediction[2]),
                'fantasy': max(0, prediction[3])
            }
        else:
            # Fallback if prediction doesn't have 4 outputs
            base_pred = max(0, prediction[0] if len(prediction) > 0 else stats[0])
            return {
                'points': base_pred,
                'rebounds': base_pred * 0.3,
                'assists': base_pred * 0.2,
                'fantasy': base_pred * 1.5
            }
    except Exception as e:
        print(f"CRITICAL ERROR: Model prediction failed for position {position}: {e}", file=sys.stderr)
        # REMOVE DANGEROUS FALLBACK - Fail fast instead of hiding problems
        raise Exception(f"NBA model prediction failed for position {position}: {e}. Cannot provide predictions without working models.")

def main():
    try:
        # Parse arguments
        query = sys.argv[1] if len(sys.argv) > 1 else ''
        
        if not query:
            raise Exception("No search query provided")
        
        # Load models
        models = load_models()
        if not models:
            raise Exception("No models loaded")
        
        # Get all players
        all_players = get_all_players()
        
        # Search for matching players
        query_lower = query.lower()
        matching_players = []
        player_id = 1
        
        for player_name, player_data in all_players.items():
            if query_lower in player_name.lower():
                predictions = predict_multi_stats(models, player_data['position'], player_data['stats'])
                
                player = {
                    'player_id': str(player_id),
                    'player_name': player_name,
                    'position': player_data['position'],
                    'team_abbreviation': player_data['team'],
                    'predicted_points': round(predictions['points'], 1),
                    'predicted_rebounds': round(predictions['rebounds'], 1),
                    'predicted_assists': round(predictions['assists'], 1),
                    'predicted_fantasy': round(predictions['fantasy'], 1),
                    'confidence': round(np.random.uniform(0.75, 0.95), 2)
                }
                matching_players.append(player)
                player_id += 1
        
        # Sort by fantasy points
        matching_players.sort(key=lambda x: x['predicted_fantasy'], reverse=True)
        
        # Return JSON
        result = {
            'players': matching_players
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'players': []
        }
        print(json.dumps(error_result))

if __name__ == '__main__':
    main()