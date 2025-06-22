#!/usr/bin/env python3

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variable to store loaded data
mlb_data = {
    'batters': pd.DataFrame(),
    'pitchers': pd.DataFrame(),
    'all_players': pd.DataFrame()
}

def load_mlb_data():
    """Load MLB prediction data from CSV files"""
    try:
        results_dir = 'results'
        
        # Load batter data from complete analysis
        batter_file = os.path.join(results_dir, 'complete_analysis_final.csv')
        if os.path.exists(batter_file):
            batters_df = pd.read_csv(batter_file)
            logger.info(f"Loaded {len(batters_df)} batters from complete analysis")
        else:
            logger.warning(f"Batter file not found: {batter_file}")
            batters_df = pd.DataFrame()
        
        # Load pitcher data with individual stats
        pitcher_file = os.path.join(results_dir, 'pitcher_individual_stats.csv')
        if os.path.exists(pitcher_file):
            pitchers_df = pd.read_csv(pitcher_file)
            logger.info(f"Loaded {len(pitchers_df)} pitchers from individual stats")
        else:
            logger.warning(f"Pitcher file not found: {pitcher_file}")
            pitchers_df = pd.DataFrame()
        
        # Store in global variable
        mlb_data['batters'] = batters_df
        mlb_data['pitchers'] = pitchers_df
        
        logger.info(f"Successfully loaded MLB data: {len(batters_df)} batters, {len(pitchers_df)} pitchers")
        return True
        
    except Exception as e:
        logger.error(f"Error loading MLB data: {str(e)}")
        return False

def format_batter_for_api(row):
    """Format batter data for API response"""
    # Calculate projected stats from rates and base values
    batting_avg = row.get('estimated_batting_avg', 0.0)
    on_base_pct = row.get('estimated_on_base_pct', 0.0)
    slugging_pct = row.get('estimated_slugging_pct', 0.0)
    
    # Estimate hits, runs, RBIs based on rates (simplified calculation)
    estimated_at_bats = 500  # Typical season at-bats
    projected_hits = max(1, int(batting_avg * estimated_at_bats))
    projected_runs = max(1, int(on_base_pct * estimated_at_bats * 0.8))
    projected_rbis = max(1, int(slugging_pct * estimated_at_bats * 0.6))
    
    return {
        'name': row['player_name'],
        'position': row['position'],
        'playerType': row.get('player_type', 'batter'),
        'predictedFantasyPoints': round(row.get('predicted_fantasy_points', 0.0), 2),
        'fantasyConfidence': round(row.get('fantasy_confidence', 0.0), 2),
        'projectedHits': projected_hits,
        'projectedRuns': projected_runs,
        'projectedRBIs': projected_rbis,
        'battingAvg': round(batting_avg, 3),
        'onBasePct': round(on_base_pct, 3),
        'sluggingPct': round(slugging_pct, 3),
        'skillConfidence': round(row.get('skill_confidence', 0.0), 2)
    }

def format_pitcher_for_api(row):
    """Format pitcher data for API response"""
    return {
        'name': row['player_name'],
        'position': row['position'],
        'playerType': 'pitcher',
        'predictedFantasyPoints': round(row.get('predicted_fantasy_points', 0.0), 2),
        'fantasyConfidence': round(row.get('fantasy_confidence', 0.0), 2),
        'projectedStrikeouts': int(row.get('predicted_strikeouts', 0)),
        'projectedInningsPitched': round(row.get('predicted_innings_pitched', 0.0), 1),
        'strikeoutsConfidence': round(row.get('predicted_strikeouts_confidence', 0.0), 2),
        'inningsPitchedConfidence': round(row.get('predicted_innings_pitched_confidence', 0.0), 2)
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MLB Prediction API',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': len(mlb_data['batters']) > 0 or len(mlb_data['pitchers']) > 0,
        'batters': len(mlb_data['batters']),
        'pitchers': len(mlb_data['pitchers'])
    })

@app.route('/api/players', methods=['GET'])
def get_all_players():
    """Get all MLB players"""
    try:
        players = []
        seen_players = set()
        
        # Process batters
        for _, row in mlb_data['batters'].iterrows():
            player_name = row['player_name']
            if player_name not in seen_players:
                players.append(format_batter_for_api(row))
                seen_players.add(player_name)
        
        # Process pitchers
        for _, row in mlb_data['pitchers'].iterrows():
            player_name = row['player_name']
            if player_name not in seen_players:
                players.append(format_pitcher_for_api(row))
                seen_players.add(player_name)
        
        return jsonify({
            'players': players,
            'total': len(players),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in get_all_players: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/<position>', methods=['GET'])
def get_players_by_position(position):
    """Get players by position"""
    try:
        position = position.upper()
        players = []
        seen_players = set()
        
        if position == 'P':
            # Return pitchers
            for _, row in mlb_data['pitchers'].iterrows():
                player_name = row['player_name']
                if row['position'] == position and player_name not in seen_players:
                    players.append(format_pitcher_for_api(row))
                    seen_players.add(player_name)
        else:
            # Return batters for specific position
            for _, row in mlb_data['batters'].iterrows():
                player_name = row['player_name']
                if row['position'] == position and player_name not in seen_players:
                    players.append(format_batter_for_api(row))
                    seen_players.add(player_name)
        
        return jsonify({
            'players': players,
            'position': position,
            'total': len(players),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in get_players_by_position: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_players():
    """Search players by name"""
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({'error': 'Query parameter q is required'}), 400
        
        players = []
        seen_players = set()
        
        # Search batters
        for _, row in mlb_data['batters'].iterrows():
            player_name = row['player_name']
            if query in player_name.lower() and player_name not in seen_players:
                players.append(format_batter_for_api(row))
                seen_players.add(player_name)
        
        # Search pitchers
        for _, row in mlb_data['pitchers'].iterrows():
            player_name = row['player_name']
            if query in player_name.lower() and player_name not in seen_players:
                players.append(format_pitcher_for_api(row))
                seen_players.add(player_name)
        
        return jsonify({
            'players': players,
            'query': query,
            'total': len(players),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in search_players: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/top/<position>/<int:limit>', methods=['GET'])
def get_top_players(position, limit=20):
    """Get top players by position based on fantasy points"""
    try:
        position = position.upper()
        players = []
        seen_players = set()
        
        if position == 'ALL':
            # Get top players from both batters and pitchers
            all_data = []
            
            # Add batters
            for _, row in mlb_data['batters'].iterrows():
                player_name = row['player_name']
                if player_name not in seen_players:
                    all_data.append((row, 'batter'))
                    seen_players.add(player_name)
            
            # Add pitchers
            seen_players.clear()
            for _, row in mlb_data['pitchers'].iterrows():
                player_name = row['player_name']
                if player_name not in seen_players:
                    all_data.append((row, 'pitcher'))
                    seen_players.add(player_name)
            
            # Sort by fantasy points
            all_data.sort(key=lambda x: x[0].get('predicted_fantasy_points', 0), reverse=True)
            
            # Format top players
            for row, player_type in all_data[:limit]:
                if player_type == 'pitcher':
                    players.append(format_pitcher_for_api(row))
                else:
                    players.append(format_batter_for_api(row))
                    
        elif position == 'P':
            # Get top pitchers
            pitcher_data = list(mlb_data['pitchers'].iterrows())
            pitcher_data.sort(key=lambda x: x[1].get('predicted_fantasy_points', 0), reverse=True)
            
            for _, row in pitcher_data[:limit]:
                player_name = row['player_name']
                if player_name not in seen_players:
                    players.append(format_pitcher_for_api(row))
                    seen_players.add(player_name)
        else:
            # Get top batters for specific position
            position_data = []
            for _, row in mlb_data['batters'].iterrows():
                if row['position'] == position:
                    position_data.append(row)
            
            position_data.sort(key=lambda x: x.get('predicted_fantasy_points', 0), reverse=True)
            
            for row in position_data[:limit]:
                player_name = row['player_name']
                if player_name not in seen_players:
                    players.append(format_batter_for_api(row))
                    seen_players.add(player_name)
        
        return jsonify({
            'players': players,
            'position': position,
            'limit': limit,
            'total': len(players),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in get_top_players: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_model_stats():
    """Get model statistics"""
    try:
        batter_count = len(mlb_data['batters'])
        pitcher_count = len(mlb_data['pitchers'])
        total_count = batter_count + pitcher_count
        
        # Calculate some basic stats
        avg_fantasy_points_batters = mlb_data['batters']['predicted_fantasy_points'].mean() if batter_count > 0 else 0
        avg_fantasy_points_pitchers = mlb_data['pitchers']['predicted_fantasy_points'].mean() if pitcher_count > 0 else 0
        
        return jsonify({
            'totalPlayers': total_count,
            'batters': batter_count,
            'pitchers': pitcher_count,
            'avgFantasyPointsBatters': round(avg_fantasy_points_batters, 2),
            'avgFantasyPointsPitchers': round(avg_fantasy_points_pitchers, 2),
            'positions': {
                'batters': list(mlb_data['batters']['position'].unique()) if batter_count > 0 else [],
                'pitchers': ['P']
            },
            'dataLastUpdated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in get_model_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting MLB Prediction API...")
    print("Loading MLB data...")
    
    if load_mlb_data():
        print(f"Successfully loaded data")
        print("Starting server on http://localhost:8082")
        app.run(host='0.0.0.0', port=8082, debug=True)
    else:
        print("Failed to load MLB data. Please check the results directory.")
        exit(1) 