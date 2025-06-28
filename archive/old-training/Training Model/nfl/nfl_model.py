import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
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
    
    def load_and_clean_data(self, use_temporal_split=True):
        """Load and clean NFL data with proper temporal split"""
        print("Loading NFL data...")
        
        if use_temporal_split:
            # Load all available data for temporal splitting
            all_years = [2022, 2023, 2024]
            all_data = []
            
            for year in all_years:
                try:
                    year_data = nfl.import_weekly_data([year], columns=[
                        'player_id', 'player_name', 'position', 'recent_team', 'week', 'season',
                        'passing_yards', 'passing_tds', 'interceptions', 'attempts',
                        'rushing_yards', 'rushing_tds', 'carries',
                        'receiving_yards', 'receiving_tds', 'receptions', 'targets',
                        'fantasy_points_ppr'
                    ])
                    if not year_data.empty:
                        year_data['season'] = year
                        all_data.append(year_data)
                except:
                    print(f"Could not load data for {year}")
            
            if all_data:
                combined_data = pd.concat(all_data, ignore_index=True)
                # Sort by season and week for proper temporal ordering
                combined_data = combined_data.sort_values(['season', 'week'])
                return self.clean_data(combined_data), None
            
        # Fallback to original year-based split
        train_data = nfl.import_weekly_data([2023], columns=[
            'player_id', 'player_name', 'position', 'recent_team', 'week',
            'passing_yards', 'passing_tds', 'interceptions', 'attempts',
            'rushing_yards', 'rushing_tds', 'carries',
            'receiving_yards', 'receiving_tds', 'receptions', 'targets',
            'fantasy_points_ppr'
        ])
        
        test_data = nfl.import_weekly_data([2024], columns=[
            'player_id', 'player_name', 'position', 'recent_team', 'week',
            'passing_yards', 'passing_tds', 'interceptions', 'attempts',
            'rushing_yards', 'rushing_tds', 'carries',
            'receiving_yards', 'receiving_tds', 'receptions', 'targets',
            'fantasy_points_ppr'
        ])
        
        train_clean = self.clean_and_aggregate(train_data, 'train')
        test_clean = self.clean_and_aggregate(test_data, 'test')
        
        return train_clean, test_clean
    
    def clean_data(self, data):
        """Clean weekly data without aggregation for temporal split"""
        numeric_cols = ['passing_yards', 'passing_tds', 'interceptions', 'attempts',
                       'rushing_yards', 'rushing_tds', 'carries',
                       'receiving_yards', 'receiving_tds', 'receptions', 'targets',
                       'fantasy_points_ppr']
        
        for col in numeric_cols:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
        
        # Remove invalid data
        data = data[data['fantasy_points_ppr'].notna()]
        data = data[data['position'].isin(['QB', 'RB', 'WR', 'TE'])]
        
        print(f"Cleaned data: {len(data)} game records")
        return data
    
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
    
    def train_position_models_temporal(self, data):
        """Train models using TimeSeriesSplit for proper temporal validation"""
        print("\nTraining position-specific models with temporal validation...")
        
        tscv = TimeSeriesSplit(n_splits=3)
        
        for position in ['QB', 'RB', 'WR', 'TE']:
            pos_data = data[data['position'] == position].copy()
            
            if len(pos_data) < 50:
                print(f"Skipping {position}: insufficient data ({len(pos_data)} records)")
                continue
            
            # Get position-specific features
            features = self.position_configs[position]['features']
            
            # Prepare features and target
            X = pos_data[features].fillna(0)
            y = pos_data['fantasy_points_ppr']
            
            # Train model with cross-validation
            model_params = self.position_configs[position]['model_params']
            model = RandomForestRegressor(**model_params)
            
            # Perform time series cross-validation
            cv_scores = cross_val_score(model, X, y, cv=tscv, 
                                      scoring='r2', n_jobs=-1)
            
            # Train final model on all data
            model.fit(X, y)
            
            # Store model and features
            self.models[position] = model
            self.feature_columns[position] = features
            
            # Calculate metrics
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            
            print(f"{position}: {len(pos_data)} records, R² = {r2:.3f}, "
                  f"CV R² = {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f}), "
                  f"MAE = {mae:.1f}")
    
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
    
    # Try temporal split first
    try:
        print("Attempting temporal split approach...")
        data, _ = nfl_model.load_and_clean_data(use_temporal_split=True)
        if data is not None:
            nfl_model.train_position_models_temporal(data)
        else:
            raise Exception("Temporal data loading failed")
    except:
        print("\nFalling back to year-based split...")
        # Load and clean data with year-based split
        train_data, test_data = nfl_model.load_and_clean_data(use_temporal_split=False)
        
        # Train position-specific models
        nfl_model.train_position_models(train_data)
        
        # Evaluate on test data
        results = nfl_model.evaluate_model(test_data)
        
        # Save results
        results.to_csv('inference_results.csv', index=False)
        print(f"\nSaved results to 'inference_results.csv'")
    
    # Save models
    nfl_model.save_models()
    
    print("\nModel training complete with temporal validation!")

if __name__ == "__main__":
    main() 