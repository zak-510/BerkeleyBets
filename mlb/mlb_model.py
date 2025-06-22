import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pybaseball as pb
import joblib
import warnings
warnings.filterwarnings('ignore')

class ImprovedMLBModel:
    def __init__(self):
        self.models = {}
        self.feature_columns = {}
        self.position_configs = {
            'P': {
                'features': ['wins', 'losses', 'era', 'whip', 'strikeouts', 'innings_pitched', 'saves', 'holds'],
                'min_innings': 50,
                'model_params': {'n_estimators': 100, 'max_depth': 10, 'random_state': 42}
            },
            'C': {
                'features': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
                'min_plate_appearances': 100,
                'model_params': {'n_estimators': 80, 'max_depth': 8, 'random_state': 42}
            },
            '1B': {
                'features': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
                'min_plate_appearances': 100,
                'model_params': {'n_estimators': 80, 'max_depth': 8, 'random_state': 42}
            },
            '2B': {
                'features': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
                'min_plate_appearances': 100,
                'model_params': {'n_estimators': 80, 'max_depth': 8, 'random_state': 42}
            },
            '3B': {
                'features': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
                'min_plate_appearances': 100,
                'model_params': {'n_estimators': 80, 'max_depth': 8, 'random_state': 42}
            },
            'SS': {
                'features': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
                'min_plate_appearances': 100,
                'model_params': {'n_estimators': 80, 'max_depth': 8, 'random_state': 42}
            },
            'OF': {
                'features': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
                'min_plate_appearances': 100,
                'model_params': {'n_estimators': 80, 'max_depth': 8, 'random_state': 42}
            },
            'DH': {
                'features': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
                'min_plate_appearances': 100,
                'model_params': {'n_estimators': 80, 'max_depth': 8, 'random_state': 42}
            }
        }
    
    def load_and_clean_data(self):
        """Load and clean MLB data with proper temporal split"""
        print("Loading MLB data...")
        
        try:
            # Load training data (2023 season)
            print("Loading 2023 batting data...")
            batting_2023 = pb.batting_stats(2023, qual=100)  # Minimum 100 PA
            print("Loading 2023 pitching data...")
            pitching_2023 = pb.pitching_stats(2023, qual=50)  # Minimum 50 IP
            
            # Load test data (2024 season)
            print("Loading 2024 batting data...")
            batting_2024 = pb.batting_stats(2024, qual=100)
            print("Loading 2024 pitching data...")
            pitching_2024 = pb.pitching_stats(2024, qual=50)
            
            # Process and combine data
            train_data = self.process_season_data(batting_2023, pitching_2023, 'train')
            test_data = self.process_season_data(batting_2024, pitching_2024, 'test')
            
            return train_data, test_data
            
        except Exception as e:
            print(f"Error loading data: {e}")
            print("Falling back to sample data...")
            return self.create_sample_data()
    
    def process_season_data(self, batting_data, pitching_data, dataset_type):
        """Process and combine batting and pitching data"""
        
        # Process batting data
        batting_processed = self.process_batting_data(batting_data)
        
        # Process pitching data
        pitching_processed = self.process_pitching_data(pitching_data)
        
        # Combine datasets
        combined_data = pd.concat([batting_processed, pitching_processed], ignore_index=True)
        
        # Calculate fantasy points (standard 5x5 scoring)
        combined_data['fantasy_points'] = self.calculate_fantasy_points(combined_data)
        
        # Filter out low-volume players
        combined_data = combined_data[combined_data['fantasy_points'] >= 50]
        
        print(f"{dataset_type.title()} data: {len(combined_data)} players")
        
        return combined_data
    
    def process_batting_data(self, batting_data):
        """Process batting statistics"""
        # Standardize column names
        batting_data = batting_data.rename(columns={
            'Name': 'player_name',
            'Team': 'team',
            'PA': 'plate_appearances',
            'H': 'hits',
            'HR': 'home_runs',
            'RBI': 'rbi',
            'R': 'runs',
            'SB': 'stolen_bases',
            'AVG': 'batting_average',
            'OBP': 'obp',
            'SLG': 'slg'
        })
        
        # Add position information (simplified - would need more detailed data)
        batting_data['position'] = 'OF'  # Default to OF, would need actual position data
        
        # Fill missing values
        numeric_cols = ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg']
        for col in numeric_cols:
            if col in batting_data.columns:
                batting_data[col] = pd.to_numeric(batting_data[col], errors='coerce').fillna(0)
        
        return batting_data[['player_name', 'team', 'position'] + numeric_cols]
    
    def process_pitching_data(self, pitching_data):
        """Process pitching statistics"""
        # Standardize column names
        pitching_data = pitching_data.rename(columns={
            'Name': 'player_name',
            'Team': 'team',
            'W': 'wins',
            'L': 'losses',
            'ERA': 'era',
            'WHIP': 'whip',
            'SO': 'strikeouts',
            'IP': 'innings_pitched',
            'SV': 'saves',
            'HLD': 'holds'
        })
        
        # Add position
        pitching_data['position'] = 'P'
        
        # Fill missing values
        numeric_cols = ['wins', 'losses', 'era', 'whip', 'strikeouts', 'innings_pitched', 'saves', 'holds']
        for col in numeric_cols:
            if col in pitching_data.columns:
                pitching_data[col] = pd.to_numeric(pitching_data[col], errors='coerce').fillna(0)
        
        return pitching_data[['player_name', 'team', 'position'] + numeric_cols]
    
    def calculate_fantasy_points(self, data):
        """Calculate fantasy points using standard 5x5 scoring"""
        fantasy_points = []
        
        for _, player in data.iterrows():
            if player['position'] == 'P':
                # Pitching points: Wins (10), Saves (10), Strikeouts (1), ERA/WHIP bonuses
                points = (player['wins'] * 10 + 
                         player['saves'] * 10 + 
                         player['strikeouts'] * 1)
                
                # ERA bonus (simplified)
                if player['era'] < 3.00:
                    points += 50
                elif player['era'] < 3.50:
                    points += 25
                
                # WHIP bonus (simplified)
                if player['whip'] < 1.10:
                    points += 50
                elif player['whip'] < 1.25:
                    points += 25
                    
            else:
                # Batting points: Hits (1), HR (4), RBI (2), Runs (2), SB (2)
                points = (player['hits'] * 1 + 
                         player['home_runs'] * 4 + 
                         player['rbi'] * 2 + 
                         player['runs'] * 2 + 
                         player['stolen_bases'] * 2)
            
            fantasy_points.append(points)
        
        return fantasy_points
    
    def create_sample_data(self):
        """Create sample data for testing when API fails"""
        print("Creating sample MLB data...")
        
        # Sample batting data
        batting_sample = pd.DataFrame({
            'player_name': ['M.Trout', 'A.Judge', 'F.Freeman', 'J.Ramirez', 'T.Turner'],
            'team': ['LAA', 'NYY', 'LAD', 'CLE', 'PHI'],
            'position': ['OF', 'OF', '1B', '3B', 'SS'],
            'hits': [120, 110, 140, 130, 125],
            'home_runs': [25, 35, 20, 30, 15],
            'rbi': [80, 90, 85, 95, 70],
            'runs': [85, 95, 90, 100, 75],
            'stolen_bases': [15, 5, 10, 20, 25],
            'batting_average': [0.280, 0.290, 0.310, 0.285, 0.275],
            'obp': [0.380, 0.400, 0.410, 0.375, 0.365],
            'slg': [0.520, 0.580, 0.540, 0.550, 0.480]
        })
        
        # Sample pitching data
        pitching_sample = pd.DataFrame({
            'player_name': ['J.deGrom', 'G.Cole', 'S.Ohtani', 'M.Scherzer', 'J.Verlander'],
            'team': ['TEX', 'NYY', 'LAA', 'NYM', 'HOU'],
            'position': ['P', 'P', 'P', 'P', 'P'],
            'wins': [12, 15, 10, 14, 13],
            'losses': [8, 7, 8, 6, 8],
            'era': [2.80, 3.20, 3.10, 2.90, 3.00],
            'whip': [1.05, 1.15, 1.10, 1.08, 1.12],
            'strikeouts': [180, 200, 190, 175, 185],
            'innings_pitched': [180, 200, 190, 175, 185],
            'saves': [0, 0, 0, 0, 0],
            'holds': [0, 0, 0, 0, 0]
        })
        
        # Combine and calculate fantasy points
        combined = pd.concat([batting_sample, pitching_sample], ignore_index=True)
        combined['fantasy_points'] = self.calculate_fantasy_points(combined)
        
        # Split into train/test (simplified)
        train_data = combined.copy()
        test_data = combined.copy()
        
        return train_data, test_data
    
    def train_position_models(self, train_data):
        """Train separate models for each position"""
        print("\nTraining position-specific models...")
        
        positions = ['P', 'C', '1B', '2B', '3B', 'SS', 'OF', 'DH']
        
        for position in positions:
            pos_data = train_data[train_data['position'] == position].copy()
            
            if len(pos_data) < 5:
                print(f"Skipping {position}: insufficient data ({len(pos_data)} players)")
                continue
            
            # Get position-specific features
            features = self.position_configs[position]['features']
            
            # Check if features exist in data
            available_features = [f for f in features if f in pos_data.columns]
            if len(available_features) < 3:
                print(f"Skipping {position}: insufficient features available")
                continue
            
            # Prepare features and target
            X = pos_data[available_features].fillna(0)
            y = pos_data['fantasy_points']
            
            # Train model
            model_params = self.position_configs[position]['model_params']
            model = RandomForestRegressor(**model_params)
            model.fit(X, y)
            
            # Store model and features
            self.models[position] = model
            self.feature_columns[position] = available_features
            
            # Calculate training metrics
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            
            print(f"{position}: {len(pos_data)} players, R² = {r2:.3f}, MAE = {mae:.1f}")
    
    def predict_player(self, player_data):
        """Predict fantasy points for a single player"""
        position = player_data['position']
        
        if position not in self.models:
            return None
        
        # Get features for this position
        features = self.feature_columns[position]
        
        # Extract feature values
        feature_values = []
        for feature in features:
            value = player_data.get(feature, 0)
            feature_values.append(float(value))
        
        # Make prediction
        X = np.array(feature_values).reshape(1, -1)
        prediction = self.models[position].predict(X)[0]
        
        return round(prediction, 2)
    
    def evaluate_model(self, test_data):
        """Evaluate model on test data"""
        print("\nEvaluating model on test data...")
        
        results = []
        
        for _, player in test_data.iterrows():
            prediction = self.predict_player(player)
            
            if prediction is not None:
                results.append({
                    'player_name': player['player_name'],
                    'position': player['position'],
                    'actual_points': player['fantasy_points'],
                    'predicted_points': prediction
                })
        
        results_df = pd.DataFrame(results)
        
        if len(results_df) == 0:
            print("No predictions made - check model availability")
            return results_df
        
        # Calculate overall metrics
        overall_mae = mean_absolute_error(results_df['actual_points'], results_df['predicted_points'])
        overall_rmse = np.sqrt(mean_squared_error(results_df['actual_points'], results_df['predicted_points']))
        overall_r2 = r2_score(results_df['actual_points'], results_df['predicted_points'])
        
        print(f"\nOverall Performance:")
        print(f"Players: {len(results_df)}")
        print(f"MAE: {overall_mae:.1f}")
        print(f"RMSE: {overall_rmse:.1f}")
        print(f"R²: {overall_r2:.3f}")
        
        # Position-specific metrics
        print(f"\nPosition-specific Performance:")
        for position in results_df['position'].unique():
            pos_results = results_df[results_df['position'] == position]
            pos_mae = mean_absolute_error(pos_results['actual_points'], pos_results['predicted_points'])
            pos_r2 = r2_score(pos_results['actual_points'], pos_results['predicted_points'])
            print(f"{position}: {len(pos_results)} players, MAE = {pos_mae:.1f}, R² = {pos_r2:.3f}")
        
        return results_df
    
    def save_models(self):
        """Save trained models"""
        for position, model in self.models.items():
            filename = f'mlb_{position.lower()}_model.pkl'
            joblib.dump({
                'model': model,
                'features': self.feature_columns[position]
            }, filename)
            print(f"Saved {position} model to {filename}")

def main():
    """Main training and evaluation pipeline"""
    
    # Initialize model
    mlb_model = ImprovedMLBModel()
    
    # Load and clean data
    train_data, test_data = mlb_model.load_and_clean_data()
    
    # Train position-specific models
    mlb_model.train_position_models(train_data)
    
    # Evaluate on test data
    results = mlb_model.evaluate_model(test_data)
    
    # Save results
    results.to_csv('mlb_inference_results.csv', index=False)
    print(f"\nSaved results to 'mlb_inference_results.csv'")
    
    # Save models
    mlb_model.save_models()
    
    print("\nMLB model training complete!")

if __name__ == "__main__":
    main() 