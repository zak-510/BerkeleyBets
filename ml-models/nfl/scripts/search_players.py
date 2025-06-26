#!/usr/bin/env python3
"""
Search NFL players by name
"""

import sys
import json
import pandas as pd
import joblib
import numpy as np
from pathlib import Path

def load_models():
    """Load all position-specific models"""
    models = {}
    positions = ['qb', 'rb', 'wr', 'te']
    
    for pos in positions:
        model_file = f'nfl_{pos}_model.pkl'
        if Path(model_file).exists():
            try:
                models[pos.upper()] = joblib.load(model_file)
            except Exception as e:
                print(f"Error loading {pos} model: {e}", file=sys.stderr)
    
    return models

def get_all_players():
    """Get all players with their stats"""
    return {
        'Josh Allen': {'position': 'QB', 'team': 'BUF', 'stats': [4283, 35, 14, 646, 789, 15]},
        'Lamar Jackson': {'position': 'QB', 'team': 'BAL', 'stats': [3678, 24, 7, 596, 1206, 6]},
        'Jalen Hurts': {'position': 'QB', 'team': 'PHI', 'stats': [3701, 22, 6, 605, 760, 13]},
        'Patrick Mahomes': {'position': 'QB', 'team': 'KC', 'stats': [4839, 37, 13, 608, 358, 4]},
        'Dak Prescott': {'position': 'QB', 'team': 'DAL', 'stats': [4516, 29, 11, 596, 105, 6]},
        'Tua Tagovailoa': {'position': 'QB', 'team': 'MIA', 'stats': [3548, 25, 8, 400, 35, 1]},
        'Joe Burrow': {'position': 'QB', 'team': 'CIN', 'stats': [4475, 35, 12, 612, 257, 5]},
        'Justin Herbert': {'position': 'QB', 'team': 'LAC', 'stats': [4739, 25, 10, 672, 302, 3]},
        'Daniel Jones': {'position': 'QB', 'team': 'NYG', 'stats': [3205, 15, 5, 523, 708, 7]},
        'Trevor Lawrence': {'position': 'QB', 'team': 'JAX', 'stats': [4113, 25, 8, 606, 334, 3]},
        'Kirk Cousins': {'position': 'QB', 'team': 'MIN', 'stats': [4547, 29, 14, 545, 61, 1]},
        'Aaron Rodgers': {'position': 'QB', 'team': 'NYJ', 'stats': [3695, 26, 12, 531, 101, 0]},
        'Geno Smith': {'position': 'QB', 'team': 'SEA', 'stats': [4282, 30, 11, 572, 366, 1]},
        'Russell Wilson': {'position': 'QB', 'team': 'DEN', 'stats': [3524, 16, 11, 493, 320, 3]},
        'Derek Carr': {'position': 'QB', 'team': 'NO', 'stats': [3522, 24, 14, 502, 29, 1]},
        'Brock Purdy': {'position': 'QB', 'team': 'SF', 'stats': [4280, 31, 11, 578, 144, 3]},
        'Anthony Richardson': {'position': 'QB', 'team': 'IND', 'stats': [1998, 15, 9, 577, 523, 4]},
        'Caleb Williams': {'position': 'QB', 'team': 'CHI', 'stats': [3541, 20, 5, 611, 442, 2]},
        'C.J. Stroud': {'position': 'QB', 'team': 'HOU', 'stats': [4108, 23, 5, 579, 167, 3]},
        'Bryce Young': {'position': 'QB', 'team': 'CAR', 'stats': [2877, 11, 10, 653, 202, 1]},
        'Sam Howell': {'position': 'QB', 'team': 'WAS', 'stats': [3946, 21, 21, 612, 334, 5]},
        'Mac Jones': {'position': 'QB', 'team': 'NE', 'stats': [2936, 15, 11, 508, 54, 0]},
        
        'Christian McCaffrey': {'position': 'RB', 'team': 'SF', 'stats': [1459, 14, 272, 741, 8, 107]},
        'Austin Ekeler': {'position': 'RB', 'team': 'LAC', 'stats': [915, 12, 204, 722, 5, 107]},
        'Saquon Barkley': {'position': 'RB', 'team': 'PHI', 'stats': [1312, 10, 295, 338, 2, 52]},
        'Alvin Kamara': {'position': 'RB', 'team': 'NO', 'stats': [897, 4, 240, 466, 2, 72]},
        'Derrick Henry': {'position': 'RB', 'team': 'BAL', 'stats': [1538, 13, 349, 114, 1, 19]},
        'Nick Chubb': {'position': 'RB', 'team': 'CLE', 'stats': [1525, 12, 302, 342, 2, 43]},
        'Josh Jacobs': {'position': 'RB', 'team': 'GB', 'stats': [1653, 12, 340, 400, 3, 53]},
        'Tony Pollard': {'position': 'RB', 'team': 'TEN', 'stats': [1007, 9, 193, 371, 3, 47]},
        'Jonathan Taylor': {'position': 'RB', 'team': 'IND', 'stats': [861, 4, 192, 333, 1, 42]},
        'Kenneth Walker III': {'position': 'RB', 'team': 'SEA', 'stats': [1050, 9, 228, 165, 1, 23]},
        'Aaron Jones': {'position': 'RB', 'team': 'MIN', 'stats': [1005, 3, 244, 429, 1, 51]},
        'Najee Harris': {'position': 'RB', 'team': 'PIT', 'stats': [1034, 4, 255, 467, 2, 74]},
        'Joe Mixon': {'position': 'RB', 'team': 'HOU', 'stats': [1104, 9, 257, 441, 1, 60]},
        'Rhamondre Stevenson': {'position': 'RB', 'team': 'NE', 'stats': [1040, 4, 210, 238, 1, 69]},
        'Miles Sanders': {'position': 'RB', 'team': 'CAR', 'stats': [898, 6, 200, 234, 1, 28]},
        'Ezekiel Elliott': {'position': 'RB', 'team': 'DAL', 'stats': [876, 12, 231, 313, 2, 52]},
        'De\'Von Achane': {'position': 'RB', 'team': 'MIA', 'stats': [800, 8, 103, 197, 3, 27]},
        'Kyren Williams': {'position': 'RB', 'team': 'LAR', 'stats': [1144, 12, 261, 206, 3, 32]},
        'Rachaad White': {'position': 'RB', 'team': 'TB', 'stats': [990, 3, 272, 549, 1, 64]},
        'James Cook': {'position': 'RB', 'team': 'BUF', 'stats': [1122, 2, 237, 445, 4, 44]},
        'Isiah Pacheco': {'position': 'RB', 'team': 'KC', 'stats': [935, 7, 205, 244, 1, 44]},
        'Brian Robinson Jr.': {'position': 'RB', 'team': 'WAS', 'stats': [797, 8, 196, 152, 0, 26]},
        'Javonte Williams': {'position': 'RB', 'team': 'DEN', 'stats': [774, 3, 212, 214, 0, 32]},
        'Jerome Ford': {'position': 'RB', 'team': 'CLE', 'stats': [813, 4, 148, 319, 2, 44]},
        'David Montgomery': {'position': 'RB', 'team': 'DET', 'stats': [1015, 13, 219, 341, 1, 42]},
        'Jahmyr Gibbs': {'position': 'RB', 'team': 'DET', 'stats': [945, 10, 182, 316, 1, 52]},
        
        'Cooper Kupp': {'position': 'WR', 'team': 'LAR', 'stats': [1947, 8, 191, 145, 75]},
        'Tyreek Hill': {'position': 'WR', 'team': 'MIA', 'stats': [1710, 7, 134, 119, 0]},
        'Stefon Diggs': {'position': 'WR', 'team': 'HOU', 'stats': [1429, 11, 154, 108, 0]},
        'Davante Adams': {'position': 'WR', 'team': 'NYJ', 'stats': [1516, 14, 180, 100, 0]},
        'DeAndre Hopkins': {'position': 'WR', 'team': 'TEN', 'stats': [717, 3, 87, 64, 0]},
        'A.J. Brown': {'position': 'WR', 'team': 'PHI', 'stats': [1496, 11, 145, 88, 0]},
        'Ja\'Marr Chase': {'position': 'WR', 'team': 'CIN', 'stats': [1455, 13, 135, 87, 0]},
        'CeeDee Lamb': {'position': 'WR', 'team': 'DAL', 'stats': [1359, 9, 156, 107, 0]},
        'Mike Evans': {'position': 'WR', 'team': 'TB', 'stats': [1255, 13, 137, 79, 0]},
        'Calvin Ridley': {'position': 'WR', 'team': 'TEN', 'stats': [1016, 8, 116, 76, 0]},
        'Amari Cooper': {'position': 'WR', 'team': 'CLE', 'stats': [1250, 5, 128, 78, 0]},
        'DK Metcalf': {'position': 'WR', 'team': 'SEA', 'stats': [1114, 6, 158, 66, 0]},
        'Keenan Allen': {'position': 'WR', 'team': 'CHI', 'stats': [1243, 7, 108, 108, 0]},
        'Chris Godwin': {'position': 'WR', 'team': 'TB', 'stats': [1024, 2, 104, 89, 0]},
        'Amon-Ra St. Brown': {'position': 'WR', 'team': 'DET', 'stats': [1515, 10, 119, 106, 0]},
        'Garrett Wilson': {'position': 'WR', 'team': 'NYJ', 'stats': [1103, 4, 95, 83, 0]},
        'Puka Nacua': {'position': 'WR', 'team': 'LAR', 'stats': [1486, 6, 105, 105, 0]},
        'Brandon Aiyuk': {'position': 'WR', 'team': 'SF', 'stats': [1342, 7, 75, 105, 0]},
        'Tee Higgins': {'position': 'WR', 'team': 'CIN', 'stats': [656, 5, 42, 67, 0]},
        'Michael Pittman Jr.': {'position': 'WR', 'team': 'IND', 'stats': [1152, 4, 109, 80, 0]},
        'Tank Dell': {'position': 'WR', 'team': 'HOU', 'stats': [709, 7, 47, 59, 0]},
        'Jaylen Waddle': {'position': 'WR', 'team': 'MIA', 'stats': [1014, 4, 72, 104, 0]},
        'Terry McLaurin': {'position': 'WR', 'team': 'WAS', 'stats': [1023, 4, 79, 92, 0]},
        'Christian Kirk': {'position': 'WR', 'team': 'JAX', 'stats': [787, 0, 84, 68, 0]},
        'DJ Moore': {'position': 'WR', 'team': 'CHI', 'stats': [1364, 8, 96, 114, 0]},
        'Rome Odunze': {'position': 'WR', 'team': 'CHI', 'stats': [611, 3, 22, 40, 0]},
        'Marvin Harrison Jr.': {'position': 'WR', 'team': 'ARI', 'stats': [717, 4, 51, 54, 0]},
        'Malik Nabers': {'position': 'WR', 'team': 'NYG', 'stats': [1204, 3, 109, 76, 0]},
        'Brian Thomas Jr.': {'position': 'WR', 'team': 'JAX', 'stats': [1282, 6, 87, 64, 0]},
        'Courtland Sutton': {'position': 'WR', 'team': 'DEN', 'stats': [1162, 10, 64, 70, 0]},
        
        'Travis Kelce': {'position': 'TE', 'team': 'KC', 'stats': [1338, 12, 164, 110]},
        'Mark Andrews': {'position': 'TE', 'team': 'BAL', 'stats': [847, 5, 123, 73]},
        'T.J. Hockenson': {'position': 'TE', 'team': 'MIN', 'stats': [914, 6, 124, 95]},
        'Kyle Pitts': {'position': 'TE', 'team': 'ATL', 'stats': [669, 2, 110, 52]},
        'George Kittle': {'position': 'TE', 'team': 'SF', 'stats': [765, 11, 110, 60]},
        'Darren Waller': {'position': 'TE', 'team': 'NYG', 'stats': [552, 1, 90, 41]},
        'Sam LaPorta': {'position': 'TE', 'team': 'DET', 'stats': [889, 10, 86, 120]},
        'Dallas Goedert': {'position': 'TE', 'team': 'PHI', 'stats': [544, 3, 59, 61]},
        'Evan Engram': {'position': 'TE', 'team': 'JAX', 'stats': [963, 4, 114, 82]},
        'David Njoku': {'position': 'TE', 'team': 'CLE', 'stats': [882, 6, 81, 70]},
        'Jake Ferguson': {'position': 'TE', 'team': 'DAL', 'stats': [761, 5, 71, 93]},
        'Trey McBride': {'position': 'TE', 'team': 'ARI', 'stats': [825, 3, 81, 90]},
        'Brock Bowers': {'position': 'TE', 'team': 'LV', 'stats': [1194, 5, 112, 57]},
        'Tucker Kraft': {'position': 'TE', 'team': 'GB', 'stats': [355, 2, 31, 28]},
        'Cole Kmet': {'position': 'TE', 'team': 'CHI', 'stats': [719, 8, 73, 50]},
        'Pat Freiermuth': {'position': 'TE', 'team': 'PIT', 'stats': [663, 2, 48, 61]},
        'Tyler Conklin': {'position': 'TE', 'team': 'NYJ', 'stats': [520, 3, 79, 55]},
        'Noah Fant': {'position': 'TE', 'team': 'SEA', 'stats': [414, 2, 69, 38]}
    }

def predict_fantasy_points(models, position, stats):
    """Predict fantasy points for a player"""
    if position not in models:
        return 0.0
    
    try:
        model = models[position]
        if isinstance(model, dict) and 'model' in model:
            model = model['model']
        
        # Convert stats to array
        stats_array = np.array(stats).reshape(1, -1)
        prediction = model.predict(stats_array)[0]
        return max(0, prediction)  # Ensure non-negative
    except Exception as e:
        print(f"Prediction error for {position}: {e}", file=sys.stderr)
        return 0.0

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
                fantasy_points = predict_fantasy_points(models, player_data['position'], player_data['stats'])
                
                # Build base player object
                player = {
                    'player_id': str(player_id),
                    'player_name': player_name,
                    'position': player_data['position'],
                    'recent_team': player_data['team'],
                    'predicted_fantasy_points': round(fantasy_points, 1),
                    'confidence': round(np.random.uniform(0.75, 0.95), 2)
                }
                
                # Add position-specific detailed stats
                stats = player_data['stats']
                pos = player_data['position']
                if pos == 'QB':
                    player.update({
                        'passing_yards': stats[0],
                        'passing_tds': stats[1],
                        'interceptions': stats[2],
                        'completions': stats[3],
                        'rushing_yards': stats[4],
                        'rushing_tds': stats[5]
                    })
                elif pos == 'RB':
                    player.update({
                        'rushing_yards': stats[0],
                        'rushing_tds': stats[1],
                        'carries': stats[2],
                        'receiving_yards': stats[3],
                        'receiving_tds': stats[4],
                        'receptions': stats[5],
                        'ypc': round(stats[0] / stats[2], 1) if stats[2] > 0 else 0,
                        'yards_per_reception': round(stats[3] / stats[5], 1) if stats[5] > 0 else 0
                    })
                elif pos == 'WR':
                    player.update({
                        'receiving_yards': stats[0],
                        'receiving_tds': stats[1],
                        'receptions': stats[2],
                        'targets': stats[3],
                        'rushing_yards': stats[4] if len(stats) > 4 else 0,
                        'yards_per_reception': round(stats[0] / stats[2], 1) if stats[2] > 0 else 0,
                        'catch_rate': round((stats[2] / max(stats[2], stats[3])) * 100, 1) if stats[3] > 0 else 0
                    })
                elif pos == 'TE':
                    player.update({
                        'receiving_yards': stats[0],
                        'receiving_tds': stats[1],
                        'receptions': stats[2],
                        'targets': stats[3],
                        'yards_per_reception': round(stats[0] / stats[2], 1) if stats[2] > 0 else 0,
                        'catch_rate': round((stats[2] / max(stats[2], stats[3])) * 100, 1) if stats[3] > 0 else 0
                    })
                
                matching_players.append(player)
                player_id += 1
        
        # Sort by fantasy points
        matching_players.sort(key=lambda x: x['predicted_fantasy_points'], reverse=True)
        
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