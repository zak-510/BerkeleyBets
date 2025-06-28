#!/usr/bin/env python3
"""
MLB Feature Configuration Module
Centralized feature definitions for all positions and model training
"""

from typing import Dict, List
from enum import Enum


class PositionType(Enum):
    """Position type enumeration"""
    BATTER = "batter"
    PITCHER = "pitcher"


class MLBFeatureConfig:
    """Centralized configuration for MLB model features"""
    
    # Core historical features (used by all positions)
    CORE_HISTORICAL_FEATURES = [
        'avg_fantasy_points_L15',   # Average fantasy points over last 15 games
        'avg_fantasy_points_L10',   # Average fantasy points over last 10 games
        'avg_fantasy_points_L5',    # Average fantasy points over last 5 games
        'games_since_last_good_game',  # Games since scoring >10 fantasy points
        'trend_last_5_games',       # Trend in fantasy points (slope)
        'consistency_score'         # Inverse of standard deviation
    ]
    
    # Batter-specific raw game statistics
    BATTER_GAME_STATS = [
        'at_bats',
        'hits',
        'doubles',
        'triples', 
        'home_runs',
        'walks',
        'strikeouts',
        'hit_by_pitch',
        'batting_avg'
    ]
    
    # Pitcher-specific raw game statistics
    PITCHER_GAME_STATS = [
        'innings_pitched',
        'hits_allowed',
        'home_runs_allowed',
        'walks_allowed',
        'strikeouts',
        'total_batters'
    ]
    
    # Position-specific feature sets
    POSITION_FEATURES = {
        'C': CORE_HISTORICAL_FEATURES + BATTER_GAME_STATS,     # Catcher
        '1B': CORE_HISTORICAL_FEATURES + BATTER_GAME_STATS,    # First Base
        '2B': CORE_HISTORICAL_FEATURES + BATTER_GAME_STATS,    # Second Base
        '3B': CORE_HISTORICAL_FEATURES + BATTER_GAME_STATS,    # Third Base
        'SS': CORE_HISTORICAL_FEATURES + BATTER_GAME_STATS,    # Shortstop
        'OF': CORE_HISTORICAL_FEATURES + BATTER_GAME_STATS,    # Outfield
        'P': CORE_HISTORICAL_FEATURES + PITCHER_GAME_STATS     # Pitcher
    }
    
    # Minimum feature requirements for model training
    MIN_FEATURES_REQUIRED = {
        'batter_positions': 4,  # Minimum features for batter models
        'pitcher_positions': 3  # Minimum features for pitcher models
    }
    
    # Feature importance thresholds
    FEATURE_IMPORTANCE_THRESHOLDS = {
        'high_importance': 0.1,     # Features with >10% importance
        'medium_importance': 0.05,  # Features with >5% importance
        'low_importance': 0.01      # Features with >1% importance
    }
    
    @classmethod
    def get_features_for_position(cls, position: str) -> List[str]:
        """
        Get the feature list for a specific position
        
        Args:
            position: Position code (C, 1B, 2B, 3B, SS, OF, P)
            
        Returns:
            List of feature names for that position
        """
        return cls.POSITION_FEATURES.get(position, cls.CORE_HISTORICAL_FEATURES)
    
    @classmethod
    def get_position_type(cls, position: str) -> PositionType:
        """
        Determine if a position is a batter or pitcher
        
        Args:
            position: Position code
            
        Returns:
            PositionType enum value
        """
        if position == 'P':
            return PositionType.PITCHER
        else:
            return PositionType.BATTER
    
    @classmethod
    def validate_features(cls, position: str, available_features: List[str]) -> Dict:
        """
        Validate that required features are available for a position
        
        Args:
            position: Position code
            available_features: List of features available in the dataset
            
        Returns:
            Dictionary with validation results
        """
        required_features = cls.get_features_for_position(position)
        position_type = cls.get_position_type(position)
        
        # Check which required features are available
        available_required = [f for f in required_features if f in available_features]
        missing_features = [f for f in required_features if f not in available_features]
        
        # Determine minimum threshold
        min_threshold = (cls.MIN_FEATURES_REQUIRED['pitcher_positions'] 
                        if position_type == PositionType.PITCHER 
                        else cls.MIN_FEATURES_REQUIRED['batter_positions'])
        
        validation_result = {
            'position': position,
            'position_type': position_type.value,
            'required_features': required_features,
            'available_features': available_required,
            'missing_features': missing_features,
            'total_required': len(required_features),
            'total_available': len(available_required),
            'coverage_percentage': len(available_required) / len(required_features) * 100,
            'meets_minimum': len(available_required) >= min_threshold,
            'minimum_threshold': min_threshold,
            'is_valid': len(available_required) >= min_threshold
        }
        
        return validation_result
    
    @classmethod
    def get_core_features_only(cls) -> List[str]:
        """Get only the core historical features (no raw game stats)"""
        return cls.CORE_HISTORICAL_FEATURES.copy()
    
    @classmethod
    def get_batter_features(cls) -> List[str]:
        """Get all batter-related features"""
        return cls.CORE_HISTORICAL_FEATURES + cls.BATTER_GAME_STATS
    
    @classmethod
    def get_pitcher_features(cls) -> List[str]:
        """Get all pitcher-related features"""
        return cls.CORE_HISTORICAL_FEATURES + cls.PITCHER_GAME_STATS
    
    @classmethod
    def filter_features_by_availability(cls, position: str, dataset_columns: List[str], 
                                       min_coverage: float = 0.7) -> List[str]:
        """
        Filter features based on availability in dataset
        
        Args:
            position: Position code
            dataset_columns: Available columns in the dataset
            min_coverage: Minimum coverage required to include a feature
            
        Returns:
            List of features that meet availability criteria
        """
        required_features = cls.get_features_for_position(position)
        
        # Only return features that exist in the dataset
        available_features = [f for f in required_features if f in dataset_columns]
        
        # Ensure we meet minimum requirements
        validation = cls.validate_features(position, available_features)
        
        if not validation['is_valid']:
            # If we don't meet minimum, return at least the core features that are available
            core_available = [f for f in cls.CORE_HISTORICAL_FEATURES if f in dataset_columns]
            return core_available
        
        return available_features
    
    @classmethod
    def get_feature_groups(cls) -> Dict[str, List[str]]:
        """Get features organized by logical groups"""
        return {
            'historical_performance': cls.CORE_HISTORICAL_FEATURES,
            'batter_stats': cls.BATTER_GAME_STATS,
            'pitcher_stats': cls.PITCHER_GAME_STATS
        }
    
    @classmethod
    def get_all_possible_features(cls) -> List[str]:
        """Get complete list of all possible features"""
        all_features = set(cls.CORE_HISTORICAL_FEATURES)
        all_features.update(cls.BATTER_GAME_STATS)
        all_features.update(cls.PITCHER_GAME_STATS)
        return sorted(list(all_features))
    
    @classmethod
    def get_feature_descriptions(cls) -> Dict[str, str]:
        """Get human-readable descriptions for all features"""
        return {
            # Historical features
            'avg_fantasy_points_L15': 'Average fantasy points over last 15 games',
            'avg_fantasy_points_L10': 'Average fantasy points over last 10 games', 
            'avg_fantasy_points_L5': 'Average fantasy points over last 5 games',
            'games_since_last_good_game': 'Games since scoring >10 fantasy points',
            'trend_last_5_games': 'Trend in fantasy points (positive = improving)',
            'consistency_score': 'Performance consistency (higher = more consistent)',
            
            # Batter stats
            'at_bats': 'Number of at-bats in the game',
            'hits': 'Number of hits in the game',
            'doubles': 'Number of doubles in the game',
            'triples': 'Number of triples in the game',
            'home_runs': 'Number of home runs in the game',
            'walks': 'Number of walks in the game',
            'strikeouts': 'Number of strikeouts in the game',
            'hit_by_pitch': 'Number of times hit by pitch',
            'batting_avg': 'Batting average for the game',
            
            # Pitcher stats
            'innings_pitched': 'Innings pitched in the game',
            'hits_allowed': 'Hits allowed in the game',
            'home_runs_allowed': 'Home runs allowed in the game',
            'walks_allowed': 'Walks allowed in the game',
            'total_batters': 'Total batters faced in the game'
        }


def validate_feature_config():
    """Validate the feature configuration for consistency"""
    print("🔧 VALIDATING FEATURE CONFIGURATION")
    print("=" * 50)
    
    config = MLBFeatureConfig()
    
    # Check that all positions have features defined
    positions = ['C', '1B', '2B', '3B', 'SS', 'OF', 'P']
    for position in positions:
        features = config.get_features_for_position(position)
        position_type = config.get_position_type(position)
        print(f"✅ {position} ({position_type.value}): {len(features)} features")
    
    # Check for overlapping features
    all_features = config.get_all_possible_features()
    print(f"\n📊 Total unique features: {len(all_features)}")
    
    # Validate feature groups
    groups = config.get_feature_groups()
    for group_name, group_features in groups.items():
        print(f"📝 {group_name}: {len(group_features)} features")
    
    # Test validation function
    print(f"\n🧪 Testing validation function:")
    test_features = ['avg_fantasy_points_L15', 'at_bats', 'hits']
    validation = config.validate_features('OF', test_features)
    print(f"✅ OF validation: {validation['is_valid']} ({validation['coverage_percentage']:.1f}% coverage)")
    
    print("\n✅ Feature configuration validation complete!")


if __name__ == "__main__":
    validate_feature_config()