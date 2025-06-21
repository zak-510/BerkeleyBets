import argparse
import json
from player_projections import PlayerProjectionModel

def interactive_prediction():
    """Interactive command-line prediction interface"""
    print("🏆 Player Performance Projection System")
    print("=" * 50)
    
    # Get available sports
    available_sports = ['nba', 'nfl', 'mlb']
    
    # Select sport
    print("\nAvailable sports:")
    for i, sport in enumerate(available_sports, 1):
        print(f"{i}. {sport.upper()}")
    
    while True:
        try:
            choice = int(input("\nSelect sport (1-3): "))
            if 1 <= choice <= len(available_sports):
                selected_sport = available_sports[choice - 1]
                break
            else:
                print("Invalid choice. Please select 1-3.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Load model
    try:
        projection_model = PlayerProjectionModel(selected_sport)
        model_path = f"models/{selected_sport}_projection_model.pkl"
        projection_model.load_model(model_path)
        print(f"\n✅ Loaded {selected_sport.upper()} model successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Get player name
    player_name = input("\n👤 Enter player name: ").strip()
    
    # Get statistics
    print(f"\n📊 Enter statistics for {player_name}:")
    print("(Press Enter to skip any statistic)")
    
    config = projection_model.sport_configs[selected_sport]
    player_stats = {}
    
    for feature in config['features']:
        while True:
            try:
                value = input(f"  {feature.replace('_', ' ').title()}: ").strip()
                if value:
                    player_stats[feature] = float(value)
                    break
                else:
                    player_stats[feature] = 0
                    break
            except ValueError:
                print("    Please enter a valid number.")
    
    # Calculate per-game stats
    if 'games_played' in player_stats and player_stats['games_played'] > 0:
        for stat, value in player_stats.items():
            if stat != 'games_played':
                player_stats[f'{stat}_per_game'] = value / player_stats['games_played']
    
    # Make prediction
    try:
        prediction = projection_model.predict_player_performance(player_stats)
        
        print(f"\n🎯 PROJECTION RESULTS")
        print("=" * 30)
        print(f"Player: {player_name}")
        print(f"Sport: {selected_sport.upper()}")
        print(f"Predicted {config['target_stat'].replace('_', ' ').title()}: {prediction:.2f}")
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")

if __name__ == "__main__":
    interactive_prediction()