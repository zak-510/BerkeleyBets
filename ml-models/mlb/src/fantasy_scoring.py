#!/usr/bin/env python3
"""
MLB Fantasy Scoring Module
Centralized and standardized fantasy point calculations for all player types
"""

import pandas as pd
import numpy as np
from typing import Dict, Union, List
from enum import Enum


class ScoringSystem(Enum):
    """Different fantasy scoring systems supported"""
    STANDARD = "standard"
    DRAFTKINGS = "draftkings"
    FANDUEL = "fanduel"


class FantasyScoring:
    """Centralized fantasy scoring calculations for MLB players"""
    
    # Standard fantasy scoring weights
    STANDARD_BATTER_SCORING = {
        'singles': 3.0,           # 3 points per single (hit - extra bases)
        'doubles': 5.0,           # 5 points per double (3 for hit + 2 extra)
        'triples': 8.0,           # 8 points per triple (3 for hit + 5 extra)
        'home_runs': 10.0,        # 10 points per home run (3 for hit + 7 extra)
        'walks': 2.0,             # 2 points per walk
        'hit_by_pitch': 2.0,      # 2 points per HBP
        'runs': 2.0,              # 2 points per run scored
        'rbis': 2.0,              # 2 points per RBI
        'stolen_bases': 5.0,      # 5 points per stolen base
        'strikeouts': -1.0        # -1 point per strikeout
    }
    
    STANDARD_PITCHER_SCORING = {
        'innings_pitched': 3.0,   # 3 points per inning pitched
        'strikeouts': 2.0,        # 2 points per strikeout
        'wins': 10.0,             # 10 points per win
        'saves': 10.0,            # 10 points per save
        'hits_allowed': -1.0,     # -1 point per hit allowed
        'walks_allowed': -1.0,    # -1 point per walk allowed
        'home_runs_allowed': -4.0, # -4 points per HR allowed
        'earned_runs': -2.0       # -2 points per earned run
    }
    
    @classmethod
    def calculate_batter_fantasy_points(cls, game_stats: Dict, 
                                      scoring_system: ScoringSystem = ScoringSystem.STANDARD) -> float:
        """
        Calculate fantasy points for a batter's game performance
        
        Args:
            game_stats: Dictionary with game statistics
            scoring_system: Scoring system to use
            
        Returns:
            Total fantasy points for the game
        """
        if scoring_system != ScoringSystem.STANDARD:
            raise NotImplementedError(f"Scoring system {scoring_system} not implemented yet")
        
        weights = cls.STANDARD_BATTER_SCORING
        
        # Extract stats with safe defaults
        hits = game_stats.get('hits', 0)
        doubles = game_stats.get('doubles', 0)
        triples = game_stats.get('triples', 0)
        home_runs = game_stats.get('home_runs', 0)
        walks = game_stats.get('walks', 0)
        hit_by_pitch = game_stats.get('hit_by_pitch', 0)
        runs = game_stats.get('runs', game_stats.get('runs_scored', 0))
        rbis = game_stats.get('rbis', game_stats.get('rbi', 0))
        stolen_bases = game_stats.get('stolen_bases', game_stats.get('sb', 0))
        strikeouts = game_stats.get('strikeouts', game_stats.get('so', 0))
        
        # Calculate singles (total hits minus extra base hits)
        singles = max(0, hits - doubles - triples - home_runs)
        
        # Calculate total fantasy points
        fantasy_points = (
            singles * weights['singles'] +
            doubles * weights['doubles'] +
            triples * weights['triples'] +
            home_runs * weights['home_runs'] +
            walks * weights['walks'] +
            hit_by_pitch * weights['hit_by_pitch'] +
            runs * weights['runs'] +
            rbis * weights['rbis'] +
            stolen_bases * weights['stolen_bases'] +
            strikeouts * weights['strikeouts']
        )
        
        return round(fantasy_points, 2)
    
    @classmethod
    def calculate_pitcher_fantasy_points(cls, game_stats: Dict, 
                                       scoring_system: ScoringSystem = ScoringSystem.STANDARD) -> float:
        """
        Calculate fantasy points for a pitcher's game performance
        
        Args:
            game_stats: Dictionary with game statistics
            scoring_system: Scoring system to use
            
        Returns:
            Total fantasy points for the game
        """
        if scoring_system != ScoringSystem.STANDARD:
            raise NotImplementedError(f"Scoring system {scoring_system} not implemented yet")
        
        weights = cls.STANDARD_PITCHER_SCORING
        
        # Extract stats with safe defaults
        innings_pitched = game_stats.get('innings_pitched', game_stats.get('ip', 0))
        strikeouts = game_stats.get('strikeouts', game_stats.get('so', 0))
        wins = game_stats.get('wins', game_stats.get('w', 0))
        saves = game_stats.get('saves', game_stats.get('sv', 0))
        hits_allowed = game_stats.get('hits_allowed', game_stats.get('h', 0))
        walks_allowed = game_stats.get('walks_allowed', game_stats.get('bb', 0))
        home_runs_allowed = game_stats.get('home_runs_allowed', game_stats.get('hr', 0))
        earned_runs = game_stats.get('earned_runs', game_stats.get('er', 0))
        
        # Calculate total fantasy points
        fantasy_points = (
            innings_pitched * weights['innings_pitched'] +
            strikeouts * weights['strikeouts'] +
            wins * weights['wins'] +
            saves * weights['saves'] +
            hits_allowed * weights['hits_allowed'] +
            walks_allowed * weights['walks_allowed'] +
            home_runs_allowed * weights['home_runs_allowed'] +
            earned_runs * weights['earned_runs']
        )
        
        return round(fantasy_points, 2)
    
    @classmethod
    def calculate_from_statcast_batter(cls, statcast_data: pd.DataFrame) -> float:
        """
        Calculate fantasy points from Statcast at-bat data for batters
        This aggregates individual at-bats into game-level fantasy points
        
        Args:
            statcast_data: DataFrame with Statcast data for one game
            
        Returns:
            Total fantasy points for the game
        """
        if len(statcast_data) == 0:
            return 0.0
        
        # Aggregate at-bat events into game stats
        game_stats = {
            'hits': len(statcast_data[statcast_data['events'].isin(['single', 'double', 'triple', 'home_run'])]),
            'doubles': len(statcast_data[statcast_data['events'] == 'double']),
            'triples': len(statcast_data[statcast_data['events'] == 'triple']),
            'home_runs': len(statcast_data[statcast_data['events'] == 'home_run']),
            'walks': len(statcast_data[statcast_data['events'] == 'walk']),
            'hit_by_pitch': len(statcast_data[statcast_data['events'] == 'hit_by_pitch']),
            'strikeouts': len(statcast_data[statcast_data['events'] == 'strikeout']),
            'runs': 0,  # Not available in Statcast pitch-by-pitch data
            'rbis': 0,  # Not available in Statcast pitch-by-pitch data
            'stolen_bases': 0  # Not available in Statcast pitch-by-pitch data
        }
        
        return cls.calculate_batter_fantasy_points(game_stats)
    
    @classmethod
    def calculate_from_statcast_pitcher(cls, statcast_data: pd.DataFrame) -> float:
        """
        Calculate fantasy points from Statcast pitch data for pitchers
        This aggregates individual pitches into game-level fantasy points
        
        Args:
            statcast_data: DataFrame with Statcast data for one game
            
        Returns:
            Total fantasy points for the game
        """
        if len(statcast_data) == 0:
            return 0.0
        
        # Aggregate pitch events into game stats
        total_batters = len(statcast_data[statcast_data['events'].notna()])
        hits_allowed = len(statcast_data[statcast_data['events'].isin(['single', 'double', 'triple', 'home_run'])])
        home_runs_allowed = len(statcast_data[statcast_data['events'] == 'home_run'])
        walks_allowed = len(statcast_data[statcast_data['events'] == 'walk'])
        strikeouts = len(statcast_data[statcast_data['events'] == 'strikeout'])
        
        # Estimate innings pitched from outs recorded
        outs = len(statcast_data[statcast_data['events'].isin(['strikeout', 'field_out', 'force_out', 'grounded_into_double_play'])])
        innings_pitched = outs / 3.0
        
        game_stats = {
            'innings_pitched': innings_pitched,
            'strikeouts': strikeouts,
            'hits_allowed': hits_allowed,
            'walks_allowed': walks_allowed,
            'home_runs_allowed': home_runs_allowed,
            'wins': 0,  # Not determinable from Statcast data
            'saves': 0,  # Not determinable from Statcast data
            'earned_runs': 0  # Would need additional context
        }
        
        return cls.calculate_pitcher_fantasy_points(game_stats)
    
    @classmethod
    def validate_scoring_consistency(cls, test_cases: List[Dict]) -> Dict:
        """
        Validate scoring consistency across different calculation methods
        
        Args:
            test_cases: List of test cases with expected results
            
        Returns:
            Validation report
        """
        validation_report = {
            'total_tests': len(test_cases),
            'passed_tests': 0,
            'failed_tests': [],
            'average_error': 0.0,
            'max_error': 0.0
        }
        
        errors = []
        
        for i, test_case in enumerate(test_cases):
            player_type = test_case.get('player_type', 'batter')
            game_stats = test_case.get('game_stats', {})
            expected = test_case.get('expected_points', 0)
            
            if player_type == 'batter':
                calculated = cls.calculate_batter_fantasy_points(game_stats)
            else:
                calculated = cls.calculate_pitcher_fantasy_points(game_stats)
            
            error = abs(calculated - expected)
            errors.append(error)
            
            if error > 0.1:  # Allow for small rounding differences
                validation_report['failed_tests'].append({
                    'test_case': i,
                    'expected': expected,
                    'calculated': calculated,
                    'error': error,
                    'game_stats': game_stats
                })
            else:
                validation_report['passed_tests'] += 1
        
        if errors:
            validation_report['average_error'] = np.mean(errors)
            validation_report['max_error'] = max(errors)
        
        return validation_report
    
    @classmethod
    def get_scoring_weights(cls, player_type: str, 
                          scoring_system: ScoringSystem = ScoringSystem.STANDARD) -> Dict:
        """
        Get the scoring weights for a specific player type and system
        
        Args:
            player_type: 'batter' or 'pitcher'
            scoring_system: Scoring system to use
            
        Returns:
            Dictionary of scoring weights
        """
        if scoring_system != ScoringSystem.STANDARD:
            raise NotImplementedError(f"Scoring system {scoring_system} not implemented yet")
        
        if player_type.lower() == 'batter':
            return cls.STANDARD_BATTER_SCORING.copy()
        elif player_type.lower() == 'pitcher':
            return cls.STANDARD_PITCHER_SCORING.copy()
        else:
            raise ValueError(f"Unknown player type: {player_type}")
    
    @classmethod
    def get_scoring_explanation(cls, player_type: str) -> str:
        """
        Get human-readable explanation of scoring system
        
        Args:
            player_type: 'batter' or 'pitcher'
            
        Returns:
            String explanation of scoring
        """
        if player_type.lower() == 'batter':
            return """
BATTER SCORING (Standard System):
• Singles: +3 points
• Doubles: +5 points (3 for hit + 2 extra)
• Triples: +8 points (3 for hit + 5 extra)
• Home Runs: +10 points (3 for hit + 7 extra)
• Walks: +2 points
• Hit by Pitch: +2 points
• Runs Scored: +2 points
• RBIs: +2 points
• Stolen Bases: +5 points
• Strikeouts: -1 point
            """.strip()
        elif player_type.lower() == 'pitcher':
            return """
PITCHER SCORING (Standard System):
• Innings Pitched: +3 points per inning
• Strikeouts: +2 points each
• Wins: +10 points
• Saves: +10 points
• Hits Allowed: -1 point each
• Walks Allowed: -1 point each
• Home Runs Allowed: -4 points each
• Earned Runs: -2 points each
            """.strip()
        else:
            return "Unknown player type"


def test_fantasy_scoring():
    """Test the fantasy scoring system with known examples"""
    print("🧪 TESTING FANTASY SCORING SYSTEM")
    print("=" * 50)
    
    # Test batter scoring
    test_batter_game = {
        'hits': 3,
        'doubles': 1,
        'triples': 0,
        'home_runs': 1,
        'walks': 1,
        'hit_by_pitch': 0,
        'runs': 2,
        'rbis': 3,
        'stolen_bases': 1,
        'strikeouts': 1
    }
    
    batter_points = FantasyScoring.calculate_batter_fantasy_points(test_batter_game)
    print(f"🏏 Test Batter Game: {batter_points} fantasy points")
    print(f"   3 hits (1 single, 1 double, 1 HR) + 1 walk + 2 runs + 3 RBI + 1 SB - 1 SO")
    
    # Test pitcher scoring  
    test_pitcher_game = {
        'innings_pitched': 7.0,
        'strikeouts': 8,
        'wins': 1,
        'saves': 0,
        'hits_allowed': 5,
        'walks_allowed': 2,
        'home_runs_allowed': 1,
        'earned_runs': 2
    }
    
    pitcher_points = FantasyScoring.calculate_pitcher_fantasy_points(test_pitcher_game)
    print(f"⚾ Test Pitcher Game: {pitcher_points} fantasy points")
    print(f"   7 IP + 8 SO + 1 W - 5 H - 2 BB - 1 HR - 2 ER")
    
    # Test scoring explanations
    print(f"\n📋 Batter Scoring Rules:")
    print(FantasyScoring.get_scoring_explanation('batter'))
    
    print(f"\n📋 Pitcher Scoring Rules:")
    print(FantasyScoring.get_scoring_explanation('pitcher'))
    
    print("\n✅ Fantasy scoring test complete!")


if __name__ == "__main__":
    test_fantasy_scoring()