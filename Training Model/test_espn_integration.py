Pl#!/usr/bin/env python3
"""
Test script for ESPN Live Data Integration
Demonstrates the new live data fetching capabilities
"""

import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from espn_live_data import ESPNLiveDataFetcher, create_fallback_data
from player_projections import PlayerProjectionModel

def test_espn_data_fetcher():
    """Test the ESPN data fetcher directly"""
    print("=" * 60)
    print("Testing ESPN Live Data Fetcher")
    print("=" * 60)
    
    fetcher = ESPNLiveDataFetcher(cache_hours=1)
    
    # Test NBA data
    print("\n1. Testing NBA Teams Fetch...")
    try:
        nba_teams = fetcher.fetch_teams('nba')
        print(f"✅ Successfully fetched {len(nba_teams)} NBA teams")
        if nba_teams:
            print(f"   Sample team: {nba_teams[0]['name']} ({nba_teams[0]['abbreviation']})")
    except Exception as e:
        print(f"❌ Error fetching NBA teams: {e}")
    
    # Test roster fetch
    print("\n2. Testing Team Roster Fetch...")
    try:
        if nba_teams:
            team_id = nba_teams[0]['id']
            roster = fetcher.fetch_team_roster('nba', team_id)
            print(f"✅ Successfully fetched roster for {nba_teams[0]['name']}: {len(roster)} players")
            if roster:
                print(f"   Sample player: {roster[0]['name']} ({roster[0]['position']})")
    except Exception as e:
        print(f"❌ Error fetching roster: {e}")
    
    # Test comprehensive data fetch
    print("\n3. Testing Comprehensive Data Fetch...")
    try:
        df = fetcher.fetch_espn_data('nba', max_teams=2, max_players_per_team=5)
        print(f"✅ Successfully fetched comprehensive data: {df.shape[0]} players, {df.shape[1]} columns")
        print(f"   Columns: {list(df.columns)[:10]}...")  # Show first 10 columns
    except Exception as e:
        print(f"❌ Error fetching comprehensive data: {e}")
        print("   Creating fallback data instead...")
        df = create_fallback_data('nba', 20)
        print(f"✅ Fallback data created: {df.shape[0]} players, {df.shape[1]} columns")

def test_player_projection_integration():
    """Test the integrated player projection model"""
    print("\n" + "=" * 60)
    print("Testing Player Projection Model Integration")
    print("=" * 60)
    
    # Test with live data enabled
    print("\n1. Testing with Live Data Enabled...")
    try:
        model = PlayerProjectionModel(sport='nba', use_live_data=True, cache_hours=1)
        df = model.collect_training_data(max_players=50, max_teams=3)
        print(f"✅ Successfully collected training data: {df.shape[0]} players")
        
        # Test preprocessing
        df_processed = model.preprocess_data(df)
        print(f"✅ Data preprocessing successful: {df_processed.shape[0]} players after cleaning")
        
        # Test model training (quick test with small dataset)
        if len(df_processed) > 10:
            metrics = model.train_model(df_processed, model_type='linear')
            print(f"✅ Model training successful - Test R²: {metrics['test_r2']:.3f}")
        else:
            print("⚠️  Not enough data for model training (need >10 players)")
            
    except Exception as e:
        print(f"❌ Error with live data integration: {e}")
        print("   Testing fallback mode...")
        
        # Test fallback mode
        model = PlayerProjectionModel(sport='nba', use_live_data=False)
        df = model.collect_training_data(max_players=50)
        print(f"✅ Fallback data collection successful: {df.shape[0]} players")

def test_different_sports():
    """Test data fetching for different sports"""
    print("\n" + "=" * 60)
    print("Testing Different Sports")
    print("=" * 60)
    
    sports = ['nba', 'nfl', 'mlb']
    
    for sport in sports:
        print(f"\n{sport.upper()} Test:")
        try:
            fetcher = ESPNLiveDataFetcher(cache_hours=1)
            teams = fetcher.fetch_teams(sport)
            print(f"  ✅ {len(teams)} teams found")
            
            if teams:
                # Test model integration
                model = PlayerProjectionModel(sport=sport, use_live_data=True, cache_hours=1)
                df = model.collect_training_data(max_players=20, max_teams=2)
                print(f"  ✅ {len(df)} players collected")
                
        except Exception as e:
            print(f"  ❌ Error with {sport}: {e}")
            # Test fallback
            df = create_fallback_data(sport, 20)
            print(f"  ✅ Fallback data created: {len(df)} players")

def test_caching_functionality():
    """Test the caching functionality"""
    print("\n" + "=" * 60)
    print("Testing Caching Functionality")
    print("=" * 60)
    
    fetcher = ESPNLiveDataFetcher(cache_hours=1)
    
    print("\n1. First fetch (should hit API)...")
    start_time = datetime.now()
    try:
        teams1 = fetcher.fetch_teams('nba')
        duration1 = (datetime.now() - start_time).total_seconds()
        print(f"✅ First fetch: {len(teams1)} teams in {duration1:.2f}s")
    except Exception as e:
        print(f"❌ First fetch failed: {e}")
        return
    
    print("\n2. Second fetch (should use cache)...")
    start_time = datetime.now()
    try:
        teams2 = fetcher.fetch_teams('nba')
        duration2 = (datetime.now() - start_time).total_seconds()
        print(f"✅ Second fetch: {len(teams2)} teams in {duration2:.2f}s")
        
        if duration2 < duration1:
            print(f"✅ Caching working! Second fetch was {duration1/duration2:.1f}x faster")
        else:
            print("⚠️  Cache may not be working as expected")
            
    except Exception as e:
        print(f"❌ Second fetch failed: {e}")

def main():
    """Run all tests"""
    print("ESPN Live Data Integration Test Suite")
    print("====================================")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Basic ESPN data fetcher
        test_espn_data_fetcher()
        
        # Test 2: Player projection integration
        test_player_projection_integration()
        
        # Test 3: Different sports
        test_different_sports()
        
        # Test 4: Caching functionality
        test_caching_functionality()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        print("\nTo train a model with live data, run:")
        print("python player_projections.py --sport nba --players 100 --teams 5")
        print("\nTo use fallback data instead:")
        print("python player_projections.py --sport nba --no-live-data")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 