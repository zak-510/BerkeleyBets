#TEST CODE
from player_projections import PlayerProjectionModel

# Load the trained NBA model
model = PlayerProjectionModel('nba')
model.load_model('models/nba_projection_model.pkl')

# TJ McConnell's sample stats (replace with actual stats if needed)
player_stats = {
    'games_played': 75,
    'minutes': 20,
    'field_goals_made': 4,
    'field_goals_attempted': 8,
    'three_point_field_goals_made': 1,
    'free_throws_made': 2,
    'rebounds': 3,
    'assists': 5
}

prediction = model.predict_player_performance(player_stats)
print(f"TJ McConnell's projected points: {prediction:.2f}")