import requests
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import joblib
import os
import argparse
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PlayerProjectionModel:
    def __init__(self, sport='nba'):
        self.sport = sport.lower()
        self.model = None
        self.feature_columns = []
        self.target_column = None
        self.sport_configs = {
            'nba': {
                'api_sport': 'basketball',
                'league': 'nba',
                'target_stat': 'points',
                'features': ['games_played', 'minutes', 'field_goals_made', 'field_goals_attempted', 
                           'three_point_field_goals_made', 'free_throws_made', 'rebounds', 'assists'],
                'season_type': 2  # Regular season
            },
            'nfl': {
                'api_sport': 'football',
                'league': 'nfl',
                'target_stat': 'passing_yards',
                'features': ['games_played', 'completions', 'attempts', 'completion_percentage',
                           'passing_touchdowns', 'rushing_yards', 'rushing_touchdowns'],
                'season_type': 2
            },
            'mlb': {
                'api_sport': 'baseball',
                'league': 'mlb',
                'target_stat': 'hits',
                'features': ['games_played', 'at_bats', 'runs', 'doubles', 'triples', 
                           'home_runs', 'rbis', 'stolen_bases'],
                'season_type': 2
            }
        }
    
    def get_teams(self):
        """Get all teams for the sport"""
        config = self.sport_configs[self.sport]
        url = f"https://site.api.espn.com/apis/site/v2/sports/{config['api_sport']}/{config['league']}/teams"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            teams = []
            for team in data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', []):
                teams.append({
                    'id': team['team']['id'],
                    'name': team['team']['displayName'],
                    'abbreviation': team['team']['abbreviation']
                })
            return teams
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return []
    
    def get_team_roster(self, team_id):
        """Get roster for a specific team"""
        config = self.sport_configs[self.sport]
        url = f"https://site.api.espn.com/apis/site/v2/sports/{config['api_sport']}/{config['league']}/teams/{team_id}/roster"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            players = []
            for athlete in data.get('athletes', []):
                for player in athlete.get('items', []):
                    players.append({
                        'id': player['id'],
                        'name': player['displayName'],
                        'position': player.get('position', {}).get('abbreviation', 'N/A'),
                        'team_id': team_id
                    })
            return players
        except Exception as e:
            print(f"Error fetching roster for team {team_id}: {e}")
            return []
    
    def get_player_stats(self, player_id, season_year=2024):
        """Get player statistics for a specific season"""
        config = self.sport_configs[self.sport]
        url = f"https://site.api.espn.com/apis/site/v2/sports/{config['api_sport']}/{config['league']}/athletes/{player_id}/statistics"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract statistics - this is a simplified version
            # In practice, you'd need to parse the complex ESPN stats structure
            stats = {}
            
            # Mock data structure for demonstration
            # In real implementation, parse from data['statistics']
            if self.sport == 'nba':
                stats = {
                    'player_id': player_id,
                    'games_played': np.random.randint(60, 82),
                    'minutes': np.random.uniform(25, 40),
                    'points': np.random.uniform(8, 30),
                    'field_goals_made': np.random.uniform(3, 12),
                    'field_goals_attempted': np.random.uniform(6, 25),
                    'three_point_field_goals_made': np.random.uniform(0, 4),
                    'free_throws_made': np.random.uniform(1, 8),
                    'rebounds': np.random.uniform(3, 12),
                    'assists': np.random.uniform(2, 10)
                }
            elif self.sport == 'nfl':
                stats = {
                    'player_id': player_id,
                    'games_played': np.random.randint(12, 17),
                    'completions': np.random.uniform(200, 400),
                    'attempts': np.random.uniform(300, 600),
                    'completion_percentage': np.random.uniform(55, 75),
                    'passing_yards': np.random.uniform(2000, 5000),
                    'passing_touchdowns': np.random.uniform(15, 45),
                    'rushing_yards': np.random.uniform(0, 1000),
                    'rushing_touchdowns': np.random.uniform(0, 10)
                }
            elif self.sport == 'mlb':
                stats = {
                    'player_id': player_id,
                    'games_played': np.random.randint(120, 162),
                    'at_bats': np.random.uniform(400, 650),
                    'runs': np.random.uniform(50, 120),
                    'hits': np.random.uniform(100, 200),
                    'doubles': np.random.uniform(15, 45),
                    'triples': np.random.uniform(0, 10),
                    'home_runs': np.random.uniform(5, 50),
                    'rbis': np.random.uniform(40, 130),
                    'stolen_bases': np.random.uniform(0, 40)
                }
            
            return stats
        except Exception as e:
            print(f"Error fetching stats for player {player_id}: {e}")
            return None
    
    def collect_training_data(self, max_players=100):
        """Collect training data from multiple players"""
        print(f"Collecting training data for {self.sport.upper()}...")
        
        # Get teams
        teams = self.get_teams()
        if not teams:
            print("No teams found. Using mock data for demonstration.")
            return self.generate_mock_data(max_players)
        
        all_player_stats = []
        player_count = 0
        
        for team in teams[:10]:  # Limit to first 10 teams for demo
            if player_count >= max_players:
                break
                
            print(f"Processing team: {team['name']}")
            roster = self.get_team_roster(team['id'])
            
            for player in roster[:10]:  # Limit players per team
                if player_count >= max_players:
                    break
                    
                stats = self.get_player_stats(player['id'])
                if stats:
                    stats['player_name'] = player['name']
                    stats['position'] = player['position']
                    all_player_stats.append(stats)
                    player_count += 1
        
        if not all_player_stats:
            print("No real data collected. Using mock data for demonstration.")
            return self.generate_mock_data(max_players)
        
        df = pd.DataFrame(all_player_stats)
        print(f"Collected data for {len(df)} players")
        return df
    
    def generate_mock_data(self, num_players=100):
        """Generate mock training data for demonstration"""
        print(f"Generating mock training data for {num_players} players...")
        
        config = self.sport_configs[self.sport]
        data = []
        
        for i in range(num_players):
            if self.sport == 'nba':
                player_data = {
                    'player_id': f'mock_{i}',
                    'player_name': f'Player_{i}',
                    'position': np.random.choice(['PG', 'SG', 'SF', 'PF', 'C']),
                    'games_played': np.random.randint(60, 82),
                    'minutes': np.random.uniform(15, 40),
                    'points': np.random.uniform(5, 35),
                    'field_goals_made': np.random.uniform(2, 15),
                    'field_goals_attempted': np.random.uniform(4, 25),
                    'three_point_field_goals_made': np.random.uniform(0, 5),
                    'free_throws_made': np.random.uniform(0, 10),
                    'rebounds': np.random.uniform(2, 15),
                    'assists': np.random.uniform(1, 12)
                }
            elif self.sport == 'nfl':
                player_data = {
                    'player_id': f'mock_{i}',
                    'player_name': f'Player_{i}',
                    'position': np.random.choice(['QB', 'RB', 'WR', 'TE']),
                    'games_played': np.random.randint(12, 17),
                    'completions': np.random.uniform(150, 450),
                    'attempts': np.random.uniform(250, 650),
                    'completion_percentage': np.random.uniform(50, 80),
                    'passing_yards': np.random.uniform(1500, 5500),
                    'passing_touchdowns': np.random.uniform(10, 50),
                    'rushing_yards': np.random.uniform(0, 1200),
                    'rushing_touchdowns': np.random.uniform(0, 15)
                }
            elif self.sport == 'mlb':
                player_data = {
                    'player_id': f'mock_{i}',
                    'player_name': f'Player_{i}',
                    'position': np.random.choice(['1B', '2B', '3B', 'SS', 'OF', 'C', 'P']),
                    'games_played': np.random.randint(100, 162),
                    'at_bats': np.random.uniform(300, 700),
                    'runs': np.random.uniform(30, 140),
                    'hits': np.random.uniform(80, 220),
                    'doubles': np.random.uniform(10, 50),
                    'triples': np.random.uniform(0, 15),
                    'home_runs': np.random.uniform(0, 60),
                    'rbis': np.random.uniform(30, 150),
                    'stolen_bases': np.random.uniform(0, 50)
                }
            
            data.append(player_data)
        
        return pd.DataFrame(data)
    
    def preprocess_data(self, df):
        """Preprocess the data for training"""
        config = self.sport_configs[self.sport]
        
        # Remove rows with missing target
        df = df.dropna(subset=[config['target_stat']])
        
        # Fill missing feature values with median
        feature_cols = config['features']
        for col in feature_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        # Create per-game averages
        if 'games_played' in df.columns and df['games_played'].min() > 0:
            for col in df.columns:
                if col not in ['player_id', 'player_name', 'position', 'games_played'] and col in df.select_dtypes(include=[np.number]).columns:
                    df[f'{col}_per_game'] = df[col] / df['games_played']
        
        return df
    
    def train_model(self, df, model_type='xgboost'):
        """Train the projection model"""
        config = self.sport_configs[self.sport]
        
        # Prepare features and target
        feature_cols = [col for col in config['features'] if col in df.columns]
        
        # Add per-game features if available
        per_game_cols = [col for col in df.columns if col.endswith('_per_game') and col != f"{config['target_stat']}_per_game"]
        feature_cols.extend(per_game_cols)
        
        self.feature_columns = feature_cols
        self.target_column = config['target_stat']
        
        X = df[feature_cols]
        y = df[config['target_stat']]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        if model_type == 'linear':
            self.model = LinearRegression()
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:  # xgboost
            self.model = xgb.XGBRegressor(n_estimators=100, random_state=42)
        
        print(f"Training {model_type} model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        print(f"Model Performance:")
        print(f"Training MAE: {train_mae:.2f}")
        print(f"Testing MAE: {test_mae:.2f}")
        print(f"Training R²: {train_r2:.3f}")
        print(f"Testing R²: {test_r2:.3f}")
        
        return {
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2
        }
    
    def save_model(self, filepath=None):
        """Save the trained model"""
        if not filepath:
            os.makedirs('models', exist_ok=True)
            filepath = f'models/{self.sport}_projection_model.pkl'
        
        model_data = {
            'model': self.model,
            'feature_columns': self.feature_columns,
            'target_column': self.target_column,
            'sport': self.sport,
            'sport_config': self.sport_configs[self.sport]
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
        return filepath
    
    def load_model(self, filepath):
        """Load a trained model"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.feature_columns = model_data['feature_columns']
        self.target_column = model_data['target_column']
        self.sport = model_data['sport']
        print(f"Model loaded from {filepath}")
    
    def predict_player_performance(self, player_stats):
        """Predict performance for a specific player"""
        if self.model is None:
            raise ValueError("No model trained or loaded")
        
        # Prepare input data
        input_data = {}
        for col in self.feature_columns:
            if col in player_stats:
                input_data[col] = player_stats[col]
            else:
                input_data[col] = 0  # Default value for missing features
        
        # Create DataFrame
        X = pd.DataFrame([input_data])
        
        # Make prediction
        prediction = self.model.predict(X)[0]
        
        return prediction

def main():
    parser = argparse.ArgumentParser(description='Train player projection models')
    parser.add_argument('--sport', type=str, default='nba', 
                       choices=['nba', 'nfl', 'mlb'],
                       help='Sport to train model for')
    parser.add_argument('--model', type=str, default='xgboost',
                       choices=['linear', 'random_forest', 'xgboost'],
                       help='Model type to use')
    parser.add_argument('--players', type=int, default=100,
                       help='Maximum number of players to collect data for')
    
    args = parser.parse_args()
    
    # Initialize model
    projection_model = PlayerProjectionModel(sport=args.sport)
    
    # Collect training data
    df = projection_model.collect_training_data(max_players=args.players)
    
    # Preprocess data
    df = projection_model.preprocess_data(df)
    
    # Train model
    metrics = projection_model.train_model(df, model_type=args.model)
    
    # Save model
    model_path = projection_model.save_model()
    
    print(f"\nTraining completed for {args.sport.upper()}")
    print(f"Model saved to: {model_path}")
    
    # Example prediction
    print(f"\n--- Example Prediction ---")
    config = projection_model.sport_configs[args.sport]
    
    if args.sport == 'nba':
        example_stats = {
            'games_played': 70,
            'minutes': 32,
            'field_goals_made': 8,
            'field_goals_attempted': 18,
            'three_point_field_goals_made': 2,
            'free_throws_made': 4,
            'rebounds': 7,
            'assists': 6
        }
    elif args.sport == 'nfl':
        example_stats = {
            'games_played': 16,
            'completions': 300,
            'attempts': 500,
            'completion_percentage': 65,
            'passing_touchdowns': 25,
            'rushing_yards': 200,
            'rushing_touchdowns': 3
        }
    elif args.sport == 'mlb':
        example_stats = {
            'games_played': 150,
            'at_bats': 550,
            'runs': 80,
            'doubles': 25,
            'triples': 3,
            'home_runs': 20,
            'rbis': 85,
            'stolen_bases': 15
        }
    
    prediction = projection_model.predict_player_performance(example_stats)
    print(f"Predicted {config['target_stat']}: {prediction:.2f}")

if __name__ == "__main__":
    main()