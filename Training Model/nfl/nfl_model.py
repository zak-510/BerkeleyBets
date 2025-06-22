import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import nfl_data_py as nfl
import joblib
import warnings
warnings.filterwarnings('ignore')

class ImprovedNFLModel:
    def __init__(self):
        self.models = {}
        self.feature_columns = {}
        self.position_configs = {
            'QB': {
                'features': ['passing_yards', 'passing_tds', 'interceptions', 'attempts', 'rushing_yards', 'rushing_tds'],
                'min_attempts': 50,
                'model_params': {'n_estimators': 100, 'max_depth': 10, 'random_state': 42}
            },
            'RB': {
                'features': ['rushing_yards', 'rushing_tds', 'carries', 'receiving_yards', 'receiving_tds', 'targets'],
                'min_attempts': 25,
                'model_params': {'n_estimators': 80, 'max_depth': 8, 'random_state': 42}
            },
            'WR': {
                'features': ['receiving_yards', 'receiving_tds', 'targets', 'receptions', 'rushing_yards'],
                'min_attempts': 15,
                'model_params': {'n_estimators': 80, 'max_depth': 8, 'random_state': 42}
            },
            'TE': {
                'features': ['receiving_yards', 'receiving_tds', 'targets', 'receptions'],
                'min_attempts': 10,
                'model_params': {'n_estimators': 60, 'max_depth': 6, 'random_state': 42}
            }
        }
    
    def load_and_clean_data(self):
        """Load and clean NFL data with proper temporal split"""
        print("Loading NFL data...")
        
        # Load training data (2023)
        train_data = nfl.import_weekly_data([2023], columns=[
            'player_id', 'player_name', 'position', 'recent_team', 'week',
            'passing_yards', 'passing_tds', 'interceptions', 'attempts',
            'rushing_yards', 'rushing_tds', 'carries',
            'receiving_yards', 'receiving_tds', 'receptions', 'targets',
            'fantasy_points_ppr'
        ])
        
        # Load test data (2024)
        test_data = nfl.import_weekly_data([2024], columns=[
            'player_id', 'player_name', 'position', 'recent_team', 'week',
            'passing_yards', 'passing_tds', 'interceptions', 'attempts',
            'rushing_yards', 'rushing_tds', 'carries',
            'receiving_yards', 'receiving_tds', 'receptions', 'targets',
            'fantasy_points_ppr'
        ])
        
        # Clean and aggregate data
        train_clean = self.clean_and_aggregate(train_data, 'train')
        test_clean = self.clean_and_aggregate(test_data, 'test')
        
        return train_clean, test_clean
    
    def clean_and_aggregate(self, data, dataset_type):
        """Clean and aggregate weekly data to season totals"""
        
        # Fill NaN values with 0
        numeric_cols = ['passing_yards', 'passing_tds', 'interceptions', 'attempts',
                       'rushing_yards', 'rushing_tds', 'carries',
                       'receiving_yards', 'receiving_tds', 'receptions', 'targets',
                       'fantasy_points_ppr']
        
        for col in numeric_cols:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
        
        # Aggregate to season totals
        agg_dict = {col: 'sum' for col in numeric_cols}
        agg_dict.update({
            'position': 'first',
            'recent_team': 'first'
        })
        
        season_data = data.groupby(['player_id', 'player_name']).agg(agg_dict).reset_index()
        
        # Filter out low-volume players
        season_data = season_data[season_data['fantasy_points_ppr'] >= 10]
        
        # Remove players with invalid data
        season_data = season_data[season_data['fantasy_points_ppr'].notna()]
        season_data = season_data[season_data['position'].isin(['QB', 'RB', 'WR', 'TE'])]
        
        print(f"{dataset_type.title()} data: {len(season_data)} players")
        
        return season_data
    
    def train_position_models(self, train_data):
        """Train separate models for each position"""
        print("\nTraining position-specific models...")
        
        for position in ['QB', 'RB', 'WR', 'TE']:
            pos_data = train_data[train_data['position'] == position].copy()
            
            if len(pos_data) < 10:
                print(f"Skipping {position}: insufficient data ({len(pos_data)} players)")
                continue
            
            # Get position-specific features
            features = self.position_configs[position]['features']
            
            # Prepare features and target
            X = pos_data[features].fillna(0)
            y = pos_data['fantasy_points_ppr']
            
            # Train model
            model_params = self.position_configs[position]['model_params']
            model = RandomForestRegressor(**model_params)
            model.fit(X, y)
            
            # Store model and features
            self.models[position] = model
            self.feature_columns[position] = features
            
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
        X = np.array([player_data[feat] for feat in features]).reshape(1, -1)
        
        # Make prediction
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
                    'actual_points': player['fantasy_points_ppr'],
                    'predicted_points': prediction
                })
        
        results_df = pd.DataFrame(results)
        
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
            filename = f'nfl_{position.lower()}_model.pkl'
            joblib.dump({
                'model': model,
                'features': self.feature_columns[position]
            }, filename)
            print(f"Saved {position} model to {filename}")

def main():
    """Main training and evaluation pipeline"""
    
    # Initialize model
    nfl_model = ImprovedNFLModel()
    
    # Load and clean data
    train_data, test_data = nfl_model.load_and_clean_data()
    
    # Train position-specific models
    nfl_model.train_position_models(train_data)
    
    # Evaluate on test data
    results = nfl_model.evaluate_model(test_data)
    
    # Save results
    results.to_csv('inference_results.csv', index=False)
    print(f"\nSaved results to 'inference_results.csv'")
    
    # Save models
    nfl_model.save_models()
    
    print("\nImproved model training complete!")

if __name__ == "__main__":
    main() 