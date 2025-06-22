#!/usr/bin/env python3
"""
MLB Data Collection Infrastructure
Handles game log fetching using Statcast data aggregated to game level
"""

import pandas as pd
import numpy as np
import pybaseball as pb
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from .fantasy_scoring import FantasyScoring

class MLBDataCollector:
    def __init__(self, cache_dir: str = "mlb_data", rate_limit_delay: float = 2.0):
        """
        Initialize MLB data collector with caching and rate limiting
        
        Args:
            cache_dir: Directory for caching data
            rate_limit_delay: Seconds to wait between API calls
        """
        self.cache_dir = Path(cache_dir)
        self.rate_limit_delay = rate_limit_delay
        self.last_api_call = 0
        
        # Create cache directories
        self.setup_cache_directories()
        
        # Track API calls and errors
        self.api_call_count = 0
        self.error_log = []
        
    def setup_cache_directories(self):
        """Create necessary cache directories"""
        directories = [
            self.cache_dir,
            self.cache_dir / "raw_statcast",
            self.cache_dir / "game_logs",
            self.cache_dir / "player_lookup",
            self.cache_dir / "positions"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        print(f"✅ Cache directories created in: {self.cache_dir}")
    
    def rate_limit(self):
        """Enforce rate limiting between API calls"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            print(f"⏱️ Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
        
        self.last_api_call = time.time()
        self.api_call_count += 1
    
    def get_player_id(self, last_name: str, first_name: str, use_cache: bool = True) -> Optional[int]:
        """
        Get MLB player ID with caching
        
        Args:
            last_name: Player's last name
            first_name: Player's first name
            use_cache: Whether to use cached results
            
        Returns:
            MLB player ID or None if not found
        """
        cache_file = self.cache_dir / "player_lookup" / f"{last_name}_{first_name}.json"
        
        # Check cache first
        if use_cache and cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    print(f"📋 Using cached ID for {first_name} {last_name}: {cached_data['player_id']}")
                    return cached_data['player_id']
            except Exception as e:
                print(f"⚠️ Cache read error for {first_name} {last_name}: {e}")
        
        # Fetch from API
        try:
            self.rate_limit()
            print(f"🔍 Looking up {first_name} {last_name}...")
            
            lookup_result = pb.playerid_lookup(last_name, first_name)
            
            if len(lookup_result) > 0:
                player_id = int(lookup_result.iloc[0]['key_mlbam'])
                
                # Cache the result
                cache_data = {
                    'player_id': player_id,
                    'full_name': f"{first_name} {last_name}",
                    'lookup_date': datetime.now().isoformat(),
                    'lookup_data': lookup_result.iloc[0].to_dict()
                }
                
                with open(cache_file, 'w') as f:
                    json.dump(cache_data, f, indent=2, default=str)
                
                print(f"✅ Found {first_name} {last_name}: ID {player_id}")
                return player_id
            else:
                print(f"❌ No player found for {first_name} {last_name}")
                # Try alternative name formats
                alt_result = self._try_alternative_lookups(last_name, first_name)
                if alt_result:
                    return alt_result
                return None
                
        except Exception as e:
            error_msg = f"Error looking up {first_name} {last_name}: {str(e)}"
            print(f"❌ {error_msg}")
            self.error_log.append({
                'timestamp': datetime.now().isoformat(),
                'operation': 'player_lookup',
                'player': f"{first_name} {last_name}",
                'error': str(e)
            })
            return None
    
    def _try_alternative_lookups(self, last_name: str, first_name: str) -> Optional[int]:
        """Try alternative name formats for player lookup"""
        alternatives = []
        
        # Handle common name variations
        if "Jr." in last_name:
            alternatives.append((last_name.replace("Jr.", "").strip(), first_name))
        if "." in first_name:
            alternatives.append((last_name, first_name.replace(".", "")))
        if " " in first_name:
            # Try just first part of first name
            alternatives.append((last_name, first_name.split()[0]))
        
        # Try without accents (fallback)
        import unicodedata
        def remove_accents(text):
            return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        
        alternatives.append((remove_accents(last_name), remove_accents(first_name)))
        
        for alt_last, alt_first in alternatives:
            try:
                print(f"🔄 Trying alternative: {alt_first} {alt_last}")
                lookup_result = pb.playerid_lookup(alt_last, alt_first)
                
                if len(lookup_result) > 0:
                    player_id = int(lookup_result.iloc[0]['key_mlbam'])
                    print(f"✅ Found with alternative: {player_id}")
                    
                    # Cache this successful result with original name
                    cache_file = self.cache_dir / "player_lookup" / f"{last_name}_{first_name}.json"
                    cache_data = {
                        'player_id': player_id,
                        'full_name': f"{first_name} {last_name}",
                        'lookup_date': datetime.now().isoformat(),
                        'lookup_data': lookup_result.iloc[0].to_dict(),
                        'found_with_alternative': f"{alt_first} {alt_last}"
                    }
                    
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f, indent=2, default=str)
                    
                    return player_id
                    
            except Exception as e:
                continue
        
        return None
    
    def get_game_data(self, player_id: int, start_date: str, end_date: str, player_type: str) -> List[Dict]:
        """
        Get game-level data for a player by aggregating Statcast data
        
        Args:
            player_id: MLB player ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            player_type: 'b' for batter or 'p' for pitcher
            
        Returns:
            List of game-level statistics as dictionaries
        """
        # Convert player_type to statcast format
        statcast_type = 'batter' if player_type == 'b' else 'pitcher'
        
        # Get Statcast data
        statcast_data = self.get_statcast_data(player_id, start_date, end_date, statcast_type)
        
        if statcast_data is None or len(statcast_data) == 0:
            return []
        
        # Aggregate to game level
        game_logs_df = self.aggregate_to_game_logs(statcast_data, statcast_type)
        
        if len(game_logs_df) == 0:
            return []
        
        # Convert to list of dictionaries
        return game_logs_df.to_dict('records')
    
    def get_statcast_data(self, player_id: int, start_date: str, end_date: str, 
                         player_type: str = 'batter', use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Get Statcast data for a player with caching and error handling
        
        Args:
            player_id: MLB player ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            player_type: 'batter' or 'pitcher'
            use_cache: Whether to use cached results
            
        Returns:
            DataFrame with Statcast data or None if failed
        """
        cache_file = self.cache_dir / "raw_statcast" / f"{player_id}_{start_date}_{end_date}_{player_type}.csv"
        
        # Check cache first
        if use_cache and cache_file.exists():
            try:
                statcast_data = pd.read_csv(cache_file)
                print(f"📋 Using cached Statcast data for player {player_id} ({start_date} to {end_date}): {len(statcast_data)} at-bats")
                return statcast_data
            except Exception as e:
                print(f"⚠️ Cache read error for player {player_id}: {e}")
        
        # Fetch from API
        try:
            self.rate_limit()
            print(f"🔍 Fetching Statcast data for player {player_id} ({player_type}) from {start_date} to {end_date}...")
            
            if player_type == 'batter':
                statcast_data = pb.statcast_batter(start_date, end_date, player_id)
            else:  # pitcher
                statcast_data = pb.statcast_pitcher(start_date, end_date, player_id)
            
            if statcast_data is not None and len(statcast_data) > 0:
                # Add metadata
                statcast_data['player_id'] = player_id
                statcast_data['player_type'] = player_type
                statcast_data['fetch_date'] = datetime.now().isoformat()
                
                # Cache the result
                statcast_data.to_csv(cache_file, index=False)
                
                print(f"✅ Fetched {len(statcast_data)} at-bats for player {player_id}")
                return statcast_data
            else:
                print(f"❌ No Statcast data found for player {player_id}")
                return None
                
        except Exception as e:
            error_msg = f"Error fetching Statcast data for player {player_id}: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Enhanced error logging with retry information
            error_entry = {
                'timestamp': datetime.now().isoformat(),
                'operation': 'statcast_data',
                'player_id': player_id,
                'start_date': start_date,
                'end_date': end_date,
                'player_type': player_type,
                'error': str(e),
                'error_type': type(e).__name__,
                'api_call_count': self.api_call_count
            }
            self.error_log.append(error_entry)
            
            # Attempt retry with different date range if network error
            if 'network' in str(e).lower() or 'timeout' in str(e).lower():
                print(f"🔄 Attempting retry with shorter date range...")
                try:
                    # Retry with last 7 days only
                    retry_start = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
                    return self.get_statcast_data(player_id, retry_start, end_date, player_type, use_cache=False)
                except Exception as retry_error:
                    print(f"❌ Retry also failed: {retry_error}")
            
            return None
    
    def aggregate_to_game_logs(self, statcast_data: pd.DataFrame, player_type: str) -> pd.DataFrame:
        """
        Aggregate Statcast at-bat data to game-level statistics
        
        Args:
            statcast_data: Raw Statcast data
            player_type: 'batter' or 'pitcher'
            
        Returns:
            DataFrame with game-level statistics
        """
        if statcast_data is None or len(statcast_data) == 0:
            return pd.DataFrame()
        
        print(f"🔄 Aggregating {len(statcast_data)} at-bats to game level...")
        
        # Group by game_date to create game logs
        if player_type == 'batter':
            game_logs = self._aggregate_batter_games(statcast_data)
        else:
            game_logs = self._aggregate_pitcher_games(statcast_data)
        
        print(f"✅ Created {len(game_logs)} game logs")
        return game_logs
    
    def _aggregate_batter_games(self, data: pd.DataFrame) -> pd.DataFrame:
        """Aggregate batter Statcast data to game level"""
        games = []
        
        for game_date, game_data in data.groupby('game_date'):
            # Basic counting stats
            at_bats = len(game_data[game_data['events'].notna()])
            hits = len(game_data[game_data['events'].isin(['single', 'double', 'triple', 'home_run'])])
            doubles = len(game_data[game_data['events'] == 'double'])
            triples = len(game_data[game_data['events'] == 'triple'])
            home_runs = len(game_data[game_data['events'] == 'home_run'])
            walks = len(game_data[game_data['events'] == 'walk'])
            strikeouts = len(game_data[game_data['events'] == 'strikeout'])
            hit_by_pitch = len(game_data[game_data['events'] == 'hit_by_pitch'])
            
            # Calculate fantasy points using centralized scoring
            game_stats_for_scoring = {
                'hits': hits,
                'doubles': doubles,
                'triples': triples,
                'home_runs': home_runs,
                'walks': walks,
                'hit_by_pitch': hit_by_pitch,
                'runs': 0,  # Not available from Statcast aggregation
                'rbis': 0,  # Not available from Statcast aggregation
                'stolen_bases': 0,  # Not available from Statcast aggregation
                'strikeouts': strikeouts
            }
            
            fantasy_points = FantasyScoring.calculate_batter_fantasy_points(game_stats_for_scoring)
            
            # Calculate batting average
            batting_avg = hits / at_bats if at_bats > 0 else 0
            
            game_log = {
                'game_date': game_date,
                'player_id': data['player_id'].iloc[0],
                'at_bats': at_bats,
                'hits': hits,
                'doubles': doubles,
                'triples': triples,
                'home_runs': home_runs,
                'walks': walks,
                'strikeouts': strikeouts,
                'hit_by_pitch': hit_by_pitch,
                'batting_avg': batting_avg,
                'fantasy_points': fantasy_points,
                'total_pitches': len(game_data)
            }
            
            games.append(game_log)
        
        return pd.DataFrame(games)
    
    def _aggregate_pitcher_games(self, data: pd.DataFrame) -> pd.DataFrame:
        """Aggregate pitcher Statcast data to game level"""
        games = []
        
        for game_date, game_data in data.groupby('game_date'):
            # Basic pitching stats
            total_batters = len(game_data[game_data['events'].notna()])
            hits_allowed = len(game_data[game_data['events'].isin(['single', 'double', 'triple', 'home_run'])])
            home_runs_allowed = len(game_data[game_data['events'] == 'home_run'])
            walks_allowed = len(game_data[game_data['events'] == 'walk'])
            strikeouts = len(game_data[game_data['events'] == 'strikeout'])
            
            # Estimate innings pitched (rough approximation)
            outs = len(game_data[game_data['events'].isin(['strikeout', 'field_out', 'force_out', 'grounded_into_double_play'])])
            innings_pitched = outs / 3.0
            
            # Calculate fantasy points using centralized scoring
            game_stats_for_scoring = {
                'innings_pitched': innings_pitched,
                'strikeouts': strikeouts,
                'hits_allowed': hits_allowed,
                'walks_allowed': walks_allowed,
                'home_runs_allowed': home_runs_allowed,
                'wins': 0,  # Not available from Statcast aggregation
                'saves': 0,  # Not available from Statcast aggregation
                'earned_runs': 0  # Would need additional data
            }
            
            fantasy_points = FantasyScoring.calculate_pitcher_fantasy_points(game_stats_for_scoring)
            
            game_log = {
                'game_date': game_date,
                'player_id': data['player_id'].iloc[0],
                'innings_pitched': innings_pitched,
                'hits_allowed': hits_allowed,
                'home_runs_allowed': home_runs_allowed,
                'walks_allowed': walks_allowed,
                'strikeouts': strikeouts,
                'total_batters': total_batters,
                'fantasy_points': fantasy_points,
                'total_pitches': len(game_data)
            }
            
            games.append(game_log)
        
        return pd.DataFrame(games)
    
    def collect_player_data(self, player_info: Dict, start_date: str = "2024-04-01", 
                           end_date: str = "2024-09-30", max_retries: int = 3) -> Dict:
        """
        Collect complete data for a single player using Statcast approach
        
        Args:
            player_info: Dict with 'first_name', 'last_name', 'position', 'player_type'
            start_date: Start date for data collection
            end_date: End date for data collection
            
        Returns:
            Dict with player data and metadata
        """
        first_name = player_info['first_name']
        last_name = player_info['last_name']
        expected_position = player_info['position']
        player_type = player_info.get('player_type', 'b')
        
        # Convert player_type to statcast format
        statcast_type = 'batter' if player_type == 'b' else 'pitcher'
        
        print(f"\n🔍 Collecting data for {first_name} {last_name} ({expected_position})")
        
        # Enhanced error tracking for this player
        player_errors = []
        
        # Get player ID with retries
        player_id = None
        for attempt in range(max_retries):
            try:
                player_id = self.get_player_id(last_name, first_name)
                if player_id is not None:
                    break
                else:
                    player_errors.append(f"Attempt {attempt + 1}: Player ID not found")
            except Exception as e:
                player_errors.append(f"Attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"⚠️ Retry {attempt + 1}/{max_retries} for player lookup...")
                    time.sleep(1)  # Brief delay before retry
        
        if player_id is None:
            return {
                'success': False,
                'error': 'Player ID not found after retries',
                'player_info': player_info,
                'retry_errors': player_errors
            }
        
        # Get Statcast data
        statcast_data = self.get_statcast_data(player_id, start_date, end_date, statcast_type)
        if statcast_data is None or len(statcast_data) == 0:
            return {
                'success': False,
                'error': 'No Statcast data found',
                'player_info': player_info,
                'player_id': player_id
            }
        
        # Aggregate to game logs
        game_logs = self.aggregate_to_game_logs(statcast_data, statcast_type)
        if len(game_logs) == 0:
            return {
                'success': False,
                'error': 'No games could be aggregated',
                'player_info': player_info,
                'player_id': player_id
            }
        
        return {
            'success': True,
            'player_info': player_info,
            'player_id': player_id,
            'game_logs': game_logs,
            'total_games': len(game_logs),
            'total_at_bats': len(statcast_data),
            'date_range': f"{start_date} to {end_date}",
            'collection_date': datetime.now().isoformat()
        }
    
    def collect_multiple_players(self, player_list: List[Dict], start_date: str = "2024-04-01", 
                                end_date: str = "2024-09-30") -> Dict:
        """
        Collect data for multiple players with progress tracking
        
        Args:
            player_list: List of player info dicts
            start_date: Start date for data collection  
            end_date: End date for data collection
            
        Returns:
            Dict with results for all players
        """
        print(f"🚀 Starting data collection for {len(player_list)} players")
        print(f"📅 Date range: {start_date} to {end_date}")
        print(f"⏱️ Rate limit: {self.rate_limit_delay}s between calls")
        
        results = {
            'successful_players': [],
            'failed_players': [],
            'summary': {},
            'collection_metadata': {
                'start_time': datetime.now().isoformat(),
                'total_players': len(player_list),
                'date_range': f"{start_date} to {end_date}",
                'rate_limit_delay': self.rate_limit_delay
            }
        }
        
        for i, player_info in enumerate(player_list, 1):
            print(f"\n{'='*60}")
            print(f"Processing player {i}/{len(player_list)}")
            
            player_result = self.collect_player_data(player_info, start_date, end_date)
            
            if player_result['success']:
                results['successful_players'].append(player_result)
                print(f"✅ Success: {player_result['total_games']} games, {player_result['total_at_bats']} at-bats")
            else:
                results['failed_players'].append(player_result)
                print(f"❌ Failed: {player_result['error']}")
            
            # Progress update
            success_rate = len(results['successful_players']) / i * 100
            print(f"📊 Progress: {i}/{len(player_list)} ({success_rate:.1f}% success rate)")
        
        # Generate summary
        results['summary'] = {
            'total_players_attempted': len(player_list),
            'successful_players': len(results['successful_players']),
            'failed_players': len(results['failed_players']),
            'success_rate': len(results['successful_players']) / len(player_list) * 100,
            'total_api_calls': self.api_call_count,
            'total_errors': len(self.error_log),
            'end_time': datetime.now().isoformat()
        }
        
        print(f"\n{'='*60}")
        print(f"🏁 DATA COLLECTION COMPLETE")
        print(f"✅ Successful: {results['summary']['successful_players']}/{len(player_list)}")
        print(f"❌ Failed: {results['summary']['failed_players']}/{len(player_list)}")
        print(f"📊 Success rate: {results['summary']['success_rate']:.1f}%")
        print(f"🔌 API calls made: {self.api_call_count}")
        
        return results
    
    def save_error_log(self):
        """Save error log to file"""
        if self.error_log:
            error_file = self.cache_dir / f"error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(error_file, 'w') as f:
                json.dump(self.error_log, f, indent=2)
            print(f"📝 Error log saved to: {error_file}")
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about cached data"""
        cache_stats = {
            'player_lookups': len(list((self.cache_dir / "player_lookup").glob("*.json"))),
            'statcast_files': len(list((self.cache_dir / "raw_statcast").glob("*.csv"))),
            'game_log_files': len(list((self.cache_dir / "game_logs").glob("*.csv"))),
            'total_cache_size_mb': 0
        }
        
        # Calculate cache size
        for file_path in self.cache_dir.rglob("*"):
            if file_path.is_file():
                cache_stats['total_cache_size_mb'] += file_path.stat().st_size
        
        cache_stats['total_cache_size_mb'] = round(cache_stats['total_cache_size_mb'] / (1024 * 1024), 2)
        
        return cache_stats

def create_test_player_list() -> List[Dict]:
    """Create a test list of 15 players for foundation testing"""
    return [
        # Position players
        {'first_name': 'Aaron', 'last_name': 'Judge', 'position': 'OF', 'player_type': 'b'},
        {'first_name': 'Freddie', 'last_name': 'Freeman', 'position': '1B', 'player_type': 'b'},
        {'first_name': 'Jose', 'last_name': 'Altuve', 'position': '2B', 'player_type': 'b'},
        {'first_name': 'Manny', 'last_name': 'Machado', 'position': '3B', 'player_type': 'b'},
        {'first_name': 'Trea', 'last_name': 'Turner', 'position': 'SS', 'player_type': 'b'},
        {'first_name': 'Salvador', 'last_name': 'Perez', 'position': 'C', 'player_type': 'b'},
        {'first_name': 'Mookie', 'last_name': 'Betts', 'position': 'OF', 'player_type': 'b'},
        {'first_name': 'Vladimir', 'last_name': 'Guerrero Jr.', 'position': '1B', 'player_type': 'b'},
        {'first_name': 'Ronald', 'last_name': 'Acuna Jr.', 'position': 'OF', 'player_type': 'b'},
        {'first_name': 'Francisco', 'last_name': 'Lindor', 'position': 'SS', 'player_type': 'b'},
        
        # Pitchers
        {'first_name': 'Gerrit', 'last_name': 'Cole', 'position': 'P', 'player_type': 'p'},
        {'first_name': 'Jacob', 'last_name': 'deGrom', 'position': 'P', 'player_type': 'p'},
        {'first_name': 'Shane', 'last_name': 'Bieber', 'position': 'P', 'player_type': 'p'},
        {'first_name': 'Edwin', 'last_name': 'Diaz', 'position': 'P', 'player_type': 'p'},
        {'first_name': 'Josh', 'last_name': 'Hader', 'position': 'P', 'player_type': 'p'}
    ]

if __name__ == "__main__":
    # Test the data collection system with a smaller date range
    collector = MLBDataCollector()
    
    # Get test players
    test_players = create_test_player_list()
    
    print("🧪 TESTING DATA COLLECTION INFRASTRUCTURE")
    print("=" * 60)
    
    # Test with a smaller date range first (just September 2024)
    results = collector.collect_multiple_players(
        test_players, 
        start_date="2024-09-01", 
        end_date="2024-09-30"
    )
    
    # Save error log if any errors occurred
    collector.save_error_log()
    
    # Show cache statistics
    cache_stats = collector.get_cache_stats()
    print(f"\n📊 CACHE STATISTICS:")
    print(f"Player lookups cached: {cache_stats['player_lookups']}")
    print(f"Statcast files cached: {cache_stats['statcast_files']}")
    print(f"Game log files cached: {cache_stats['game_log_files']}")
    print(f"Total cache size: {cache_stats['total_cache_size_mb']} MB") 