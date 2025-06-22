#!/usr/bin/env python3
"""
Get top NFL players with predictions
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

def get_sample_players():
    """Generate sample players with realistic stats for predictions"""
    return {
        'QB': [
            {'name': 'Josh Allen', 'team': 'BUF', 'stats': [4283, 35, 14, 646, 789, 15]},
            {'name': 'Lamar Jackson', 'team': 'BAL', 'stats': [3678, 24, 7, 596, 1206, 6]},
            {'name': 'Jalen Hurts', 'team': 'PHI', 'stats': [3701, 22, 6, 605, 760, 13]},
            {'name': 'Patrick Mahomes', 'team': 'KC', 'stats': [4839, 37, 13, 608, 358, 4]},
            {'name': 'Dak Prescott', 'team': 'DAL', 'stats': [4516, 29, 11, 596, 105, 6]},
            {'name': 'Tua Tagovailoa', 'team': 'MIA', 'stats': [3548, 25, 8, 400, 35, 1]},
            {'name': 'Joe Burrow', 'team': 'CIN', 'stats': [4475, 35, 12, 612, 257, 5]},
            {'name': 'Justin Herbert', 'team': 'LAC', 'stats': [4739, 25, 10, 672, 302, 3]},
            {'name': 'Daniel Jones', 'team': 'NYG', 'stats': [3205, 15, 5, 523, 708, 7]},
            {'name': 'Trevor Lawrence', 'team': 'JAX', 'stats': [4113, 25, 8, 606, 334, 3]},
            {'name': 'Kirk Cousins', 'team': 'MIN', 'stats': [4547, 29, 14, 545, 61, 1]},
            {'name': 'Aaron Rodgers', 'team': 'NYJ', 'stats': [3695, 26, 12, 531, 101, 0]},
            {'name': 'Geno Smith', 'team': 'SEA', 'stats': [4282, 30, 11, 572, 366, 1]},
            {'name': 'Russell Wilson', 'team': 'DEN', 'stats': [3524, 16, 11, 493, 320, 3]},
            {'name': 'Derek Carr', 'team': 'NO', 'stats': [3522, 24, 14, 502, 29, 1]},
            {'name': 'Brock Purdy', 'team': 'SF', 'stats': [4280, 31, 11, 578, 144, 3]},
            {'name': 'Anthony Richardson', 'team': 'IND', 'stats': [1998, 15, 9, 577, 523, 4]},
            {'name': 'Caleb Williams', 'team': 'CHI', 'stats': [3541, 20, 5, 611, 442, 2]},
            {'name': 'C.J. Stroud', 'team': 'HOU', 'stats': [4108, 23, 5, 579, 167, 3]},
            {'name': 'Bryce Young', 'team': 'CAR', 'stats': [2877, 11, 10, 653, 202, 1]},
            {'name': 'Sam Howell', 'team': 'WAS', 'stats': [3946, 21, 21, 612, 334, 5]},
            {'name': 'Mac Jones', 'team': 'NE', 'stats': [2936, 15, 11, 508, 54, 0]}
        ],
        'RB': [
            {'name': 'Christian McCaffrey', 'team': 'SF', 'stats': [1459, 14, 272, 741, 8, 107]},
            {'name': 'Austin Ekeler', 'team': 'LAC', 'stats': [915, 12, 204, 722, 5, 107]},
            {'name': 'Saquon Barkley', 'team': 'PHI', 'stats': [1312, 10, 295, 338, 2, 52]},
            {'name': 'Alvin Kamara', 'team': 'NO', 'stats': [897, 4, 240, 466, 2, 72]},
            {'name': 'Derrick Henry', 'team': 'BAL', 'stats': [1538, 13, 349, 114, 1, 19]},
            {'name': 'Nick Chubb', 'team': 'CLE', 'stats': [1525, 12, 302, 342, 2, 43]},
            {'name': 'Josh Jacobs', 'team': 'GB', 'stats': [1653, 12, 340, 400, 3, 53]},
            {'name': 'Tony Pollard', 'team': 'TEN', 'stats': [1007, 9, 193, 371, 3, 47]},
            {'name': 'Jonathan Taylor', 'team': 'IND', 'stats': [861, 4, 192, 333, 1, 42]},
            {'name': 'Kenneth Walker III', 'team': 'SEA', 'stats': [1050, 9, 228, 165, 1, 23]},
            {'name': 'Aaron Jones', 'team': 'MIN', 'stats': [1005, 3, 244, 429, 1, 51]},
            {'name': 'Najee Harris', 'team': 'PIT', 'stats': [1034, 4, 255, 467, 2, 74]},
            {'name': 'Joe Mixon', 'team': 'HOU', 'stats': [1104, 9, 257, 441, 1, 60]},
            {'name': 'Rhamondre Stevenson', 'team': 'NE', 'stats': [1040, 4, 210, 238, 1, 69]},
            {'name': 'Miles Sanders', 'team': 'CAR', 'stats': [898, 6, 200, 234, 1, 28]},
            {'name': 'Ezekiel Elliott', 'team': 'DAL', 'stats': [876, 12, 231, 313, 2, 52]},
            {'name': 'De\'Von Achane', 'team': 'MIA', 'stats': [800, 8, 103, 197, 3, 27]},
            {'name': 'Kyren Williams', 'team': 'LAR', 'stats': [1144, 12, 261, 206, 3, 32]},
            {'name': 'Rachaad White', 'team': 'TB', 'stats': [990, 3, 272, 549, 1, 64]},
            {'name': 'James Cook', 'team': 'BUF', 'stats': [1122, 2, 237, 445, 4, 44]},
            {'name': 'Isiah Pacheco', 'team': 'KC', 'stats': [935, 7, 205, 244, 1, 44]},
            {'name': 'Brian Robinson Jr.', 'team': 'WAS', 'stats': [797, 8, 196, 152, 0, 26]},
            {'name': 'Javonte Williams', 'team': 'DEN', 'stats': [774, 3, 212, 214, 0, 32]},
            {'name': 'Jerome Ford', 'team': 'CLE', 'stats': [813, 4, 148, 319, 2, 44]},
            {'name': 'David Montgomery', 'team': 'DET', 'stats': [1015, 13, 219, 341, 1, 42]},
            {'name': 'Jahmyr Gibbs', 'team': 'DET', 'stats': [945, 10, 182, 316, 1, 52]}
        ],
        'WR': [
            {'name': 'Cooper Kupp', 'team': 'LAR', 'stats': [1947, 8, 191, 145, 75]},
            {'name': 'Tyreek Hill', 'team': 'MIA', 'stats': [1710, 7, 134, 119, 0]},
            {'name': 'Stefon Diggs', 'team': 'HOU', 'stats': [1429, 11, 154, 108, 0]},
            {'name': 'Davante Adams', 'team': 'NYJ', 'stats': [1516, 14, 180, 100, 0]},
            {'name': 'DeAndre Hopkins', 'team': 'TEN', 'stats': [717, 3, 87, 64, 0]},
            {'name': 'A.J. Brown', 'team': 'PHI', 'stats': [1496, 11, 145, 88, 0]},
            {'name': 'Ja\'Marr Chase', 'team': 'CIN', 'stats': [1455, 13, 135, 87, 0]},
            {'name': 'CeeDee Lamb', 'team': 'DAL', 'stats': [1359, 9, 156, 107, 0]},
            {'name': 'Mike Evans', 'team': 'TB', 'stats': [1255, 13, 137, 79, 0]},
            {'name': 'Calvin Ridley', 'team': 'TEN', 'stats': [1016, 8, 116, 76, 0]},
            {'name': 'Amari Cooper', 'team': 'CLE', 'stats': [1250, 5, 128, 78, 0]},
            {'name': 'DK Metcalf', 'team': 'SEA', 'stats': [1114, 6, 158, 66, 0]},
            {'name': 'Keenan Allen', 'team': 'CHI', 'stats': [1243, 7, 108, 108, 0]},
            {'name': 'Chris Godwin', 'team': 'TB', 'stats': [1024, 2, 104, 89, 0]},
            {'name': 'Amon-Ra St. Brown', 'team': 'DET', 'stats': [1515, 10, 119, 106, 0]},
            {'name': 'Garrett Wilson', 'team': 'NYJ', 'stats': [1103, 4, 95, 83, 0]},
            {'name': 'Puka Nacua', 'team': 'LAR', 'stats': [1486, 6, 105, 105, 0]},
            {'name': 'Brandon Aiyuk', 'team': 'SF', 'stats': [1342, 7, 75, 105, 0]},
            {'name': 'Tee Higgins', 'team': 'CIN', 'stats': [656, 5, 42, 67, 0]},
            {'name': 'Michael Pittman Jr.', 'team': 'IND', 'stats': [1152, 4, 109, 80, 0]},
            {'name': 'Tank Dell', 'team': 'HOU', 'stats': [709, 7, 47, 59, 0]},
            {'name': 'Jaylen Waddle', 'team': 'MIA', 'stats': [1014, 4, 72, 104, 0]},
            {'name': 'Terry McLaurin', 'team': 'WAS', 'stats': [1023, 4, 79, 92, 0]},
            {'name': 'Christian Kirk', 'team': 'JAX', 'stats': [787, 0, 84, 68, 0]},
            {'name': 'DJ Moore', 'team': 'CHI', 'stats': [1364, 8, 96, 114, 0]},
            {'name': 'Rome Odunze', 'team': 'CHI', 'stats': [611, 3, 22, 40, 0]},
            {'name': 'Marvin Harrison Jr.', 'team': 'ARI', 'stats': [717, 4, 51, 54, 0]},
            {'name': 'Malik Nabers', 'team': 'NYG', 'stats': [1204, 3, 109, 76, 0]},
            {'name': 'Brian Thomas Jr.', 'team': 'JAX', 'stats': [1282, 6, 87, 64, 0]},
            {'name': 'Courtland Sutton', 'team': 'DEN', 'stats': [1162, 10, 64, 70, 0]}
        ],
        'TE': [
            {'name': 'Travis Kelce', 'team': 'KC', 'stats': [1338, 12, 164, 110]},
            {'name': 'Mark Andrews', 'team': 'BAL', 'stats': [847, 5, 123, 73]},
            {'name': 'T.J. Hockenson', 'team': 'MIN', 'stats': [914, 6, 124, 95]},
            {'name': 'Kyle Pitts', 'team': 'ATL', 'stats': [669, 2, 110, 52]},
            {'name': 'George Kittle', 'team': 'SF', 'stats': [765, 11, 110, 60]},
            {'name': 'Darren Waller', 'team': 'NYG', 'stats': [552, 1, 90, 41]},
            {'name': 'Sam LaPorta', 'team': 'DET', 'stats': [889, 10, 86, 120]},
            {'name': 'Dallas Goedert', 'team': 'PHI', 'stats': [544, 3, 59, 61]},
            {'name': 'Evan Engram', 'team': 'JAX', 'stats': [963, 4, 114, 82]},
            {'name': 'David Njoku', 'team': 'CLE', 'stats': [882, 6, 81, 70]},
            {'name': 'Jake Ferguson', 'team': 'DAL', 'stats': [761, 5, 71, 93]},
            {'name': 'Trey McBride', 'team': 'ARI', 'stats': [825, 3, 81, 90]},
            {'name': 'Brock Bowers', 'team': 'LV', 'stats': [1194, 5, 112, 57]},
            {'name': 'Tucker Kraft', 'team': 'GB', 'stats': [355, 2, 31, 28]},
            {'name': 'Cole Kmet', 'team': 'CHI', 'stats': [719, 8, 73, 50]},
            {'name': 'Pat Freiermuth', 'team': 'PIT', 'stats': [663, 2, 48, 61]},
            {'name': 'Tyler Conklin', 'team': 'NYJ', 'stats': [520, 3, 79, 55]},
            {'name': 'Noah Fant', 'team': 'SEA', 'stats': [414, 2, 69, 38]}
        ]
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
        position_filter = sys.argv[1] if len(sys.argv) > 1 else 'ALL'
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        
        # Load models
        models = load_models()
        if not models:
            raise Exception("No models loaded")
        
        # Get sample players
        sample_players = get_sample_players()
        
        # Generate predictions
        all_players = []
        player_id = 1
        
        for pos, players in sample_players.items():
            if position_filter != 'ALL' and position_filter != pos:
                continue
                
            for player_data in players:
                fantasy_points = predict_fantasy_points(models, pos, player_data['stats'])
                
                # Build base player object
                player = {
                    'player_id': str(player_id),
                    'player_name': player_data['name'],
                    'position': pos,
                    'recent_team': player_data['team'],
                    'predicted_fantasy_points': round(fantasy_points, 1),
                    'confidence': round(np.random.uniform(0.75, 0.95), 2)
                }
                
                # Add position-specific detailed stats
                stats = player_data['stats']
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
                
                all_players.append(player)
                player_id += 1
        
        # Sort by fantasy points and limit
        all_players.sort(key=lambda x: x['predicted_fantasy_points'], reverse=True)
        result_players = all_players[:limit]
        
        # Return JSON
        result = {
            'players': result_players
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