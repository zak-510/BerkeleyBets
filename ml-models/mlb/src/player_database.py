#!/usr/bin/env python3
"""
MLB Player Database
Comprehensive list of fantasy-relevant players across all positions
"""

from typing import List, Dict

def get_expanded_player_list() -> List[Dict]:
    """
    Get comprehensive list of 50+ top fantasy-relevant MLB players
    Balanced across all positions for model training
    """
    
    players = []
    
    # CATCHERS (3 players)
    catchers = [
        {'first_name': 'Salvador', 'last_name': 'Pérez', 'position': 'C', 'player_type': 'b', 'team': 'KC'},
        {'first_name': 'Will', 'last_name': 'Smith', 'position': 'C', 'player_type': 'b', 'team': 'LAD'},
        {'first_name': 'J.T.', 'last_name': 'Realmuto', 'position': 'C', 'player_type': 'b', 'team': 'PHI'}
    ]
    
    # FIRST BASEMEN (5 players)
    first_base = [
        {'first_name': 'Freddie', 'last_name': 'Freeman', 'position': '1B', 'player_type': 'b', 'team': 'LAD'},
        {'first_name': 'Vladimir', 'last_name': 'Guerrero Jr.', 'position': '1B', 'player_type': 'b', 'team': 'TOR'},
        {'first_name': 'Pete', 'last_name': 'Alonso', 'position': '1B', 'player_type': 'b', 'team': 'NYM'},
        {'first_name': 'Matt', 'last_name': 'Olson', 'position': '1B', 'player_type': 'b', 'team': 'ATL'},
        {'first_name': 'Paul', 'last_name': 'Goldschmidt', 'position': '1B', 'player_type': 'b', 'team': 'STL'}
    ]
    
    # SECOND BASEMEN (5 players)
    second_base = [
        {'first_name': 'José', 'last_name': 'Altuve', 'position': '2B', 'player_type': 'b', 'team': 'HOU'},
        {'first_name': 'Gleyber', 'last_name': 'Torres', 'position': '2B', 'player_type': 'b', 'team': 'NYY'},
        {'first_name': 'Marcus', 'last_name': 'Semien', 'position': '2B', 'player_type': 'b', 'team': 'TEX'},
        {'first_name': 'Jazz', 'last_name': 'Chisholm Jr.', 'position': '2B', 'player_type': 'b', 'team': 'MIA'},
        {'first_name': 'Ozzie', 'last_name': 'Albies', 'position': '2B', 'player_type': 'b', 'team': 'ATL'}
    ]
    
    # THIRD BASEMEN (5 players)
    third_base = [
        {'first_name': 'Manny', 'last_name': 'Machado', 'position': '3B', 'player_type': 'b', 'team': 'SD'},
        {'first_name': 'Rafael', 'last_name': 'Devers', 'position': '3B', 'player_type': 'b', 'team': 'BOS'},
        {'first_name': 'Nolan', 'last_name': 'Arenado', 'position': '3B', 'player_type': 'b', 'team': 'STL'},
        {'first_name': 'Austin', 'last_name': 'Riley', 'position': '3B', 'player_type': 'b', 'team': 'ATL'},
        {'first_name': 'José', 'last_name': 'Ramírez', 'position': '3B', 'player_type': 'b', 'team': 'CLE'}
    ]
    
    # SHORTSTOPS (5 players)
    shortstops = [
        {'first_name': 'Trea', 'last_name': 'Turner', 'position': 'SS', 'player_type': 'b', 'team': 'PHI'},
        {'first_name': 'Francisco', 'last_name': 'Lindor', 'position': 'SS', 'player_type': 'b', 'team': 'NYM'},
        {'first_name': 'Fernando', 'last_name': 'Tatis Jr.', 'position': 'SS', 'player_type': 'b', 'team': 'SD'},
        {'first_name': 'Corey', 'last_name': 'Seager', 'position': 'SS', 'player_type': 'b', 'team': 'TEX'},
        {'first_name': 'Bo', 'last_name': 'Bichette', 'position': 'SS', 'player_type': 'b', 'team': 'TOR'}
    ]
    
    # OUTFIELDERS (15 players)
    outfielders = [
        {'first_name': 'Aaron', 'last_name': 'Judge', 'position': 'OF', 'player_type': 'b', 'team': 'NYY'},
        {'first_name': 'Mookie', 'last_name': 'Betts', 'position': 'OF', 'player_type': 'b', 'team': 'LAD'},
        {'first_name': 'Ronald', 'last_name': 'Acuña Jr.', 'position': 'OF', 'player_type': 'b', 'team': 'ATL'},
        {'first_name': 'Mike', 'last_name': 'Trout', 'position': 'OF', 'player_type': 'b', 'team': 'LAA'},
        {'first_name': 'Juan', 'last_name': 'Soto', 'position': 'OF', 'player_type': 'b', 'team': 'NYY'},
        {'first_name': 'Kyle', 'last_name': 'Tucker', 'position': 'OF', 'player_type': 'b', 'team': 'HOU'},
        {'first_name': 'Yordan', 'last_name': 'Alvarez', 'position': 'OF', 'player_type': 'b', 'team': 'HOU'},
        {'first_name': 'George', 'last_name': 'Springer', 'position': 'OF', 'player_type': 'b', 'team': 'TOR'},
        {'first_name': 'Cody', 'last_name': 'Bellinger', 'position': 'OF', 'player_type': 'b', 'team': 'CHC'},
        {'first_name': 'Randy', 'last_name': 'Arozarena', 'position': 'OF', 'player_type': 'b', 'team': 'TB'},
        {'first_name': 'Byron', 'last_name': 'Buxton', 'position': 'OF', 'player_type': 'b', 'team': 'MIN'},
        {'first_name': 'Jesse', 'last_name': 'Winker', 'position': 'OF', 'player_type': 'b', 'team': 'MIL'},
        {'first_name': 'Teoscar', 'last_name': 'Hernández', 'position': 'OF', 'player_type': 'b', 'team': 'LAD'},
        {'first_name': 'Christian', 'last_name': 'Yelich', 'position': 'OF', 'player_type': 'b', 'team': 'MIL'},
        {'first_name': 'Luis', 'last_name': 'Robert Jr.', 'position': 'OF', 'player_type': 'b', 'team': 'CHW'}
    ]
    
    # PITCHERS (15 players - mix of starters and closers)
    pitchers = [
        # Elite Starters
        {'first_name': 'Gerrit', 'last_name': 'Cole', 'position': 'P', 'player_type': 'p', 'team': 'NYY'},
        {'first_name': 'Jacob', 'last_name': 'deGrom', 'position': 'P', 'player_type': 'p', 'team': 'TEX'},
        {'first_name': 'Shane', 'last_name': 'Bieber', 'position': 'P', 'player_type': 'p', 'team': 'CLE'},
        {'first_name': 'Spencer', 'last_name': 'Strider', 'position': 'P', 'player_type': 'p', 'team': 'ATL'},
        {'first_name': 'Sandy', 'last_name': 'Alcantara', 'position': 'P', 'player_type': 'p', 'team': 'MIA'},
        {'first_name': 'Corbin', 'last_name': 'Burnes', 'position': 'P', 'player_type': 'p', 'team': 'BAL'},
        {'first_name': 'Tyler', 'last_name': 'Glasnow', 'position': 'P', 'player_type': 'p', 'team': 'LAD'},
        {'first_name': 'Zac', 'last_name': 'Gallen', 'position': 'P', 'player_type': 'p', 'team': 'ARI'},
        {'first_name': 'Logan', 'last_name': 'Webb', 'position': 'P', 'player_type': 'p', 'team': 'SF'},
        {'first_name': 'Pablo', 'last_name': 'López', 'position': 'P', 'player_type': 'p', 'team': 'MIN'},
        
        # Elite Closers
        {'first_name': 'Edwin', 'last_name': 'Díaz', 'position': 'P', 'player_type': 'p', 'team': 'NYM'},
        {'first_name': 'Josh', 'last_name': 'Hader', 'position': 'P', 'player_type': 'p', 'team': 'HOU'},
        {'first_name': 'Emmanuel', 'last_name': 'Clase', 'position': 'P', 'player_type': 'p', 'team': 'CLE'},
        {'first_name': 'Félix', 'last_name': 'Bautista', 'position': 'P', 'player_type': 'p', 'team': 'BAL'},
        {'first_name': 'Ryan', 'last_name': 'Helsley', 'position': 'P', 'player_type': 'p', 'team': 'STL'}
    ]
    
    # Combine all players
    players.extend(catchers)
    players.extend(first_base)
    players.extend(second_base)
    players.extend(third_base)
    players.extend(shortstops)
    players.extend(outfielders)
    players.extend(pitchers)
    
    return players

def get_position_distribution(players: List[Dict]) -> Dict:
    """Get distribution of players by position"""
    distribution = {}
    for player in players:
        pos = player['position']
        if pos not in distribution:
            distribution[pos] = 0
        distribution[pos] += 1
    return distribution

def get_players_by_position(players: List[Dict], position: str) -> List[Dict]:
    """Get all players for a specific position"""
    return [p for p in players if p['position'] == position]

def validate_player_database() -> Dict:
    """Validate the player database structure and coverage"""
    players = get_expanded_player_list()
    distribution = get_position_distribution(players)
    
    validation_report = {
        'total_players': len(players),
        'position_distribution': distribution,
        'target_met': {},
        'issues': []
    }
    
    # Check against targets
    targets = {'C': 3, '1B': 5, '2B': 5, '3B': 5, 'SS': 5, 'OF': 15, 'P': 15}
    
    for pos, target in targets.items():
        actual = distribution.get(pos, 0)
        validation_report['target_met'][pos] = actual >= target
        if actual < target:
            validation_report['issues'].append(f"{pos}: {actual}/{target} players")
    
    # Check for required fields
    required_fields = ['first_name', 'last_name', 'position', 'player_type', 'team']
    for i, player in enumerate(players):
        for field in required_fields:
            if field not in player:
                validation_report['issues'].append(f"Player {i}: Missing {field}")
    
    return validation_report

if __name__ == "__main__":
    print("🧪 VALIDATING PLAYER DATABASE")
    print("=" * 50)
    
    players = get_expanded_player_list()
    validation = validate_player_database()
    
    print(f"📊 PLAYER DATABASE SUMMARY:")
    print(f"Total Players: {validation['total_players']}")
    print(f"\nPosition Distribution:")
    for pos, count in validation['position_distribution'].items():
        target = {'C': 3, '1B': 5, '2B': 5, '3B': 5, 'SS': 5, 'OF': 15, 'P': 15}.get(pos, 0)
        status = "✅" if count >= target else "❌"
        print(f"  {pos}: {count}/{target} {status}")
    
    if validation['issues']:
        print(f"\n⚠️ Issues Found:")
        for issue in validation['issues']:
            print(f"  • {issue}")
    else:
        print(f"\n✅ Player database validation passed!")
    
    print(f"\n📋 Sample Players:")
    for pos in ['C', '1B', 'OF', 'P']:
        pos_players = get_players_by_position(players, pos)
        if pos_players:
            sample = pos_players[0]
            print(f"  {pos}: {sample['first_name']} {sample['last_name']} ({sample['team']})") 