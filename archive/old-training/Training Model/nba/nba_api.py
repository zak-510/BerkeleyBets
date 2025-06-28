from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Load the inference results once at startup
def load_data():
    try:
        df = pd.read_csv('inference_results_fixed.csv')
        print(f"✅ Loaded {len(df)} NBA player records from inference_results_fixed.csv")
        print(f"👥 Unique players: {df['player_name'].nunique()}")
        
        # Aggregate data by player - take the mean of all games for each player
        aggregated_df = df.groupby(['player_name', 'position']).agg({
            'actual_pts': 'mean',
            'actual_reb': 'mean', 
            'actual_ast': 'mean',
            'actual_fantasy_points': 'mean',
            'predicted_pts': 'mean',
            'predicted_reb': 'mean',
            'predicted_ast': 'mean',
            'predicted_fantasy_points': 'mean'
        }).reset_index()
        
        # Round to 1 decimal place for cleaner display
        numeric_cols = ['actual_pts', 'actual_reb', 'actual_ast', 'actual_fantasy_points',
                       'predicted_pts', 'predicted_reb', 'predicted_ast', 'predicted_fantasy_points']
        for col in numeric_cols:
            aggregated_df[col] = aggregated_df[col].round(1)
        
        print(f"📊 Aggregated to {len(aggregated_df)} unique players")
        return aggregated_df
    except FileNotFoundError:
        print("❌ inference_results_fixed.csv not found. Please run the NBA model first.")
        return pd.DataFrame()

# Global variable to store data
nba_data = load_data()

@app.route('/api/players', methods=['GET'])
def get_all_players():
    """Get all NBA players with predictions"""
    if nba_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    # Convert to list of dictionaries
    players = []
    for _, row in nba_data.iterrows():
        player = {
            'name': row['player_name'],
            'position': row['position'],
            'actualPoints': float(row['actual_pts']),
            'actualRebounds': float(row['actual_reb']),
            'actualAssists': float(row['actual_ast']),
            'actualFantasyPoints': float(row['actual_fantasy_points']),
            'predictedPoints': float(row['predicted_pts']),
            'predictedRebounds': float(row['predicted_reb']),
            'predictedAssists': float(row['predicted_ast']),
            'predictedFantasyPoints': float(row['predicted_fantasy_points']),
            'pointsAccuracy': calculate_accuracy(row['actual_pts'], row['predicted_pts']),
            'reboundsAccuracy': calculate_accuracy(row['actual_reb'], row['predicted_reb']),
            'assistsAccuracy': calculate_accuracy(row['actual_ast'], row['predicted_ast']),
            'overallAccuracy': calculate_accuracy(row['actual_fantasy_points'], row['predicted_fantasy_points'])
        }
        players.append(player)
    
    return jsonify({
        'players': players,
        'total': len(players),
        'positions': list(nba_data['position'].unique())
    })

@app.route('/api/players/<position>', methods=['GET'])
def get_players_by_position(position):
    """Get players filtered by position"""
    if nba_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    position_data = nba_data[nba_data['position'].str.upper() == position.upper()]
    
    if position_data.empty:
        return jsonify({'error': f'No players found for position: {position}'}), 404
    
    players = []
    for _, row in position_data.iterrows():
        player = {
            'name': row['player_name'],
            'position': row['position'],
            'actualPoints': float(row['actual_pts']),
            'actualRebounds': float(row['actual_reb']),
            'actualAssists': float(row['actual_ast']),
            'actualFantasyPoints': float(row['actual_fantasy_points']),
            'predictedPoints': float(row['predicted_pts']),
            'predictedRebounds': float(row['predicted_reb']),
            'predictedAssists': float(row['predicted_ast']),
            'predictedFantasyPoints': float(row['predicted_fantasy_points']),
            'pointsAccuracy': calculate_accuracy(row['actual_pts'], row['predicted_pts']),
            'reboundsAccuracy': calculate_accuracy(row['actual_reb'], row['predicted_reb']),
            'assistsAccuracy': calculate_accuracy(row['actual_ast'], row['predicted_ast']),
            'overallAccuracy': calculate_accuracy(row['actual_fantasy_points'], row['predicted_fantasy_points'])
        }
        players.append(player)
    
    # Sort by predicted fantasy points descending
    players.sort(key=lambda x: x['predictedFantasyPoints'], reverse=True)
    
    return jsonify({
        'players': players,
        'total': len(players),
        'position': position.upper()
    })

@app.route('/api/player/<player_name>', methods=['GET'])
def get_player_by_name(player_name):
    """Get specific player by name"""
    if nba_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    # Case-insensitive search
    player_data = nba_data[nba_data['player_name'].str.contains(player_name, case=False, na=False)]
    
    if player_data.empty:
        return jsonify({'error': f'Player not found: {player_name}'}), 404
    
    # If multiple matches, return the first one
    row = player_data.iloc[0]
    
    player = {
        'name': row['player_name'],
        'position': row['position'],
        'actualPoints': float(row['actual_pts']),
        'actualRebounds': float(row['actual_reb']),
        'actualAssists': float(row['actual_ast']),
        'actualFantasyPoints': float(row['actual_fantasy_points']),
        'predictedPoints': float(row['predicted_pts']),
        'predictedRebounds': float(row['predicted_reb']),
        'predictedAssists': float(row['predicted_ast']),
        'predictedFantasyPoints': float(row['predicted_fantasy_points']),
        'pointsAccuracy': calculate_accuracy(row['actual_pts'], row['predicted_pts']),
        'reboundsAccuracy': calculate_accuracy(row['actual_reb'], row['predicted_reb']),
        'assistsAccuracy': calculate_accuracy(row['actual_ast'], row['predicted_ast']),
        'overallAccuracy': calculate_accuracy(row['actual_fantasy_points'], row['predicted_fantasy_points'])
    }
    
    return jsonify({'player': player})

@app.route('/api/search', methods=['GET'])
def search_players():
    """Search players by name (fuzzy search)"""
    if nba_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    # Case-insensitive partial match
    matches = nba_data[nba_data['player_name'].str.contains(query, case=False, na=False)]
    
    players = []
    for _, row in matches.iterrows():
        player = {
            'name': row['player_name'],
            'position': row['position'],
            'actualPoints': float(row['actual_pts']),
            'actualRebounds': float(row['actual_reb']),
            'actualAssists': float(row['actual_ast']),
            'actualFantasyPoints': float(row['actual_fantasy_points']),
            'predictedPoints': float(row['predicted_pts']),
            'predictedRebounds': float(row['predicted_reb']),
            'predictedAssists': float(row['predicted_ast']),
            'predictedFantasyPoints': float(row['predicted_fantasy_points']),
            'pointsAccuracy': calculate_accuracy(row['actual_pts'], row['predicted_pts']),
            'reboundsAccuracy': calculate_accuracy(row['actual_reb'], row['predicted_reb']),
            'assistsAccuracy': calculate_accuracy(row['actual_ast'], row['predicted_ast']),
            'overallAccuracy': calculate_accuracy(row['actual_fantasy_points'], row['predicted_fantasy_points'])
        }
        players.append(player)
    
    # Sort by predicted fantasy points descending
    players.sort(key=lambda x: x['predictedFantasyPoints'], reverse=True)
    
    return jsonify({
        'players': players[:20],  # Limit to top 20 results
        'total': len(players),
        'query': query
    })

@app.route('/api/stats', methods=['GET'])
def get_model_stats():
    """Get overall model performance statistics"""
    if nba_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    # Calculate overall stats for each stat category
    pts_mae = np.mean(np.abs(nba_data['actual_pts'] - nba_data['predicted_pts']))
    reb_mae = np.mean(np.abs(nba_data['actual_reb'] - nba_data['predicted_reb']))
    ast_mae = np.mean(np.abs(nba_data['actual_ast'] - nba_data['predicted_ast']))
    fantasy_mae = np.mean(np.abs(nba_data['actual_fantasy_points'] - nba_data['predicted_fantasy_points']))
    
    # Calculate R² for each category
    def calculate_r2(actual, predicted):
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    pts_r2 = calculate_r2(nba_data['actual_pts'], nba_data['predicted_pts'])
    reb_r2 = calculate_r2(nba_data['actual_reb'], nba_data['predicted_reb'])
    ast_r2 = calculate_r2(nba_data['actual_ast'], nba_data['predicted_ast'])
    fantasy_r2 = calculate_r2(nba_data['actual_fantasy_points'], nba_data['predicted_fantasy_points'])
    
    # Position-specific stats
    position_stats = {}
    for position in nba_data['position'].unique():
        pos_data = nba_data[nba_data['position'] == position]
        
        position_stats[position] = {
            'pointsMAE': float(np.mean(np.abs(pos_data['actual_pts'] - pos_data['predicted_pts']))),
            'reboundsMAE': float(np.mean(np.abs(pos_data['actual_reb'] - pos_data['predicted_reb']))),
            'assistsMAE': float(np.mean(np.abs(pos_data['actual_ast'] - pos_data['predicted_ast']))),
            'fantasyMAE': float(np.mean(np.abs(pos_data['actual_fantasy_points'] - pos_data['predicted_fantasy_points']))),
            'playerCount': len(pos_data)
        }
    
    return jsonify({
        'overall': {
            'pointsMAE': float(pts_mae),
            'reboundsMAE': float(reb_mae),
            'assistsMAE': float(ast_mae),
            'fantasyMAE': float(fantasy_mae),
            'pointsR2': float(pts_r2),
            'reboundsR2': float(reb_r2),
            'assistsR2': float(ast_r2),
            'fantasyR2': float(fantasy_r2),
            'totalPlayers': len(nba_data)
        },
        'byPosition': position_stats
    })

@app.route('/api/top/<position>/<int:limit>', methods=['GET'])
def get_top_players(position, limit=10):
    """Get top N players by position based on predicted fantasy points"""
    if nba_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    if position.upper() == 'ALL':
        position_data = nba_data
    else:
        position_data = nba_data[nba_data['position'].str.upper() == position.upper()]
    
    if position_data.empty:
        return jsonify({'error': f'No players found for position: {position}'}), 404
    
    # Sort by predicted fantasy points and get top N
    top_players = position_data.nlargest(limit, 'predicted_fantasy_points')
    
    players = []
    for _, row in top_players.iterrows():
        player = {
            'name': row['player_name'],
            'position': row['position'],
            'actualPoints': float(row['actual_pts']),
            'actualRebounds': float(row['actual_reb']),
            'actualAssists': float(row['actual_ast']),
            'actualFantasyPoints': float(row['actual_fantasy_points']),
            'predictedPoints': float(row['predicted_pts']),
            'predictedRebounds': float(row['predicted_reb']),
            'predictedAssists': float(row['predicted_ast']),
            'predictedFantasyPoints': float(row['predicted_fantasy_points']),
            'pointsAccuracy': calculate_accuracy(row['actual_pts'], row['predicted_pts']),
            'reboundsAccuracy': calculate_accuracy(row['actual_reb'], row['predicted_reb']),
            'assistsAccuracy': calculate_accuracy(row['actual_ast'], row['predicted_ast']),
            'overallAccuracy': calculate_accuracy(row['actual_fantasy_points'], row['predicted_fantasy_points'])
        }
        players.append(player)
    
    return jsonify({
        'players': players,
        'total': len(players),
        'position': position.upper(),
        'limit': limit
    })

def calculate_accuracy(actual, predicted):
    """Calculate accuracy percentage"""
    if actual == 0:
        return 0.0
    error_pct = abs(actual - predicted) / actual * 100
    accuracy = max(0, 100 - error_pct)
    return round(accuracy, 1)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'dataLoaded': not nba_data.empty,
        'playerCount': len(nba_data) if not nba_data.empty else 0,
        'uniquePlayers': nba_data['player_name'].nunique() if not nba_data.empty else 0
    })

if __name__ == '__main__':
    print("🏀 Starting NBA Predictions API...")
    print(f"📊 Loaded {len(nba_data)} player records")
    if not nba_data.empty:
        print(f"👥 Unique players: {nba_data['player_name'].nunique()}")
    print("🚀 API running on http://localhost:8081")
    print("\nAvailable endpoints:")
    print("  GET /api/players - All players")
    print("  GET /api/players/<position> - Players by position")
    print("  GET /api/player/<name> - Specific player")
    print("  GET /api/search?q=<query> - Search players")
    print("  GET /api/stats - Model statistics")
    print("  GET /api/top/<position>/<limit> - Top N players")
    print("  GET /api/health - Health check")
    
    app.run(debug=False, host='127.0.0.1', port=8081) 