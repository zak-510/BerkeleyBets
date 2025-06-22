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
        df = pd.read_csv('inference_results.csv')
        print(f"✅ Loaded {len(df)} players from inference_results.csv")
        return df
    except FileNotFoundError:
        print("❌ inference_results.csv not found. Please run the NFL model first.")
        return pd.DataFrame()

# Global variable to store data
nfl_data = load_data()

@app.route('/api/players', methods=['GET'])
def get_all_players():
    """Get all NFL players with predictions"""
    if nfl_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    # Convert to list of dictionaries
    players = []
    for _, row in nfl_data.iterrows():
        player = {
            'name': row['player_name'],
            'position': row['position'],
            'actualPoints': float(row['actual_points']),
            'predictedPoints': float(row['predicted_points']),
            'confidence': calculate_confidence(row['actual_points'], row['predicted_points']),
            'error': float(abs(row['actual_points'] - row['predicted_points'])),
            'accuracy': calculate_accuracy(row['actual_points'], row['predicted_points'])
        }
        players.append(player)
    
    return jsonify({
        'players': players,
        'total': len(players),
        'positions': list(nfl_data['position'].unique())
    })

@app.route('/api/players/<position>', methods=['GET'])
def get_players_by_position(position):
    """Get players filtered by position"""
    if nfl_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    position_data = nfl_data[nfl_data['position'].str.upper() == position.upper()]
    
    if position_data.empty:
        return jsonify({'error': f'No players found for position: {position}'}), 404
    
    players = []
    for _, row in position_data.iterrows():
        player = {
            'name': row['player_name'],
            'position': row['position'],
            'actualPoints': float(row['actual_points']),
            'predictedPoints': float(row['predicted_points']),
            'confidence': calculate_confidence(row['actual_points'], row['predicted_points']),
            'error': float(abs(row['actual_points'] - row['predicted_points'])),
            'accuracy': calculate_accuracy(row['actual_points'], row['predicted_points'])
        }
        players.append(player)
    
    # Sort by predicted points descending
    players.sort(key=lambda x: x['predictedPoints'], reverse=True)
    
    return jsonify({
        'players': players,
        'total': len(players),
        'position': position.upper()
    })

@app.route('/api/player/<player_name>', methods=['GET'])
def get_player_by_name(player_name):
    """Get specific player by name"""
    if nfl_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    # Case-insensitive search
    player_data = nfl_data[nfl_data['player_name'].str.contains(player_name, case=False, na=False)]
    
    if player_data.empty:
        return jsonify({'error': f'Player not found: {player_name}'}), 404
    
    # If multiple matches, return the first one
    row = player_data.iloc[0]
    
    player = {
        'name': row['player_name'],
        'position': row['position'],
        'actualPoints': float(row['actual_points']),
        'predictedPoints': float(row['predicted_points']),
        'confidence': calculate_confidence(row['actual_points'], row['predicted_points']),
        'error': float(abs(row['actual_points'] - row['predicted_points'])),
        'accuracy': calculate_accuracy(row['actual_points'], row['predicted_points'])
    }
    
    return jsonify({'player': player})

@app.route('/api/search', methods=['GET'])
def search_players():
    """Search players by name (fuzzy search)"""
    if nfl_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    # Case-insensitive partial match
    matches = nfl_data[nfl_data['player_name'].str.contains(query, case=False, na=False)]
    
    players = []
    for _, row in matches.iterrows():
        player = {
            'name': row['player_name'],
            'position': row['position'],
            'actualPoints': float(row['actual_points']),
            'predictedPoints': float(row['predicted_points']),
            'confidence': calculate_confidence(row['actual_points'], row['predicted_points']),
            'error': float(abs(row['actual_points'] - row['predicted_points'])),
            'accuracy': calculate_accuracy(row['actual_points'], row['predicted_points'])
        }
        players.append(player)
    
    # Sort by predicted points descending
    players.sort(key=lambda x: x['predictedPoints'], reverse=True)
    
    return jsonify({
        'players': players[:20],  # Limit to top 20 results
        'total': len(players),
        'query': query
    })

@app.route('/api/stats', methods=['GET'])
def get_model_stats():
    """Get overall model performance statistics"""
    if nfl_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    # Calculate overall stats
    mae = np.mean(np.abs(nfl_data['actual_points'] - nfl_data['predicted_points']))
    rmse = np.sqrt(np.mean((nfl_data['actual_points'] - nfl_data['predicted_points']) ** 2))
    
    # Calculate R²
    ss_res = np.sum((nfl_data['actual_points'] - nfl_data['predicted_points']) ** 2)
    ss_tot = np.sum((nfl_data['actual_points'] - np.mean(nfl_data['actual_points'])) ** 2)
    r2 = 1 - (ss_res / ss_tot)
    
    # Position-specific stats
    position_stats = {}
    for position in nfl_data['position'].unique():
        pos_data = nfl_data[nfl_data['position'] == position]
        pos_mae = np.mean(np.abs(pos_data['actual_points'] - pos_data['predicted_points']))
        
        # Calculate R² for position
        pos_ss_res = np.sum((pos_data['actual_points'] - pos_data['predicted_points']) ** 2)
        pos_ss_tot = np.sum((pos_data['actual_points'] - np.mean(pos_data['actual_points'])) ** 2)
        pos_r2 = 1 - (pos_ss_res / pos_ss_tot) if pos_ss_tot != 0 else 0
        
        position_stats[position] = {
            'mae': float(pos_mae),
            'r2': float(pos_r2),
            'playerCount': len(pos_data)
        }
    
    return jsonify({
        'overall': {
            'mae': float(mae),
            'rmse': float(rmse),
            'r2': float(r2),
            'totalPlayers': len(nfl_data)
        },
        'byPosition': position_stats
    })

@app.route('/api/top/<position>/<int:limit>', methods=['GET'])
def get_top_players(position, limit=10):
    """Get top N players by position based on predicted points"""
    if nfl_data.empty:
        return jsonify({'error': 'No data available'}), 500
    
    if position.upper() == 'ALL':
        position_data = nfl_data
    else:
        position_data = nfl_data[nfl_data['position'].str.upper() == position.upper()]
    
    if position_data.empty:
        return jsonify({'error': f'No players found for position: {position}'}), 404
    
    # Sort by predicted points and get top N
    top_players = position_data.nlargest(limit, 'predicted_points')
    
    players = []
    for _, row in top_players.iterrows():
        player = {
            'name': row['player_name'],
            'position': row['position'],
            'actualPoints': float(row['actual_points']),
            'predictedPoints': float(row['predicted_points']),
            'confidence': calculate_confidence(row['actual_points'], row['predicted_points']),
            'error': float(abs(row['actual_points'] - row['predicted_points'])),
            'accuracy': calculate_accuracy(row['actual_points'], row['predicted_points'])
        }
        players.append(player)
    
    return jsonify({
        'players': players,
        'total': len(players),
        'position': position.upper(),
        'limit': limit
    })

def calculate_confidence(actual, predicted):
    """Calculate confidence score based on prediction accuracy"""
    error = abs(actual - predicted)
    # Higher confidence for lower error
    # Scale to 0-100 where 0 error = 100% confidence
    max_error = 100  # Assume max reasonable error is 100 points
    confidence = max(0, (max_error - error) / max_error * 100)
    return round(confidence, 1)

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
        'dataLoaded': not nfl_data.empty,
        'playerCount': len(nfl_data) if not nfl_data.empty else 0
    })

if __name__ == '__main__':
    print("🏈 Starting NFL Predictions API...")
    print(f"📊 Loaded {len(nfl_data)} players")
    print("🚀 API running on http://localhost:5001")
    print("\nAvailable endpoints:")
    print("  GET /api/players - All players")
    print("  GET /api/players/<position> - Players by position")
    print("  GET /api/player/<name> - Specific player")
    print("  GET /api/search?q=<query> - Search players")
    print("  GET /api/stats - Model statistics")
    print("  GET /api/top/<position>/<limit> - Top N players")
    print("  GET /api/health - Health check")
    
    app.run(debug=False, host='127.0.0.1', port=5001)
