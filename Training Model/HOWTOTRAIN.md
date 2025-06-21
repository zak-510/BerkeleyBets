Setup and Usage Instructions
Installation
bashCopy# Install required packages
pip install pandas numpy scikit-learn xgboost requests joblib

# Optional: For GUI
pip install tkinter  # Usually comes with Python
Usage

Train Models:

bashCopy# Train NBA model
python player_projections.py --sport nba --model xgboost --players 100

# Train NFL model
python player_projections.py --sport nfl --model random_forest --players 50

# Train MLB model
python player_projections.py --sport mlb --model linear --players 75

Interactive GUI:

bashCopypython interactive_predictions.py

Command Line Interface:

bashCopypython cli_predictions.py
Example Usage
pythonCopyfrom player_projections import PlayerProjectionModel

# Initialize and train model
model = PlayerProjectionModel('nba')
df = model.collect_training_data(max_players=50)
df = model.preprocess_data(df)
model.train_model(df, model_type='xgboost')
model.save_model()

# Make prediction
player_stats = {
    'games_played': 70,
    'minutes': 35,
    'field_goals_made': 9,
    'field_goals_attempted': 20,
    'three_point_field_goals_made': 3,
    'free_throws_made': 5,
    'rebounds': 8,
    'assists': 7
}

prediction = model.predict_player_performance(player_stats)
print(f"Predicted points: {prediction:.2f}")
This comprehensive system provides:

✅ Multi-sport support (NBA, NFL, MLB)
✅ Automated data collection and preprocessing
✅ Multiple ML models (Linear, Random Forest, XGBoost)
✅ Model persistence with joblib
✅ Interactive GUI interface
✅ Command-line interface
✅ Example predictions and usage

The system is modular and extensible, allowing you to easily add new sports or modify the prediction models as needed!