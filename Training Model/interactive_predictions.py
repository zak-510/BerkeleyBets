import tkinter as tk
from tkinter import ttk, messagebox
import joblib
import os
import pandas as pd
from player_projections import PlayerProjectionModel

class PlayerProjectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Performance Projections")
        self.root.geometry("600x500")
        
        self.loaded_models = {}
        self.create_widgets()
        self.load_available_models()
    
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Player Performance Projections", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Player input frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill="x")
        
        # Player name
        ttk.Label(input_frame, text="👤 Player Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.player_name_var = tk.StringVar()
        self.player_name_entry = ttk.Entry(input_frame, textvariable=self.player_name_var, width=30)
        self.player_name_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Sport selection
        ttk.Label(input_frame, text="🏀 Sport:").grid(row=1, column=0, sticky="w", pady=5)
        self.sport_var = tk.StringVar()
        self.sport_combo = ttk.Combobox(input_frame, textvariable=self.sport_var, 
                                       values=["NBA", "NFL", "MLB"], state="readonly")
        self.sport_combo.grid(row=1, column=1, pady=5, padx=(10, 0), sticky="ew")
        self.sport_combo.bind("<<ComboboxSelected>>", self.on_sport_change)
        
        # Stats input frame
        self.stats_frame = ttk.LabelFrame(self.root, text="Player Statistics", padding=10)
        self.stats_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Prediction button
        self.predict_button = ttk.Button(self.root, text="🔮 Generate Prediction", 
                                        command=self.make_prediction)
        self.predict_button.pack(pady=10)
        
        # Results frame
        self.results_frame = ttk.LabelFrame(self.root, text="Prediction Results", padding=10)
        self.results_frame.pack(pady=10, padx=20, fill="x")
        
        self.results_text = tk.Text(self.results_frame, height=6, width=70)
        self.results_text.pack()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken")
        status_bar.pack(side="bottom", fill="x")
    
    def load_available_models(self):
        """Load available trained models"""
        models_dir = "models"
        if not os.path.exists(models_dir):
            self.status_var.set("No models directory found. Please train models first.")
            return
        
        for filename in os.listdir(models_dir):
            if filename.endswith('.pkl'):
                sport = filename.split('_')[0].upper()
                try:
                    model_path = os.path.join(models_dir, filename)
                    model_data = joblib.load(model_path)
                    self.loaded_models[sport] = {
                        'model_data': model_data,
                        'path': model_path
                    }
                except Exception as e:
                    print(f"Error loading model {filename}: {e}")
        
        if self.loaded_models:
            available_sports = list(self.loaded_models.keys())
            self.sport_combo['values'] = available_sports
            self.sport_combo.set(available_sports[0])
            self.on_sport_change(None)
            self.status_var.set(f"Loaded models for: {', '.join(available_sports)}")
        else:
            self.status_var.set("No trained models found. Please train models first.")
    
    def on_sport_change(self, event):
        """Handle sport selection change"""
        selected_sport = self.sport_var.get()
        if selected_sport not in self.loaded_models:
            return
        
        # Clear previous stats inputs
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Get feature columns for selected sport
        model_data = self.loaded_models[selected_sport]['model_data']
        feature_columns = model_data['feature_columns']
        
        # Create input fields for each feature
        self.stat_vars = {}
        row = 0
        col = 0
        
        for feature in feature_columns:
            if not feature.endswith('_per_game'):  # Skip per-game features for input
                # Create label and entry
                label_text = feature.replace('_', ' ').title()
                ttk.Label(self.stats_frame, text=f"{label_text}:").grid(
                    row=row, column=col*2, sticky="w", pady=2, padx=(0, 5))
                
                var = tk.StringVar()
                entry = ttk.Entry(self.stats_frame, textvariable=var, width=10)
                entry.grid(row=row, column=col*2+1, pady=2, padx=(0, 15))
                
                self.stat_vars[feature] = var
                
                col += 1
                if col >= 3:  # 3 columns of inputs
                    col = 0
                    row += 1
    
    def make_prediction(self):
        """Make prediction based on input"""
        selected_sport = self.sport_var.get()
        player_name = self.player_name_var.get().strip()
        
        if not selected_sport:
            messagebox.showerror("Error", "Please select a sport")
            return
        
        if not player_name:
            messagebox.showerror("Error", "Please enter a player name")
            return
        
        if selected_sport not in self.loaded_models:
            messagebox.showerror("Error", f"No model available for {selected_sport}")
            return
        
        # Collect input stats
        player_stats = {}
        missing_stats = []
        
        for feature, var in self.stat_vars.items():
            value = var.get().strip()
            if value:
                try:
                    player_stats[feature] = float(value)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid value for {feature}: {value}")
                    return
            else:
                missing_stats.append(feature)
        
        if missing_stats:
            messagebox.showwarning("Warning", 
                                 f"Missing values for: {', '.join(missing_stats)}\n"
                                 "These will be set to 0 for prediction.")
        
        try:
            # Load model and make prediction
            model_data = self.loaded_models[selected_sport]['model_data']
            
            # Create projection model instance
            projection_model = PlayerProjectionModel(selected_sport.lower())
            projection_model.model = model_data['model']
            projection_model.feature_columns = model_data['feature_columns']
            projection_model.target_column = model_data['target_column']
            
            # Add per-game calculations
            if 'games_played' in player_stats and player_stats['games_played'] > 0:
                for stat, value in player_stats.items():
                    if stat != 'games_played':
                        player_stats[f'{stat}_per_game'] = value / player_stats['games_played']
            
            # Make prediction
            prediction = projection_model.predict_player_performance(player_stats)
            
            # Display results
            self.display_results(player_name, selected_sport, prediction, 
                               model_data['target_column'], player_stats)
            
        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed: {str(e)}")
    
    def display_results(self, player_name, sport, prediction, target_stat, input_stats):
        """Display prediction results"""
        self.results_text.delete(1.0, tk.END)
        
        result_text = f"🎯 PROJECTION FOR {player_name.upper()}\n"
        result_text += f"Sport: {sport}\n"
        result_text += f"Predicted {target_stat.replace('_', ' ').title()}: {prediction:.2f}\n\n"
        
        result_text += "📊 Input Statistics:\n"
        for stat, value in input_stats.items():
            if not stat.endswith('_per_game'):
                result_text += f"  • {stat.replace('_', ' ').title()}: {value}\n"
        
        result_text += f"\n🔮 This projection is based on the player's current statistics\n"
        result_text += f"and historical performance patterns in {sport}."
        
        self.results_text.insert(1.0, result_text)
        self.status_var.set(f"Prediction generated for {player_name}")

def main():
    root = tk.Tk()
    app = PlayerProjectionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()