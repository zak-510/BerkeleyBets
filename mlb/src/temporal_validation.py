#!/usr/bin/env python3
"""
MLB Temporal Validation Framework
Ensures strict chronological ordering and prevents data leakage
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class TemporalValidator:
    def __init__(self):
        """Initialize temporal validator"""
        self.validation_errors = []
        self.warnings = []
        
    def validate_game_logs(self, game_logs: pd.DataFrame, player_id: int, 
                          player_name: str) -> Dict:
        """
        Validate game logs for temporal integrity
        
        Args:
            game_logs: DataFrame with game-level data
            player_id: MLB player ID
            player_name: Player name for reporting
            
        Returns:
            Validation report
        """
        print(f"🔍 Validating temporal integrity for {player_name}")
        
        validation_report = {
            'player_id': player_id,
            'player_name': player_name,
            'total_games': len(game_logs),
            'date_range': None,
            'temporal_issues': [],
            'is_valid': True,
            'recommendations': []
        }
        
        if len(game_logs) == 0:
            validation_report['temporal_issues'].append("No games found")
            validation_report['is_valid'] = False
            return validation_report
        
        # Ensure game_date is datetime
        if 'game_date' in game_logs.columns:
            game_logs['game_date'] = pd.to_datetime(game_logs['game_date'])
            
            # Check chronological ordering
            self._check_chronological_order(game_logs, validation_report)
            
            # Check for date range
            min_date = game_logs['game_date'].min()
            max_date = game_logs['game_date'].max()
            validation_report['date_range'] = f"{min_date.date()} to {max_date.date()}"
            
            # Check for reasonable date gaps
            self._check_date_gaps(game_logs, validation_report)
            
            # Check for future dates
            self._check_future_dates(game_logs, validation_report)
            
        else:
            validation_report['temporal_issues'].append("Missing game_date column")
            validation_report['is_valid'] = False
        
        # Check for data consistency
        self._check_data_consistency(game_logs, validation_report)
        
        # Generate recommendations
        self._generate_recommendations(validation_report)
        
        return validation_report
    
    def _check_chronological_order(self, game_logs: pd.DataFrame, report: Dict):
        """Check if games are in chronological order"""
        sorted_logs = game_logs.sort_values('game_date')
        
        if not game_logs['game_date'].equals(sorted_logs['game_date']):
            report['temporal_issues'].append("Games not in chronological order")
            report['is_valid'] = False
            
            # Sort the data for further validation
            game_logs.sort_values('game_date', inplace=True)
            game_logs.reset_index(drop=True, inplace=True)
    
    def _check_date_gaps(self, game_logs: pd.DataFrame, report: Dict):
        """Check for unusual gaps in game dates"""
        if len(game_logs) < 2:
            return
        
        dates = game_logs['game_date'].sort_values()
        gaps = dates.diff().dt.days
        
        # Flag gaps longer than 14 days (unusual for active players)
        large_gaps = gaps[gaps > 14]
        if len(large_gaps) > 0:
            max_gap = large_gaps.max()
            report['temporal_issues'].append(f"Large date gap found: {max_gap} days")
            
        # Flag if too many games on same date (suspicious)
        same_date_counts = game_logs['game_date'].value_counts()
        multiple_games = same_date_counts[same_date_counts > 2]
        if len(multiple_games) > 0:
            report['temporal_issues'].append(f"Multiple games on same date: {len(multiple_games)} dates")
    
    def _check_future_dates(self, game_logs: pd.DataFrame, report: Dict):
        """Check for games in the future (data leakage indicator)"""
        today = datetime.now().date()
        future_games = game_logs[game_logs['game_date'].dt.date > today]
        
        if len(future_games) > 0:
            report['temporal_issues'].append(f"Found {len(future_games)} games in the future")
            report['is_valid'] = False
    
    def _check_data_consistency(self, game_logs: pd.DataFrame, report: Dict):
        """Check for data consistency issues"""
        # Check for negative fantasy points that are too extreme
        if 'fantasy_points' in game_logs.columns:
            extreme_negative = game_logs[game_logs['fantasy_points'] < -20]
            if len(extreme_negative) > 0:
                report['temporal_issues'].append(f"Found {len(extreme_negative)} games with extreme negative fantasy points")
            
            # Check for unrealistic fantasy points
            extreme_positive = game_logs[game_logs['fantasy_points'] > 50]
            if len(extreme_positive) > 0:
                report['temporal_issues'].append(f"Found {len(extreme_positive)} games with extreme positive fantasy points")
        
        # Check for missing data
        missing_data = game_logs.isnull().sum()
        critical_columns = ['game_date', 'fantasy_points']
        for col in critical_columns:
            if col in missing_data and missing_data[col] > 0:
                report['temporal_issues'].append(f"Missing data in {col}: {missing_data[col]} games")
    
    def _generate_recommendations(self, report: Dict):
        """Generate recommendations based on validation results"""
        if not report['is_valid']:
            report['recommendations'].append("Fix temporal validation issues before using data")
        
        if report['total_games'] < 10:
            report['recommendations'].append("Consider collecting more games for better model training")
        
        if len(report['temporal_issues']) == 0:
            report['recommendations'].append("Data passes temporal validation - ready for feature engineering")
    
    def create_temporal_splits(self, game_logs: pd.DataFrame, 
                              train_ratio: float = 0.8) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Create temporal train/test splits (no random splitting!)
        
        Args:
            game_logs: DataFrame with game logs
            train_ratio: Ratio of games for training (earliest games)
            
        Returns:
            Tuple of (train_data, test_data)
        """
        if len(game_logs) == 0:
            return pd.DataFrame(), pd.DataFrame()
        
        # Ensure chronological order
        game_logs_sorted = game_logs.sort_values('game_date').reset_index(drop=True)
        
        # Calculate split point
        split_point = int(len(game_logs_sorted) * train_ratio)
        
        train_data = game_logs_sorted.iloc[:split_point].copy()
        test_data = game_logs_sorted.iloc[split_point:].copy()
        
        print(f"📊 Temporal split: {len(train_data)} train games, {len(test_data)} test games")
        
        return train_data, test_data
    
    def generate_historical_features(self, game_logs: pd.DataFrame, 
                                   lookback_window: int = 15) -> pd.DataFrame:
        """
        Generate historical features with strict temporal ordering
        ENHANCED: Now includes position-specific raw game statistics
        
        Args:
            game_logs: DataFrame with game logs (must be chronologically ordered)
            lookback_window: Number of previous games to use for features
            
        Returns:
            DataFrame with historical features added
        """
        print(f"🔄 Generating historical features with {lookback_window}-game lookback")
        
        # Ensure chronological order
        game_logs_sorted = game_logs.sort_values('game_date').reset_index(drop=True)
        
        # Initialize feature columns (historical averages)
        feature_columns = [
            'avg_fantasy_points_L15',
            'avg_fantasy_points_L10', 
            'avg_fantasy_points_L5',
            'games_since_last_good_game',
            'trend_last_5_games',
            'consistency_score'
        ]
        
        for col in feature_columns:
            game_logs_sorted[col] = np.nan
        
        # ENHANCED: Detect if this is pitcher data and preserve raw stats
        is_pitcher_data = any(col in game_logs_sorted.columns for col in 
                             ['innings_pitched', 'hits_allowed', 'walks_allowed', 'strikeouts'])
        
        if is_pitcher_data:
            print("🎯 Detected pitcher data - preserving raw game statistics")
            # Ensure pitcher-specific columns exist
            pitcher_stats = ['innings_pitched', 'hits_allowed', 'home_runs_allowed', 
                           'walks_allowed', 'total_batters', 'strikeouts']
            for stat in pitcher_stats:
                if stat not in game_logs_sorted.columns:
                    game_logs_sorted[stat] = 0
        else:
            print("🏏 Detected batter data - preserving batting statistics")
            # Ensure batter-specific columns exist
            batter_stats = ['at_bats', 'hits', 'doubles', 'triples', 'home_runs', 
                          'walks', 'strikeouts', 'hit_by_pitch', 'batting_avg']
            for stat in batter_stats:
                if stat not in game_logs_sorted.columns:
                    if stat == 'batting_avg':
                        game_logs_sorted[stat] = 0.0
                    else:
                        game_logs_sorted[stat] = 0
        
        # Generate features for each game (using only previous games)
        for i in range(len(game_logs_sorted)):
            if i == 0:
                continue  # No historical data for first game
            
            # Get previous games only (strict temporal ordering)
            prev_games = game_logs_sorted.iloc[:i]
            
            if len(prev_games) > 0:
                # Average fantasy points over different windows
                game_logs_sorted.loc[i, 'avg_fantasy_points_L15'] = prev_games['fantasy_points'].tail(15).mean()
                game_logs_sorted.loc[i, 'avg_fantasy_points_L10'] = prev_games['fantasy_points'].tail(10).mean()
                game_logs_sorted.loc[i, 'avg_fantasy_points_L5'] = prev_games['fantasy_points'].tail(5).mean()
                
                # Games since last "good" game (>10 fantasy points)
                good_games = prev_games[prev_games['fantasy_points'] > 10]
                if len(good_games) > 0:
                    last_good_game_idx = good_games.index[-1]
                    games_since = i - last_good_game_idx - 1
                    game_logs_sorted.loc[i, 'games_since_last_good_game'] = games_since
                else:
                    game_logs_sorted.loc[i, 'games_since_last_good_game'] = i
                
                # Trend in last 5 games (slope of fantasy points)
                if len(prev_games) >= 5:
                    last_5_points = prev_games['fantasy_points'].tail(5).values
                    x = np.arange(len(last_5_points))
                    trend = np.polyfit(x, last_5_points, 1)[0]
                    game_logs_sorted.loc[i, 'trend_last_5_games'] = trend
                
                # Consistency score (inverse of standard deviation)
                if len(prev_games) >= 3:
                    std_dev = prev_games['fantasy_points'].std()
                    consistency = 1 / (1 + std_dev)  # Higher = more consistent
                    game_logs_sorted.loc[i, 'consistency_score'] = consistency
        
        print(f"✅ Generated historical features for {len(game_logs_sorted)} games")
        return game_logs_sorted
    
    def validate_feature_integrity(self, featured_data: pd.DataFrame) -> Dict:
        """
        Validate that historical features don't contain data leakage
        
        Args:
            featured_data: DataFrame with historical features
            
        Returns:
            Validation report
        """
        validation_report = {
            'total_games': len(featured_data),
            'leakage_issues': [],
            'is_valid': True,
            'feature_coverage': {}
        }
        
        print(f"🔍 Validating feature integrity for {len(featured_data)} games")
        
        # Check that first game has no historical features (should be NaN)
        if len(featured_data) > 0:
            first_game = featured_data.iloc[0]
            historical_features = [col for col in featured_data.columns if 'avg_' in col or 'trend_' in col or 'consistency_' in col]
            
            for feature in historical_features:
                if not pd.isna(first_game[feature]):
                    validation_report['leakage_issues'].append(f"First game has {feature} value (should be NaN)")
                    validation_report['is_valid'] = False
        
        # Check feature coverage (how many games have complete features)
        for feature in historical_features:
            non_null_count = featured_data[feature].notna().sum()
            coverage = non_null_count / len(featured_data) * 100 if len(featured_data) > 0 else 0
            validation_report['feature_coverage'][feature] = coverage
        
        # Check for any impossible values
        if 'games_since_last_good_game' in featured_data.columns:
            impossible_values = featured_data[featured_data['games_since_last_good_game'] < 0]
            if len(impossible_values) > 0:
                validation_report['leakage_issues'].append("Found negative 'games_since_last_good_game' values")
                validation_report['is_valid'] = False
        
        return validation_report
    
    def validate_temporal_integrity(self, features_df: pd.DataFrame) -> Dict:
        """
        Comprehensive temporal integrity validation for the entire dataset
        
        Args:
            features_df: DataFrame with features and target variables
            
        Returns:
            Dictionary with validation results
        """
        print("🔍 Validating temporal integrity of complete dataset...")
        
        validation_results = {
            'total_rows': len(features_df),
            'unique_players': features_df['player_id'].nunique() if 'player_id' in features_df.columns else 0,
            'date_range': None,
            'chronological_order': True,
            'leakage_detected': False,
            'feature_integrity': True,
            'issues': [],
            'warnings': []
        }
        
        if len(features_df) == 0:
            validation_results['issues'].append("No data to validate")
            return validation_results
        
        # Check date range
        if 'game_date' in features_df.columns:
            features_df['game_date'] = pd.to_datetime(features_df['game_date'])
            min_date = features_df['game_date'].min()
            max_date = features_df['game_date'].max()
            validation_results['date_range'] = f"{min_date.date()} to {max_date.date()}"
            
            # Check for future dates (data leakage)
            today = datetime.now().date()
            future_games = features_df[features_df['game_date'].dt.date > today]
            if len(future_games) > 0:
                validation_results['leakage_detected'] = True
                validation_results['issues'].append(f"Found {len(future_games)} games in the future")
        
        # Check chronological order per player
        if 'player_id' in features_df.columns and 'game_date' in features_df.columns:
            for player_id in features_df['player_id'].unique():
                player_data = features_df[features_df['player_id'] == player_id].copy()
                if len(player_data) > 1:
                    sorted_data = player_data.sort_values('game_date')
                    if not player_data['game_date'].equals(sorted_data['game_date']):
                        validation_results['chronological_order'] = False
                        validation_results['issues'].append(f"Player {player_id} games not in chronological order")
        
        # Check for data leakage in features
        feature_cols = [col for col in features_df.columns if col.startswith(('avg_', 'recent_'))]
        
        # First game should have NaN features (no historical data)
        if len(feature_cols) > 0:
            for player_id in features_df['player_id'].unique():
                player_data = features_df[features_df['player_id'] == player_id].sort_values('game_date')
                if len(player_data) > 0:
                    first_game = player_data.iloc[0]
                    non_null_features = sum(1 for col in feature_cols if pd.notna(first_game[col]))
                    
                    if non_null_features > 0:
                        validation_results['leakage_detected'] = True
                        validation_results['issues'].append(f"Player {player_id} first game has {non_null_features} non-null features (possible leakage)")
        
        # Check feature integrity
        if 'fantasy_points' in features_df.columns:
            # Check for extreme values
            extreme_low = features_df[features_df['fantasy_points'] < -30]
            extreme_high = features_df[features_df['fantasy_points'] > 60]
            
            if len(extreme_low) > 0:
                validation_results['warnings'].append(f"Found {len(extreme_low)} games with fantasy points < -30")
            if len(extreme_high) > 0:
                validation_results['warnings'].append(f"Found {len(extreme_high)} games with fantasy points > 60")
            
            # Check for missing targets
            missing_targets = features_df['fantasy_points'].isnull().sum()
            if missing_targets > 0:
                validation_results['feature_integrity'] = False
                validation_results['issues'].append(f"Found {missing_targets} games with missing fantasy points")
        
        # Summary assessment
        if len(validation_results['issues']) == 0:
            print("✅ Temporal integrity validation passed")
        else:
            print(f"❌ Temporal integrity validation failed: {len(validation_results['issues'])} issues")
            for issue in validation_results['issues']:
                print(f"  • {issue}")
        
        if len(validation_results['warnings']) > 0:
            print(f"⚠️ Warnings:")
            for warning in validation_results['warnings']:
                print(f"  • {warning}")
        
        return validation_results
    
    def get_validation_summary(self) -> Dict:
        """Get summary of all validation checks performed"""
        return {
            'total_errors': len(self.validation_errors),
            'total_warnings': len(self.warnings),
            'errors': self.validation_errors,
            'warnings': self.warnings
        }

def test_temporal_validation():
    """Test the temporal validation system"""
    print("🧪 TESTING TEMPORAL VALIDATION SYSTEM")
    print("=" * 50)
    
    # Create sample game logs
    dates = pd.date_range('2024-09-01', '2024-09-15', freq='D')
    sample_data = pd.DataFrame({
        'game_date': dates,
        'player_id': [592450] * len(dates),
        'fantasy_points': np.random.normal(8, 5, len(dates)),  # Mean 8, std 5
        'at_bats': np.random.randint(3, 6, len(dates))
    })
    
    validator = TemporalValidator()
    
    # Test validation
    report = validator.validate_game_logs(sample_data, 592450, "Test Player")
    print(f"✅ Validation report: {report['is_valid']}")
    print(f"📊 Issues found: {len(report['temporal_issues'])}")
    
    # Test temporal splits
    train, test = validator.create_temporal_splits(sample_data, train_ratio=0.8)
    print(f"📈 Split: {len(train)} train, {len(test)} test")
    
    # Test feature generation
    featured_data = validator.generate_historical_features(sample_data, lookback_window=10)
    print(f"🔄 Features generated for {len(featured_data)} games")
    
    # Test feature integrity
    feature_report = validator.validate_feature_integrity(featured_data)
    print(f"✅ Feature validation: {feature_report['is_valid']}")
    
    return validator

if __name__ == "__main__":
    test_temporal_validation() 