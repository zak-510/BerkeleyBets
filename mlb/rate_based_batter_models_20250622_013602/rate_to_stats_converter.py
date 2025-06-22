
def convert_rates_to_game_stats(rates, plate_appearances=4.0, at_bats=3.5):
    """Convert predicted rates to expected per-game stats"""
    game_stats = {}
    
    # Hits per game
    game_stats['hits'] = max(0, round(rates.get('batting_avg', 0.250) * at_bats))
    
    # Walks per game  
    game_stats['walks'] = max(0, round(rates.get('walk_rate', 0.08) * plate_appearances))
    
    # Strikeouts per game
    game_stats['strikeouts'] = max(0, round(rates.get('strikeout_rate', 0.20) * plate_appearances))
    
    # Home runs per game
    game_stats['home_runs'] = max(0, round(rates.get('home_run_rate', 0.03) * at_bats))
    
    # Stolen bases per game (rare)
    game_stats['stolen_bases'] = max(0, round(rates.get('steal_rate', 0.05)))
    
    # Estimate other stats from hits and performance
    hits = game_stats['hits']
    slg = rates.get('slugging_pct', 0.400)
    avg = rates.get('batting_avg', 0.250)
    
    # Doubles (typically 20-25% of hits for average players)
    game_stats['doubles'] = max(0, round(hits * 0.22))
    
    # Triples (very rare, ~1% of hits)
    game_stats['triples'] = 1 if hits >= 3 and np.random.random() < 0.01 else 0
    
    # Runs and RBIs (correlated with overall offensive performance)
    ops = rates.get('on_base_pct', 0.320) + slg
    if ops >= 0.850:
        run_rbi_factor = 1.2
    elif ops >= 0.750:
        run_rbi_factor = 1.0
    else:
        run_rbi_factor = 0.8
    
    game_stats['runs'] = max(0, round((hits + game_stats['walks']) * 0.3 * run_rbi_factor))
    game_stats['rbis'] = max(0, round(hits * 0.4 * run_rbi_factor))
    
    return game_stats
