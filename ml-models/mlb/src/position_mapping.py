#!/usr/bin/env python3
"""
MLB Position Mapping System
Handles player position detection, validation, and mapping
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class PositionMapper:
    def __init__(self, cache_dir: str = "mlb_data"):
        """
        Initialize position mapper with caching
        
        Args:
            cache_dir: Directory for caching position data
        """
        self.cache_dir = Path(cache_dir)
        self.position_cache_file = self.cache_dir / "positions" / "position_mappings.json"
        
        # Position groupings for model training
        self.position_groups = {
            'C': 'C',      # Catcher
            '1B': '1B',    # First Base
            '2B': '2B',    # Second Base  
            '3B': '3B',    # Third Base
            'SS': 'SS',    # Shortstop
            'LF': 'OF',    # Left Field -> Outfield
            'CF': 'OF',    # Center Field -> Outfield
            'RF': 'OF',    # Right Field -> Outfield
            'OF': 'OF',    # General Outfield
            'DH': 'DH',    # Designated Hitter
            'P': 'P'       # Pitcher
        }
        
        # Load existing position mappings
        self.position_mappings = self.load_position_mappings()
        
    def load_position_mappings(self) -> Dict:
        """Load cached position mappings"""
        if self.position_cache_file.exists():
            try:
                with open(self.position_cache_file, 'r') as f:
                    mappings = json.load(f)
                print(f"📋 Loaded {len(mappings)} cached position mappings")
                return mappings
            except Exception as e:
                print(f"⚠️ Error loading position cache: {e}")
        
        return {}
    
    def save_position_mappings(self):
        """Save position mappings to cache"""
        try:
            with open(self.position_cache_file, 'w') as f:
                json.dump(self.position_mappings, f, indent=2)
            print(f"💾 Saved {len(self.position_mappings)} position mappings")
        except Exception as e:
            print(f"❌ Error saving position mappings: {e}")
    
    def get_player_position(self, player_id: int, player_name: str, 
                           expected_position: str = None) -> str:
        """
        Get or determine a player's primary position
        
        Args:
            player_id: MLB player ID
            player_name: Player's full name
            expected_position: Expected position from input data
            
        Returns:
            Primary position (mapped to our position groups)
        """
        # Check cache first
        cache_key = str(player_id)
        if cache_key in self.position_mappings:
            cached_pos = self.position_mappings[cache_key]['primary_position']
            print(f"📋 Using cached position for {player_name}: {cached_pos}")
            return cached_pos
        
        # Use expected position if provided and valid
        if expected_position and expected_position in self.position_groups:
            mapped_position = self.position_groups[expected_position]
            
            # Cache the result
            self.position_mappings[cache_key] = {
                'player_id': player_id,
                'player_name': player_name,
                'expected_position': expected_position,
                'primary_position': mapped_position,
                'detection_method': 'expected_input',
                'last_updated': datetime.now().isoformat()
            }
            
            print(f"✅ Mapped {player_name} to position {mapped_position} (from expected: {expected_position})")
            return mapped_position
        
        # Fallback logic for position detection
        return self._detect_position_from_context(player_id, player_name, expected_position)
    
    def _detect_position_from_context(self, player_id: int, player_name: str, 
                                     expected_position: str = None) -> str:
        """
        Detect position from context clues and fallback rules
        
        Args:
            player_id: MLB player ID
            player_name: Player's full name
            expected_position: Expected position hint
            
        Returns:
            Best guess at primary position
        """
        # Position detection heuristics
        detected_position = None
        detection_method = "fallback_rules"
        
        # Rule 1: If expected position is P, assume pitcher
        if expected_position == 'P':
            detected_position = 'P'
            detection_method = "pitcher_hint"
        
        # Rule 2: If name contains common pitcher indicators
        elif any(indicator in player_name.lower() for indicator in ['closer', 'reliever', 'starter']):
            detected_position = 'P'
            detection_method = "name_analysis"
        
        # Rule 3: Default position assignments based on common patterns
        else:
            # For now, default to OF for position players if unclear
            detected_position = 'OF'
            detection_method = "default_outfield"
        
        # Cache the result
        cache_key = str(player_id)
        self.position_mappings[cache_key] = {
            'player_id': player_id,
            'player_name': player_name,
            'expected_position': expected_position,
            'primary_position': detected_position,
            'detection_method': detection_method,
            'confidence': 'low',
            'last_updated': datetime.now().isoformat()
        }
        
        print(f"🔍 Detected position for {player_name}: {detected_position} (method: {detection_method})")
        return detected_position
    
    def validate_position_assignments(self, player_results: List[Dict]) -> Dict:
        """
        Validate position assignments across all collected players
        
        Args:
            player_results: List of player collection results
            
        Returns:
            Validation report
        """
        validation_report = {
            'total_players': len(player_results),
            'position_distribution': {},
            'validation_issues': [],
            'recommendations': []
        }
        
        print(f"\n🔍 VALIDATING POSITION ASSIGNMENTS")
        print("=" * 50)
        
        # Analyze position distribution
        for result in player_results:
            if result['success']:
                player_info = result['player_info']
                player_name = f"{player_info['first_name']} {player_info['last_name']}"
                expected_pos = player_info['position']
                
                # Get mapped position
                mapped_pos = self.get_player_position(
                    result['player_id'], 
                    player_name, 
                    expected_pos
                )
                
                # Track distribution
                if mapped_pos not in validation_report['position_distribution']:
                    validation_report['position_distribution'][mapped_pos] = 0
                validation_report['position_distribution'][mapped_pos] += 1
                
                # Check for potential issues
                if expected_pos != mapped_pos and expected_pos in self.position_groups:
                    validation_report['validation_issues'].append({
                        'player': player_name,
                        'expected': expected_pos,
                        'mapped': mapped_pos,
                        'issue': 'position_mismatch'
                    })
        
        # Generate recommendations
        pos_dist = validation_report['position_distribution']
        
        if 'P' not in pos_dist or pos_dist.get('P', 0) < 2:
            validation_report['recommendations'].append(
                "Consider adding more pitchers for better model training"
            )
        
        if len(pos_dist) < 4:
            validation_report['recommendations'].append(
                "Consider adding players from more positions for comprehensive coverage"
            )
        
        # Print validation results
        print(f"📊 Position Distribution:")
        for pos, count in sorted(pos_dist.items()):
            print(f"  {pos}: {count} players")
        
        if validation_report['validation_issues']:
            print(f"\n⚠️ Validation Issues ({len(validation_report['validation_issues'])}):")
            for issue in validation_report['validation_issues']:
                print(f"  {issue['player']}: {issue['expected']} → {issue['mapped']}")
        
        if validation_report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in validation_report['recommendations']:
                print(f"  • {rec}")
        
        return validation_report
    
    def get_position_groups_summary(self) -> Dict:
        """Get summary of position group mappings"""
        return {
            'position_groups': self.position_groups,
            'total_cached_players': len(self.position_mappings),
            'cache_file': str(self.position_cache_file)
        }
    
    def update_player_position(self, player_id: int, new_position: str, 
                              confidence: str = 'manual', source: str = 'user_update'):
        """
        Manually update a player's position
        
        Args:
            player_id: MLB player ID
            new_position: New position assignment
            confidence: Confidence level ('high', 'medium', 'low', 'manual')
            source: Source of the update
        """
        cache_key = str(player_id)
        
        if new_position not in self.position_groups.values():
            print(f"❌ Invalid position: {new_position}")
            return
        
        if cache_key in self.position_mappings:
            old_position = self.position_mappings[cache_key]['primary_position']
            self.position_mappings[cache_key]['primary_position'] = new_position
            self.position_mappings[cache_key]['confidence'] = confidence
            self.position_mappings[cache_key]['last_updated'] = datetime.now().isoformat()
            self.position_mappings[cache_key]['update_source'] = source
            
            print(f"✅ Updated player {player_id}: {old_position} → {new_position}")
        else:
            print(f"❌ Player {player_id} not found in cache")

def create_initial_position_mappings() -> List[Dict]:
    """Create initial position mappings for known star players"""
    return [
        # Catchers
        {'player_name': 'Salvador Perez', 'position': 'C'},
        {'player_name': 'J.T. Realmuto', 'position': 'C'},
        {'player_name': 'Will Smith', 'position': 'C'},
        
        # First Base
        {'player_name': 'Freddie Freeman', 'position': '1B'},
        {'player_name': 'Vladimir Guerrero Jr.', 'position': '1B'},
        {'player_name': 'Pete Alonso', 'position': '1B'},
        
        # Second Base
        {'player_name': 'Jose Altuve', 'position': '2B'},
        {'player_name': 'Gleyber Torres', 'position': '2B'},
        {'player_name': 'Marcus Semien', 'position': '2B'},
        
        # Third Base
        {'player_name': 'Manny Machado', 'position': '3B'},
        {'player_name': 'Rafael Devers', 'position': '3B'},
        {'player_name': 'Nolan Arenado', 'position': '3B'},
        
        # Shortstop
        {'player_name': 'Trea Turner', 'position': 'SS'},
        {'player_name': 'Francisco Lindor', 'position': 'SS'},
        {'player_name': 'Fernando Tatis Jr.', 'position': 'SS'},
        
        # Outfield
        {'player_name': 'Aaron Judge', 'position': 'OF'},
        {'player_name': 'Mookie Betts', 'position': 'OF'},
        {'player_name': 'Ronald Acuna Jr.', 'position': 'OF'},
        {'player_name': 'Mike Trout', 'position': 'OF'},
        
        # Pitchers
        {'player_name': 'Gerrit Cole', 'position': 'P'},
        {'player_name': 'Jacob deGrom', 'position': 'P'},
        {'player_name': 'Shane Bieber', 'position': 'P'},
        {'player_name': 'Edwin Diaz', 'position': 'P'},
        {'player_name': 'Josh Hader', 'position': 'P'}
    ]

if __name__ == "__main__":
    # Test the position mapping system
    mapper = PositionMapper()
    
    print("🧪 TESTING POSITION MAPPING SYSTEM")
    print("=" * 50)
    
    # Test position detection
    test_cases = [
        (592450, "Aaron Judge", "OF"),
        (543037, "Gerrit Cole", "P"), 
        (605141, "Mookie Betts", "OF"),
        (518692, "Freddie Freeman", "1B"),
        (none_id := 999999, "Unknown Player", "SS")
    ]
    
    for player_id, name, expected_pos in test_cases:
        if player_id == 999999:
            player_id = None
        
        position = mapper.get_player_position(player_id or 0, name, expected_pos)
        print(f"✅ {name}: {expected_pos} → {position}")
    
    # Save mappings
    mapper.save_position_mappings()
    
    # Show summary
    summary = mapper.get_position_groups_summary()
    print(f"\n📊 POSITION MAPPING SUMMARY:")
    print(f"Total position groups: {len(summary['position_groups'])}")
    print(f"Cached players: {summary['total_cached_players']}")
    print(f"Position groups: {list(summary['position_groups'].values())}") 