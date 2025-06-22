#!/usr/bin/env python3
"""
MLB Predictions from CSV - Unified Interface
Automatically detects and processes both batters and pitchers from CSV data
"""

import pandas as pd
import os
import sys
import subprocess
from datetime import datetime

def detect_player_types(csv_file):
    """Detect if CSV contains batters, pitchers, or both"""
    try:
        df = pd.read_csv(csv_file)
        
        if 'position' not in df.columns:
            print("⚠️ No position column found. Please specify --type [batters|pitchers] or add position column")
            return None, None, None
        
        # Count by type
        batter_positions = ['C', '1B', '2B', '3B', 'SS', 'OF']
        batters = df[df['position'].isin(batter_positions)]
        pitchers = df[df['position'] == 'P']
        
        return df, batters, pitchers
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return None, None, None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='MLB Fantasy Predictions from CSV - Unified Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script automatically detects batters and pitchers in your CSV and runs
the appropriate prediction scripts.

CSV Format Requirements:
  - player_name: Player name
  - position: Player position (C, 1B, 2B, 3B, SS, OF for batters; P for pitchers)
  - avg_fantasy_points_L15: Average fantasy points last 15 games
  - avg_fantasy_points_L10: Average fantasy points last 10 games  
  - avg_fantasy_points_L5: Average fantasy points last 5 games
  - games_since_last_good_game: Games since >10 fantasy points
  - trend_last_5_games: Trend in last 5 games (positive = improving)
  - consistency_score: Performance consistency (0-1, higher = more consistent)

Examples:
  python predict_csv.py players.csv
  python predict_csv.py players.csv --output-dir results/
  python predict_csv.py players.csv --type batters
        """
    )
    
    parser.add_argument('csv_file', help='Input CSV file with player data')
    parser.add_argument('--output-dir', '-o', default='.', help='Output directory (default: current directory)')
    parser.add_argument('--type', choices=['batters', 'pitchers'], help='Force specific player type (auto-detect if not specified)')
    parser.add_argument('--models', '-m', default='models', help='Models directory (default: models)')
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.csv_file):
        print(f"❌ Input file not found: {args.csv_file}")
        sys.exit(1)
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"📁 Created output directory: {args.output_dir}")
    
    print("🚀 MLB UNIFIED PREDICTION FROM CSV")
    print("=" * 50)
    print(f"📊 Input file: {args.csv_file}")
    print(f"📁 Output directory: {args.output_dir}")
    print(f"🎯 Models directory: {args.models}")
    
    # Detect player types
    if args.type:
        print(f"🎯 Forced type: {args.type}")
        if args.type == 'batters':
            script = 'predict_batters_csv.py'
        else:
            script = 'predict_pitchers_csv.py'
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(args.output_dir, f'{args.type}_predictions_{timestamp}.csv')
        
        cmd = ['python', script, args.csv_file, '--output', output_file, '--models', args.models]
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print(f"\n✅ {args.type.title()} predictions completed!")
        else:
            print(f"\n❌ {args.type.title()} predictions failed!")
            sys.exit(1)
    else:
        # Auto-detect
        df, batters, pitchers = detect_player_types(args.csv_file)
        
        if df is None:
            sys.exit(1)
        
        print(f"\n🔍 Auto-detection results:")
        print(f"  📊 Total players: {len(df)}")
        print(f"  ⚾ Batters: {len(batters)}")
        print(f"  🥎 Pitchers: {len(pitchers)}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        success_count = 0
        
        # Process batters if found
        if len(batters) > 0:
            print(f"\n🏃 Processing {len(batters)} batters...")
            batter_file = f"batters_only_{timestamp}.csv"
            batters.to_csv(batter_file, index=False)
            
            output_file = os.path.join(args.output_dir, f'batter_predictions_{timestamp}.csv')
            cmd = ['python', 'predict_batters_csv.py', batter_file, '--output', output_file, '--models', args.models]
            result = subprocess.run(cmd)
            
            os.remove(batter_file)  # Clean up temp file
            
            if result.returncode == 0:
                print(f"✅ Batter predictions saved to: {output_file}")
                success_count += 1
            else:
                print(f"❌ Batter predictions failed!")
        
        # Process pitchers if found
        if len(pitchers) > 0:
            print(f"\n🥎 Processing {len(pitchers)} pitchers...")
            pitcher_file = f"pitchers_only_{timestamp}.csv"
            pitchers.to_csv(pitcher_file, index=False)
            
            output_file = os.path.join(args.output_dir, f'pitcher_predictions_{timestamp}.csv')
            cmd = ['python', 'predict_pitchers_csv.py', pitcher_file, '--output', output_file, '--models', args.models]
            result = subprocess.run(cmd)
            
            os.remove(pitcher_file)  # Clean up temp file
            
            if result.returncode == 0:
                print(f"✅ Pitcher predictions saved to: {output_file}")
                success_count += 1
            else:
                print(f"❌ Pitcher predictions failed!")
        
        # Summary
        total_expected = (1 if len(batters) > 0 else 0) + (1 if len(pitchers) > 0 else 0)
        
        if success_count == total_expected:
            print(f"\n🎉 All predictions completed successfully! ({success_count}/{total_expected})")
        else:
            print(f"\n⚠️ Some predictions failed ({success_count}/{total_expected})")
            sys.exit(1)

if __name__ == "__main__":
    main()