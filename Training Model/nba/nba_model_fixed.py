import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import warnings
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# NBA API imports
try:
    from nba_api.stats.endpoints import playergamelog, playerprofilev2, leaguegamelog
    from nba_api.stats.static import players, teams
    NBA_API_AVAILABLE = True
except ImportError:
    print("❌ ERROR: nba_api not installed. Install with: pip install nba_api")
    NBA_API_AVAILABLE = False

warnings.filterwarnings('ignore')

class NBAPlayerProjectionModelFixed:
    """
    FIXED NBA Player Performance Prediction System with NO DATA LEAKAGE
    
    Uses only shooting efficiency, minutes, and usage patterns as features
    to predict individual stats (points, rebounds, assists) and fantasy points.
    
    CRITICAL FIX: Complete separation between features and targets!
    Features: shooting metrics, efficiency, minutes, usage
    Targets: pts, reb, ast, fantasy_points
    """
    
    def __init__(self):
        self.models = {}  # Multi-output models for each position
        self.feature_columns = {}
        self.target_columns = ['pts', 'reb', 'ast', 'fantasy_points']  # What we predict
        
        # FINAL FIX: Features are ONLY historical averages from previous games
        # ZERO DATA LEAKAGE - no same-game information used!
        self.position_configs = {
            'PG': {
                'features': ['hist_fg_pct', 'hist_fg3_pct', 'hist_ft_pct', 'hist_min_avg', 'hist_usage_rate'],
                'focus_stats': ['assists', 'steals', 'pace'],
                'min_games': 20,
                'model_params': {'n_estimators': 80, 'max_depth': 4, 'random_state': 42}
            },
            'SG': {
                'features': ['hist_fg_pct', 'hist_fg3_pct', 'hist_ft_pct', 'hist_min_avg', 'hist_usage_rate'],
                'focus_stats': ['shooting', 'scoring', 'efficiency'],
                'min_games': 20,
                'model_params': {'n_estimators': 80, 'max_depth': 4, 'random_state': 42}
            },
            'SF': {
                'features': ['hist_fg_pct', 'hist_fg3_pct', 'hist_ft_pct', 'hist_min_avg', 'hist_usage_rate'],
                'focus_stats': ['versatility', 'all_around'],
                'min_games': 20,
                'model_params': {'n_estimators': 80, 'max_depth': 4, 'random_state': 42}
            },
            'PF': {
                'features': ['hist_fg_pct', 'hist_fg3_pct', 'hist_ft_pct', 'hist_min_avg', 'hist_usage_rate'],
                'focus_stats': ['rebounds', 'blocks', 'inside'],
                'min_games': 20,
                'model_params': {'n_estimators': 80, 'max_depth': 4, 'random_state': 42}
            },
            'C': {
                'features': ['hist_fg_pct', 'hist_fg3_pct', 'hist_ft_pct', 'hist_min_avg', 'hist_usage_rate'],
                'focus_stats': ['rebounds', 'blocks', 'inside'],
                'min_games': 20,
                'model_params': {'n_estimators': 80, 'max_depth': 4, 'random_state': 42}
            }
        }
        self.current_season = '2024-25'
        
    def calculate_fantasy_points_correct(self, stats: Dict) -> float:
        """CORRECTED fantasy points calculation including ALL relevant stats"""
        pts = stats.get('pts', 0)
        reb = stats.get('reb', 0) 
        ast = stats.get('ast', 0)
        stl = stats.get('stl', 0)
        blk = stats.get('blk', 0)
        tov = stats.get('tov', 0)
        
        fantasy_pts = (pts * 1.0 + reb * 1.2 + ast * 1.5 + stl * 3.0 + blk * 3.0 + tov * -1.0)
        
        # Bonus for double-doubles and triple-doubles
        double_double_stats = [pts >= 10, reb >= 10, ast >= 10, stl >= 10, blk >= 10]
        double_double_count = sum(double_double_stats)
        
        if double_double_count >= 3:
            fantasy_pts += 3.0  # Triple-double bonus
        elif double_double_count >= 2:
            fantasy_pts += 1.5  # Double-double bonus
            
        return round(fantasy_pts, 2)
    
    def validate_player_name(self, player_name: str) -> bool:
        """Validate that player name is a real NBA player name, not a generic placeholder"""
        if not player_name or not isinstance(player_name, str):
            return False
        
        # Filter out generic "Player_" entries
        if player_name.startswith('Player_'):
            return False
        
        # Basic validation - real names should have at least first and last name
        name_parts = player_name.strip().split()
        if len(name_parts) < 2:
            return False
        
        # Check for other generic patterns
        generic_patterns = ['Player', 'Test', 'Sample', 'Unknown', 'N/A', 'NULL']
        for pattern in generic_patterns:
            if pattern.lower() in player_name.lower():
                return False
        
        return True
    
    def get_player_position_from_api(self, player_id: int) -> Optional[str]:
        """Get player position from NBA API using player profile"""
        try:
            # Rate limiting
            time.sleep(1.1)
            
            profile = playerprofilev2.PlayerProfileV2(player_id=player_id)
            profile_data = profile.get_data_frames()
            
            if len(profile_data) > 0 and len(profile_data[0]) > 0:
                player_info = profile_data[0].iloc[0]
                position = player_info.get('POSITION', '')
                
                # Normalize position names
                if position:
                    position = position.upper().strip()
                    
                    if position in ['POINT GUARD', 'PG']:
                        return 'PG'
                    elif position in ['SHOOTING GUARD', 'SG']:
                        return 'SG'  
                    elif position in ['SMALL FORWARD', 'SF']:
                        return 'SF'
                    elif position in ['POWER FORWARD', 'PF']:
                        return 'PF'
                    elif position in ['CENTER', 'C']:
                        return 'C'
                    elif 'GUARD' in position:
                        if 'POINT' in position:
                            return 'PG'
                        else:
                            return 'SG'
                    elif 'FORWARD' in position:
                        if 'POWER' in position or 'CENTER' in position:
                            return 'PF'
                        else:
                            return 'SF'
                    elif 'CENTER' in position:
                        return 'C'
                
        except Exception as e:
            print(f"Warning: Could not fetch position for player ID {player_id}: {str(e)}")
        
        return None
    
    def get_player_position_fallback(self, player_name: str) -> str:
        """Comprehensive position mapping with accurate NBA player positions"""
        position_mapping = {
            # Point Guards
            'Stephen Curry': 'PG', 'Luka Doncic': 'PG', 'Damian Lillard': 'PG',
            'Chris Paul': 'PG', 'Russell Westbrook': 'PG', 'Kyrie Irving': 'PG',
            'Ja Morant': 'PG', 'Trae Young': 'PG', 'Darius Garland': 'PG',
            'De\'Aaron Fox': 'PG', 'LaMelo Ball': 'PG', 'Fred VanVleet': 'PG',
            'Mike Conley': 'PG', 'Jrue Holiday': 'PG', 'Marcus Smart': 'PG',
            'Cole Anthony': 'PG', 'Anthony Black': 'PG', 'Lonzo Ball': 'PG',
            
            # Shooting Guards  
            'James Harden': 'SG', 'Devin Booker': 'SG', 'Bradley Beal': 'SG',
            'Donovan Mitchell': 'SG', 'Zach LaVine': 'SG', 'Jaylen Brown': 'SG',
            'Anthony Edwards': 'SG', 'Tyler Herro': 'SG', 'CJ McCollum': 'SG',
            'Klay Thompson': 'SG', 'Jordan Poole': 'SG', 'Desmond Bane': 'SG',
            
            # Small Forwards
            'LeBron James': 'SF', 'Kevin Durant': 'SF', 'Kawhi Leonard': 'SF',
            'Jimmy Butler': 'SF', 'Paul George': 'SF', 'Jayson Tatum': 'SF',
            'Scottie Barnes': 'SF', 'Franz Wagner': 'SF', 'Mikal Bridges': 'SF',
            'OG Anunoby': 'SF', 'Harrison Barnes': 'SF', 'RJ Barrett': 'SF',
            
            # Power Forwards
            'Giannis Antetokounmpo': 'PF', 'Anthony Davis': 'PF', 'Draymond Green': 'PF',
            'Pascal Siakam': 'PF', 'Julius Randle': 'PF', 'Paolo Banchero': 'PF',
            'Jaren Jackson Jr.': 'PF', 'Evan Mobley': 'PF', 'Tobias Harris': 'PF',
            'John Collins': 'PF', 'Alperen Sengun': 'PF', 'Lauri Markkanen': 'PF',
            
            # Centers
            'Nikola Jokic': 'C', 'Joel Embiid': 'C', 'Rudy Gobert': 'C',
            'Karl-Anthony Towns': 'C', 'Bam Adebayo': 'C', 'Domantas Sabonis': 'C',
            'Myles Turner': 'C', 'Clint Capela': 'C', 'Robert Williams III': 'C',
            'Jarrett Allen': 'C', 'Brook Lopez': 'C', 'Kristaps Porzingis': 'C',
            'Deandre Ayton': 'C', 'Steven Adams': 'C', 'Adem Bona': 'C'
        }
        
        return position_mapping.get(player_name, 'SF')  # Default to SF if unknown
    
    def fetch_player_data(self, max_players: int = 50) -> pd.DataFrame:
        """
        Fetch NBA player game data using nba_api with enhanced validation
        ONLY returns real NBA player data - no synthetic fallback
        """
        if not NBA_API_AVAILABLE:
            raise RuntimeError("❌ NBA API is not available. Cannot proceed without real NBA data. "
                             "Please install nba_api: pip install nba_api")
        
        print(f"🏀 Fetching real NBA player data for up to {max_players} players...")
        all_game_data = []
        
        try:
            # Get active players from NBA API
            nba_players = players.get_active_players()
            
            if not nba_players:
                raise RuntimeError("❌ Failed to fetch active players from NBA API")
            
            print(f"✅ Found {len(nba_players)} active NBA players")
            
            # Limit to specified number of players
            selected_players = nba_players[:max_players]
            successful_fetches = 0
            
            for i, player in enumerate(selected_players):
                try:
                    player_name = player['full_name']
                    
                    # Validate player name
                    if not self.validate_player_name(player_name):
                        print(f"⚠️  Skipping invalid player name: {player_name}")
                        continue
                    
                    print(f"📊 Fetching data for {player_name} ({i+1}/{len(selected_players)})")
                    
                    # Rate limiting - 1 request per second
                    time.sleep(1.1)
                    
                    # Get player game log for current season
                    gamelog = playergamelog.PlayerGameLog(
                        player_id=player['id'],
                        season=self.current_season,
                        season_type_all_star='Regular Season'
                    )
                    
                    games_df = gamelog.get_data_frames()[0]
                    
                    if len(games_df) == 0:
                        print(f"⚠️  No games found for {player_name}")
                        continue
                    
                    # Add player info
                    games_df['player_name'] = player_name
                    games_df['player_id'] = player['id']
                    
                    # Get player position (try API first, then fallback)
                    position = self.get_player_position_from_api(player['id'])
                    if not position:
                        position = self.get_player_position_fallback(player_name)
                    
                    games_df['position'] = position
                    
                    # Calculate fantasy points for each game using CORRECTED formula
                    games_df['fantasy_points'] = games_df.apply(
                        lambda row: self.calculate_fantasy_points_correct({
                            'pts': row.get('PTS', 0),
                            'reb': row.get('REB', 0),
                            'ast': row.get('AST', 0),
                            'stl': row.get('STL', 0),
                            'blk': row.get('BLK', 0),
                            'tov': row.get('TOV', 0)
                        }), axis=1
                    )
                    
                    # Rename columns to match our schema
                    games_df = games_df.rename(columns={
                        'MIN': 'min', 'PTS': 'pts', 'AST': 'ast', 'REB': 'reb',
                        'STL': 'stl', 'BLK': 'blk', 'TOV': 'tov',
                        'FGM': 'fgm', 'FGA': 'fga', 'FG3M': 'fg3m', 'FG3A': 'fg3a',
                        'FTM': 'ftm', 'FTA': 'fta'
                    })
                    
                    all_game_data.append(games_df)
                    successful_fetches += 1
                    
                    print(f"✅ Successfully fetched {len(games_df)} games for {player_name}")
                    
                except Exception as e:
                    print(f"❌ Error fetching data for {player.get('full_name', 'Unknown')}: {str(e)}")
                    continue
            
            if not all_game_data:
                raise RuntimeError("❌ No valid player data could be fetched from NBA API. "
                                 "Please check your internet connection and try again.")
            
            # Combine all player data
            combined_df = pd.concat(all_game_data, ignore_index=True)
            
            # Clean and validate data
            combined_df = self.clean_and_engineer_features(combined_df)
            
            # Final validation - remove any remaining invalid player names
            valid_mask = combined_df['player_name'].apply(self.validate_player_name)
            combined_df = combined_df[valid_mask]
            
            if len(combined_df) == 0:
                raise RuntimeError("❌ No valid games remaining after data cleaning")
            
            print(f"✅ Successfully processed {len(combined_df)} games from {combined_df['player_name'].nunique()} real NBA players")
            print(f"📈 Data includes {successful_fetches} players with complete game logs")
            
            return combined_df
            
        except Exception as e:
            print(f"❌ Critical error in data fetching: {str(e)}")
            raise RuntimeError(f"Failed to fetch NBA data: {str(e)}")
    
    def clean_and_engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean data and engineer HISTORICAL efficiency features to eliminate ALL leakage
        CRITICAL: Uses rolling averages from PREVIOUS games only
        """
        print("🧹 Cleaning data and engineering HISTORICAL efficiency features...")
        print("🔧 ZERO LEAKAGE: Using only past game averages to predict future games")
        
        # Convert minutes to numeric (handle MM:SS format)
        if 'min' in df.columns:
            df['min'] = df['min'].apply(self.convert_minutes_to_numeric)
        
        # Fill NaN values with 0 for numeric columns
        numeric_cols = ['min', 'pts', 'ast', 'reb', 'stl', 'blk', 'tov', 
                       'fgm', 'fga', 'fg3m', 'fg3a', 'ftm', 'fta', 'fantasy_points']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Enhanced data validation
        initial_count = len(df)
        
        # Filter out invalid games
        df = df[df['min'] >= 10]  # At least 10 minutes played
        df = df[df['fantasy_points'].notna()]
        
        # Remove statistical outliers
        df = df[df['pts'] <= 80]   
        df = df[df['min'] <= 48]   
        df = df[df['ast'] <= 25]   
        df = df[df['reb'] <= 25]   
        df = df[df['stl'] <= 10]   
        df = df[df['blk'] <= 10]   
        
        # Remove games with negative stats
        for col in ['pts', 'ast', 'reb', 'stl', 'blk', 'fgm', 'fga', 'fg3m', 'fg3a', 'ftm', 'fta']:
            if col in df.columns:
                df = df[df[col] >= 0]
        
        # Validate shooting ratios
        if 'fga' in df.columns and 'fgm' in df.columns:
            df = df[df['fga'] >= df['fgm']]
        if 'fg3a' in df.columns and 'fg3m' in df.columns:
            df = df[df['fg3a'] >= df['fg3m']]
        if 'fta' in df.columns and 'ftm' in df.columns:
            df = df[df['fta'] >= df['ftm']]
        
        # Final player name validation
        df = df[df['player_name'].apply(self.validate_player_name)]
        
        # Sort by player and game order for rolling calculations
        if 'GAME_DATE' in df.columns:
            df = df.sort_values(['player_name', 'GAME_DATE']).reset_index(drop=True)
        else:
            df = df.sort_values(['player_name']).reset_index(drop=True)
        
        # CRITICAL: Calculate HISTORICAL efficiency features (NO SAME-GAME DATA)
        historical_features = []
        
        for player_name in df['player_name'].unique():
            player_games = df[df['player_name'] == player_name].copy()
            
            if len(player_games) < 5:  # Need at least 5 games for rolling averages
                continue
            
            # Calculate rolling averages using ONLY previous games
            player_games['hist_fg_pct'] = 0.0
            player_games['hist_fg3_pct'] = 0.0
            player_games['hist_ft_pct'] = 0.0
            player_games['hist_min_avg'] = 0.0
            player_games['hist_usage_rate'] = 0.0
            
            for i in range(len(player_games)):
                if i < 3:  # Skip first 3 games (need history)
                    continue
                
                # Use games 0 to i-1 (PREVIOUS games only) to predict game i
                prev_games = player_games.iloc[:i]
                
                # Calculate historical shooting percentages
                total_fgm = prev_games['fgm'].sum()
                total_fga = prev_games['fga'].sum()
                hist_fg_pct = total_fgm / total_fga if total_fga > 0 else 0.0
                
                total_fg3m = prev_games['fg3m'].sum()
                total_fg3a = prev_games['fg3a'].sum()
                hist_fg3_pct = total_fg3m / total_fg3a if total_fg3a > 0 else 0.0
                
                total_ftm = prev_games['ftm'].sum()
                total_fta = prev_games['fta'].sum()
                hist_ft_pct = total_ftm / total_fta if total_fta > 0 else 0.0
                
                # Calculate historical averages
                hist_min_avg = prev_games['min'].mean()
                hist_usage_rate = hist_min_avg / 48.0 if hist_min_avg > 0 else 0.0
                
                # Assign historical features to current game
                player_games.iloc[i, player_games.columns.get_loc('hist_fg_pct')] = hist_fg_pct
                player_games.iloc[i, player_games.columns.get_loc('hist_fg3_pct')] = hist_fg3_pct
                player_games.iloc[i, player_games.columns.get_loc('hist_ft_pct')] = hist_ft_pct
                player_games.iloc[i, player_games.columns.get_loc('hist_min_avg')] = hist_min_avg
                player_games.iloc[i, player_games.columns.get_loc('hist_usage_rate')] = hist_usage_rate
            
            # Only keep games with historical features (skip first 3 games)
            player_games_with_history = player_games.iloc[3:].copy()
            historical_features.append(player_games_with_history)
        
        if not historical_features:
            raise RuntimeError("❌ No games with sufficient history for feature engineering")
        
        # Combine all players with historical features
        df_with_history = pd.concat(historical_features, ignore_index=True)
        
        # Validate historical efficiency percentages (0-1 range)
        df_with_history = df_with_history[
            (df_with_history['hist_fg_pct'] >= 0) & (df_with_history['hist_fg_pct'] <= 1) &
            (df_with_history['hist_fg3_pct'] >= 0) & (df_with_history['hist_fg3_pct'] <= 1) &
            (df_with_history['hist_ft_pct'] >= 0) & (df_with_history['hist_ft_pct'] <= 1)
        ]
        
        final_count = len(df_with_history)
        removed_count = initial_count - final_count
        
        print(f"✅ Data cleaning complete: {removed_count} games removed, {final_count} games remaining")
        print(f"🎯 Created HISTORICAL features: hist_fg_pct, hist_fg3_pct, hist_ft_pct, hist_min_avg, hist_usage_rate")
        print(f"🔒 ZERO LEAKAGE: Each game uses only previous games' averages")
        
        return df_with_history
    
    def convert_minutes_to_numeric(self, minutes_str) -> float:
        """Convert MM:SS format to decimal minutes"""
        if pd.isna(minutes_str) or minutes_str == '':
            return 0.0
        
        try:
            if ':' in str(minutes_str):
                parts = str(minutes_str).split(':')
                return float(parts[0]) + float(parts[1]) / 60.0
            else:
                return float(minutes_str)
        except:
            return 0.0
    
    def prepare_training_data(self, game_data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prepare training data with temporal split to prevent data leakage
        """
        print("📚 Preparing training data with temporal validation...")
        
        # Sort by game chronologically
        if 'GAME_DATE' in game_data.columns:
            game_data_sorted = game_data.sort_values(['player_name', 'GAME_DATE'])
        else:
            # Use index as proxy for chronological order
            game_data_sorted = game_data.sort_values(['player_name']).reset_index(drop=True)
        
        # For each player, use first 80% of games for training, last 20% for testing
        train_data = []
        test_data = []
        
        for player_name in game_data_sorted['player_name'].unique():
            player_games = game_data_sorted[game_data_sorted['player_name'] == player_name]
            
            if len(player_games) < 15:  # Skip players with too few games
                continue
                
            split_idx = int(len(player_games) * 0.8)
            
            train_data.append(player_games.iloc[:split_idx])
            test_data.append(player_games.iloc[split_idx:])
        
        train_df = pd.concat(train_data, ignore_index=True) if train_data else pd.DataFrame()
        test_df = pd.concat(test_data, ignore_index=True) if test_data else pd.DataFrame()
        
        print(f"📊 Training data: {len(train_df)} games from {train_df['player_name'].nunique() if len(train_df) > 0 else 0} players")
        print(f"📊 Test data: {len(test_df)} games from {test_df['player_name'].nunique() if len(test_df) > 0 else 0} players")
        
        return train_df, test_df
    
    def train_position_models(self, train_data: pd.DataFrame):
        """
        Train multi-output models for each NBA position
        FIXED: Uses only shooting efficiency features to predict counting stats
        """
        print("\n🎯 Training FINAL LEAKAGE-FREE position-specific multi-output models...")
        print("🔧 Features: ONLY historical averages from PREVIOUS games")
        print("🎯 Targets: points, rebounds, assists, fantasy points")
        print("🔒 ZERO DATA LEAKAGE: No same-game information used")
        
        for position in ['PG', 'SG', 'SF', 'PF', 'C']:
            pos_data = train_data[train_data['position'] == position].copy()
            
            if len(pos_data) < 50:  # Need sufficient data for training
                print(f"⚠️  Skipping {position}: insufficient data ({len(pos_data)} games)")
                continue
            
            # Get position-specific features (ONLY efficiency metrics)
            features = self.position_configs[position]['features']
            available_features = [f for f in features if f in pos_data.columns]
            
            if len(available_features) < 5:
                print(f"⚠️  Skipping {position}: insufficient features available")
                continue
            
            # CRITICAL: Prepare features (shooting efficiency) and targets (counting stats)
            X = pos_data[available_features].fillna(0)
            y = pos_data[self.target_columns]
            
            # Remove any infinite or extremely large values
            X = X.replace([np.inf, -np.inf], 0)
            y = y.replace([np.inf, -np.inf], 0)
            
            # Filter reasonable ranges for all stats
            mask = (
                (y['pts'] >= 0) & (y['pts'] <= 60) &
                (y['reb'] >= 0) & (y['reb'] <= 25) &
                (y['ast'] >= 0) & (y['ast'] <= 20) &
                (y['fantasy_points'] >= 0) & (y['fantasy_points'] <= 150)
            )
            X, y = X[mask], y[mask]
            
            if len(X) < 30:
                print(f"⚠️  Skipping {position}: insufficient valid data after cleaning")
                continue
            
            # Create multi-output model
            model_params = self.position_configs[position]['model_params']
            base_model = RandomForestRegressor(**model_params)
            multi_model = MultiOutputRegressor(base_model)
            
            # Use TimeSeriesSplit for temporal validation
            tscv = TimeSeriesSplit(n_splits=3)
            cv_scores = {stat: [] for stat in self.target_columns}
            
            for train_idx, val_idx in tscv.split(X):
                X_train_cv, X_val_cv = X.iloc[train_idx], X.iloc[val_idx]
                y_train_cv, y_val_cv = y.iloc[train_idx], y.iloc[val_idx]
                
                model_cv = MultiOutputRegressor(RandomForestRegressor(**model_params))
                model_cv.fit(X_train_cv, y_train_cv)
                
                y_pred_cv = model_cv.predict(X_val_cv)
                
                # Calculate R² for each target
                for i, stat in enumerate(self.target_columns):
                    try:
                        cv_score = r2_score(y_val_cv.iloc[:, i], y_pred_cv[:, i])
                        cv_scores[stat].append(cv_score)
                    except:
                        cv_scores[stat].append(0.0)
            
            # Train final model on all training data
            multi_model.fit(X, y)
            
            # Store model and features
            self.models[position] = multi_model
            self.feature_columns[position] = available_features
            
            # Calculate training metrics for each target
            y_pred = multi_model.predict(X)
            
            metrics = {}
            for i, stat in enumerate(self.target_columns):
                r2 = r2_score(y.iloc[:, i], y_pred[:, i])
                mae = mean_absolute_error(y.iloc[:, i], y_pred[:, i])
                cv_mean = np.mean(cv_scores[stat]) if cv_scores[stat] else 0.0
                metrics[stat] = {'r2': r2, 'mae': mae, 'cv_r2': cv_mean}
            
            print(f"✅ {position}: {len(pos_data)} games, Features: {available_features}")
            print(f"   📊 PTS: R² = {metrics['pts']['r2']:.3f}, MAE = {metrics['pts']['mae']:.1f}, CV R² = {metrics['pts']['cv_r2']:.3f}")
            print(f"   📊 REB: R² = {metrics['reb']['r2']:.3f}, MAE = {metrics['reb']['mae']:.1f}, CV R² = {metrics['reb']['cv_r2']:.3f}")
            print(f"   📊 AST: R² = {metrics['ast']['r2']:.3f}, MAE = {metrics['ast']['mae']:.1f}, CV R² = {metrics['ast']['cv_r2']:.3f}")
            print(f"   📊 FAN: R² = {metrics['fantasy_points']['r2']:.3f}, MAE = {metrics['fantasy_points']['mae']:.1f}, CV R² = {metrics['fantasy_points']['cv_r2']:.3f}")
            
            # Warning if performance is suspiciously high (possible remaining leakage)
            if metrics['pts']['r2'] > 0.95 or metrics['reb']['r2'] > 0.95 or metrics['ast']['r2'] > 0.95:
                print(f"   ⚠️  WARNING: Suspiciously high R² values - check for data leakage!")
    
    def predict_player_performance(self, player_stats: Dict) -> Optional[Dict]:
        """
        Predict individual stats and fantasy points using ONLY historical averages
        """
        position = player_stats.get('position')
        
        if position not in self.models:
            return None
        
        # Get features for this position (ONLY historical averages)
        features = self.feature_columns[position]
        
        try:
            # Extract feature values (historical averages only)
            feature_values = []
            for feat in features:
                if feat in player_stats:
                    feature_values.append(player_stats[feat])
                else:
                    # Default values for missing historical features
                    if feat in ['hist_fg_pct', 'hist_fg3_pct', 'hist_ft_pct']:
                        feature_values.append(0.45)  # Default shooting percentage
                    elif feat == 'hist_min_avg':
                        feature_values.append(25.0)  # Default minutes
                    elif feat == 'hist_usage_rate':
                        feature_values.append(0.52)  # Default usage rate (25/48)
                    else:
                        feature_values.append(0.0)
            
            X = np.array(feature_values).reshape(1, -1)
            predictions = self.models[position].predict(X)[0]
            
            # Ensure non-negative predictions and round appropriately
            predicted_stats = {
                'pts': round(max(0, predictions[0]), 1),
                'reb': round(max(0, predictions[1]), 1),
                'ast': round(max(0, predictions[2]), 1),
                'fantasy_points': round(max(0, predictions[3]), 2)
            }
            
            # Verify consistency: calculate fantasy points from predicted stats
            # (Note: This is simplified since we don't predict stl, blk, tov separately)
            calculated_fantasy = self.calculate_fantasy_points_correct({
                'pts': predicted_stats['pts'],
                'reb': predicted_stats['reb'],
                'ast': predicted_stats['ast'],
                'stl': 1.0,  # Assume average steals
                'blk': 0.5,  # Assume average blocks
                'tov': 2.0   # Assume average turnovers
            })
            
            # Use model's fantasy prediction but validate it's reasonable
            if abs(predicted_stats['fantasy_points'] - calculated_fantasy) > 10:
                predicted_stats['fantasy_points'] = calculated_fantasy
            
            return predicted_stats
            
        except Exception as e:
            print(f"❌ Error predicting for {position}: {str(e)}")
            return None
    
    def evaluate_models(self, test_data: pd.DataFrame) -> pd.DataFrame:
        """Evaluate trained multi-output models on test data with realistic expectations"""
        print("\n📈 Evaluating FIXED multi-output models on test data...")
        print("🎯 Expecting REALISTIC performance (no perfect predictions)")
        
        results = []
        
        for _, game in test_data.iterrows():
            player_stats = game.to_dict()
            predicted_stats = self.predict_player_performance(player_stats)
            
            if predicted_stats is not None:
                results.append({
                    'player_name': game['player_name'],
                    'position': game['position'],
                    'actual_pts': game['pts'],
                    'actual_reb': game['reb'],
                    'actual_ast': game['ast'],
                    'actual_fantasy_points': game['fantasy_points'],
                    'predicted_pts': predicted_stats['pts'],
                    'predicted_reb': predicted_stats['reb'],
                    'predicted_ast': predicted_stats['ast'],
                    'predicted_fantasy_points': predicted_stats['fantasy_points']
                })
        
        results_df = pd.DataFrame(results)
        
        if len(results_df) > 0:
            # Calculate comprehensive metrics for each stat
            stats_metrics = {}
            
            for stat in ['pts', 'reb', 'ast', 'fantasy_points']:
                actual_col = f'actual_{stat}'
                predicted_col = f'predicted_{stat}'
                
                mae = mean_absolute_error(results_df[actual_col], results_df[predicted_col])
                rmse = np.sqrt(mean_squared_error(results_df[actual_col], results_df[predicted_col]))
                r2 = r2_score(results_df[actual_col], results_df[predicted_col])
                
                # Calculate accuracy within realistic thresholds
                if stat == 'pts':
                    threshold = 6  # Within 6 points
                elif stat == 'reb':
                    threshold = 3  # Within 3 rebounds
                elif stat == 'ast':
                    threshold = 3  # Within 3 assists
                else:  # fantasy_points
                    threshold = 8  # Within 8 fantasy points
                
                within_threshold = np.abs(results_df[actual_col] - results_df[predicted_col]) <= threshold
                accuracy_pct = (within_threshold.sum() / len(results_df)) * 100
                
                # Calculate perfect match percentage (should be very low now)
                perfect_matches = (results_df[actual_col] == results_df[predicted_col]).sum()
                perfect_pct = (perfect_matches / len(results_df)) * 100
                
                stats_metrics[stat] = {
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2,
                    'accuracy_pct': accuracy_pct,
                    'threshold': threshold,
                    'perfect_pct': perfect_pct
                }
            
            # Print comprehensive results
            print(f"\n📊 FIXED MODEL PERFORMANCE (REALISTIC EXPECTATIONS):")
            print("=" * 70)
            for stat in ['pts', 'reb', 'ast', 'fantasy_points']:
                m = stats_metrics[stat]
                stat_name = stat.upper().replace('_', ' ')
                print(f"{stat_name:12} | MAE: {m['mae']:5.2f} | R²: {m['r2']:5.3f} | Within {m['threshold']}: {m['accuracy_pct']:5.1f}% | Perfect: {m['perfect_pct']:4.1f}%")
            
            print(f"\n🎯 Total predictions: {len(results_df)}")
            print(f"👥 Players analyzed: {results_df['player_name'].nunique()}")
            
            # Performance quality assessment
            avg_r2 = np.mean([stats_metrics[stat]['r2'] for stat in ['pts', 'reb', 'ast']])
            perfect_avg = np.mean([stats_metrics[stat]['perfect_pct'] for stat in ['pts', 'reb', 'ast']])
            
            print(f"\n🔍 QUALITY ASSESSMENT:")
            print(f"   Average R²: {avg_r2:.3f}")
            print(f"   Perfect matches: {perfect_avg:.1f}% (should be <5%)")
            
            if perfect_avg > 10:
                print("   ⚠️  WARNING: Too many perfect matches - possible remaining data leakage!")
            elif avg_r2 > 0.90:
                print("   ⚠️  WARNING: R² too high - check for data leakage!")
            elif avg_r2 < 0.30:
                print("   ⚠️  WARNING: R² very low - model may need more features!")
            else:
                print("   ✅ Performance looks realistic for shooting-based predictions!")
        
        return results_df
    
    def save_models(self):
        """Save trained FIXED models to disk"""
        print("\n💾 Saving FIXED trained models...")
        
        for position, model in self.models.items():
            filename = f'nba_{position.lower()}_model_fixed.pkl'
            joblib.dump({
                'model': model,
                'features': self.feature_columns[position],
                'config': self.position_configs[position],
                'model_type': 'fixed_no_leakage',
                'created_date': datetime.now().isoformat()
            }, filename)
            print(f"✅ Saved FIXED {position} model to {filename}")
    
    def load_models(self):
        """Load trained FIXED models from disk"""
        print("📂 Loading FIXED trained models...")
        
        for position in ['PG', 'SG', 'SF', 'PF', 'C']:
            filename = f'nba_{position.lower()}_model_fixed.pkl'
            try:
                model_data = joblib.load(filename)
                self.models[position] = model_data['model']
                self.feature_columns[position] = model_data['features']
                print(f"✅ Loaded FIXED {position} model from {filename}")
            except FileNotFoundError:
                print(f"⚠️  FIXED model file not found: {filename}")
            except Exception as e:
                print(f"❌ Error loading FIXED {position} model: {str(e)}")

def main():
    """Main training and evaluation pipeline for FIXED model"""
    print("🏀 NBA FANTASY POINTS PREDICTION SYSTEM - FINAL LEAKAGE-FREE VERSION")
    print("=" * 70)
    print("🎯 Using ONLY historical averages from previous games")
    print("🔒 ZERO DATA LEAKAGE - No same-game information used")
    print("📊 Expecting realistic performance (R² 0.2-0.6, MAE 3-7)")
    
    try:
        # Initialize FIXED model
        model = NBAPlayerProjectionModelFixed()
        
        # Fetch real NBA data
        print("\n📊 STEP 1: Fetching Real NBA Player Data")
        game_data = model.fetch_player_data(max_players=40)  # Smaller dataset for testing
        
        # Prepare training data
        print("\n📚 STEP 2: Preparing Training Data with Temporal Split")
        train_data, test_data = model.prepare_training_data(game_data)
        
        if len(train_data) == 0:
            raise RuntimeError("❌ No training data available")
        
        # Train FIXED models
        print("\n🎯 STEP 3: Training FIXED Position-Specific Models")
        model.train_position_models(train_data)
        
        # Evaluate FIXED models
        print("\n📈 STEP 4: Evaluating FIXED Models")
        results_df = model.evaluate_models(test_data)
        
        # Save results
        results_file = 'inference_results_fixed.csv'
        results_df.to_csv(results_file, index=False)
        print(f"💾 FIXED results saved to {results_file}")
        
        # Save FIXED models
        print("\n💾 STEP 5: Saving FIXED Models")
        model.save_models()
        
        print("\n✅ FINAL LEAKAGE-FREE NBA PREDICTION SYSTEM COMPLETE!")
        print("🎯 Features: historical averages from previous games only")
        print("🎯 Targets: points, rebounds, assists, fantasy points")
        print("🔒 ZERO DATA LEAKAGE: True predictive model")
        print(f"📊 Total predictions: {len(results_df)}")
        print(f"👥 Players analyzed: {results_df['player_name'].nunique()}")
        
        # Final validation check
        if len(results_df) > 0:
            perfect_pts = (results_df['actual_pts'] == results_df['predicted_pts']).sum()
            perfect_pct = (perfect_pts / len(results_df)) * 100
            
            if perfect_pct > 10:
                print(f"⚠️  WARNING: {perfect_pct:.1f}% perfect point predictions - check for remaining leakage!")
            else:
                print(f"✅ Perfect predictions: {perfect_pct:.1f}% (realistic level)")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        print("💡 Please ensure:")
        print("   1. NBA API is installed: pip install nba_api")
        print("   2. Internet connection is stable")
        print("   3. NBA API servers are accessible")
        raise

if __name__ == "__main__":
    main()
