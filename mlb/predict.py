#!/usr/bin/env python3
"""
Enhanced MLB Prediction CLI with comprehensive error handling
Usage: python predict.py "Player Name" [--production]
"""

import sys
import argparse
from datetime import datetime
import traceback

def main():
    parser = argparse.ArgumentParser(
        description='MLB Fantasy Prediction System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python predict.py "Aaron Judge"
  python predict.py "Gerrit Cole" --production
  python predict.py "José Altuve" --position OF
        """
    )
    
    parser.add_argument('player_name', help='Full player name (e.g., "Aaron Judge")')
    parser.add_argument('--production', action='store_true', 
                       help='Use production inference system')
    parser.add_argument('--position', type=str, 
                       help='Expected position to help with lookup')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed error information')
    
    try:
        args = parser.parse_args()
    except SystemExit:
        return
    
    player_name = args.player_name.strip()
    
    if not player_name:
        print("❌ Error: Player name cannot be empty")
        return
    
    print(f"⚾ MLB Fantasy Prediction System")
    print(f"🎯 Player: {player_name}")
    print(f"🔧 Mode: {'Production' if args.production else 'Standard'}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Choose inference system
        if args.production:
            try:
                from mlb_inference_production import MLBProductionInference
                mlb = MLBProductionInference()
                
                # Check system status
                status = mlb.get_system_status()
                if not status['models_loaded']:
                    print("❌ Production system not ready - no models loaded")
                    return
                
                print(f"✅ Production system ready ({status['models_loaded']} models)")
                
                # Run production prediction
                result = mlb.predict_player(player_name, position_hint=args.position)
                
            except ImportError:
                print("❌ Production inference system not available, falling back to standard system")
                from mlb_inference import MLBInference
                mlb = MLBInference()
                result = mlb.predict_player(player_name)
        else:
            from mlb_inference import MLBInference
            mlb = MLBInference()
            result = mlb.predict_player(player_name)
        
        # Process results
        if result and (result.get('success', False) if args.production else result is not None):
            print(f"\n✅ Prediction completed successfully for {player_name}")
            
            if args.production and 'predictions' in result:
                predictions = result['predictions']
                if predictions:
                    avg_prediction = sum(p['predicted_fantasy_points'] for p in predictions) / len(predictions)
                    print(f"📊 Average predicted fantasy points: {avg_prediction:.1f}")
                    print(f"🎮 Total games predicted: {len(predictions)}")
                    
                    if result['metadata'].get('position'):
                        print(f"🏷️ Position: {result['metadata']['position']}")
                    
                    processing_time = result['metadata'].get('processing_time_ms', 0)
                    print(f"⏱️ Processing time: {processing_time:.0f}ms")
        else:
            print(f"\n❌ Prediction failed for {player_name}")
            
            # Show detailed error information if available
            if args.production and result and 'metadata' in result:
                errors = result['metadata'].get('errors', [])
                if errors and args.verbose:
                    print("\n🔍 Error details:")
                    for error in errors:
                        print(f"  • {error}")
            
            # Provide helpful suggestions
            print("\n💡 Troubleshooting suggestions:")
            print("  • Check player name spelling")
            print("  • Try with --production flag for enhanced system")
            print("  • Verify player is active in current season")
            if args.position:
                print(f"  • Position hint provided: {args.position}")
            else:
                print("  • Try adding --position [POS] to help with lookup")
    
    except KeyboardInterrupt:
        print("\n⚠️ Prediction interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        
        if args.verbose:
            print("\n🔍 Full error traceback:")
            traceback.print_exc()
        else:
            print("💡 Use --verbose for detailed error information")

if __name__ == "__main__":
    main() 