#!/usr/bin/env python3
"""
MLB Fantasy Baseball GUI Predictions
Tkinter-based GUI for making MLB player predictions
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import joblib
import numpy as np

class MLBPredictionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MLB Fantasy Baseball Predictions")
        self.root.geometry("700x600")
        
        self.models = {}
        self.model_loaded = False
        
        self.setup_ui()
        self.try_load_default_models()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="⚾ MLB Fantasy Baseball Predictions", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Model section
        model_frame = ttk.LabelFrame(main_frame, text="Models", padding="10")
        model_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.model_status = ttk.Label(model_frame, text="No models loaded", foreground="red")
        self.model_status.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(model_frame, text="Load Models", command=self.load_models).grid(row=0, column=1, padx=(10, 0))
        
        # Position selection
        pos_frame = ttk.LabelFrame(main_frame, text="Player Position", padding="10")
        pos_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(pos_frame, text="Position:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.position_var = tk.StringVar(value="OF")
        position_combo = ttk.Combobox(pos_frame, textvariable=self.position_var, 
                                    values=["P", "C", "1B", "2B", "3B", "SS", "OF", "DH"], 
                                    state="readonly", width=10)
        position_combo.grid(row=0, column=1, sticky=tk.W)
        position_combo.bind('<<ComboboxSelected>>', self.on_position_change)
        
        # Player stats section
        stats_frame = ttk.LabelFrame(main_frame, text="Player Statistics", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create input fields
        self.stat_vars = {}
        self.batting_stats = [
            ('hits', 'Hits'),
            ('home_runs', 'Home Runs'),
            ('rbi', 'RBI'),
            ('runs', 'Runs'),
            ('stolen_bases', 'Stolen Bases'),
            ('batting_average', 'Batting Average'),
            ('obp', 'OBP'),
            ('slg', 'SLG')
        ]
        
        self.pitching_stats = [
            ('wins', 'Wins'),
            ('losses', 'Losses'),
            ('era', 'ERA'),
            ('whip', 'WHIP'),
            ('strikeouts', 'Strikeouts'),
            ('innings_pitched', 'Innings Pitched'),
            ('saves', 'Saves'),
            ('holds', 'Holds')
        ]
        
        # Initialize with batting stats
        self.create_stat_inputs(self.batting_stats)
        
        # Prediction section
        pred_frame = ttk.LabelFrame(main_frame, text="Prediction", padding="10")
        pred_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(pred_frame, text="Predict Fantasy Points", 
                  command=self.make_prediction).grid(row=0, column=0, pady=(0, 10))
        
        self.result_label = ttk.Label(pred_frame, text="Enter player stats and click predict", 
                                     font=("Arial", 12))
        self.result_label.grid(row=1, column=0)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def create_stat_inputs(self, stats_list):
        """Create input fields for statistics"""
        # Clear existing inputs
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        self.stat_vars = {}
        
        for i, (key, label) in enumerate(stats_list):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(self.stats_frame, text=f"{label}:").grid(row=row, column=col, sticky=tk.W, padx=(0, 5))
            
            var = tk.StringVar(value="0")
            self.stat_vars[key] = var
            entry = ttk.Entry(self.stats_frame, textvariable=var, width=10)
            entry.grid(row=row, column=col+1, padx=(0, 20), pady=2)
    
    def on_position_change(self, event=None):
        """Handle position change"""
        position = self.position_var.get()
        
        if position == "P":
            self.create_stat_inputs(self.pitching_stats)
        else:
            self.create_stat_inputs(self.batting_stats)
    
    def try_load_default_models(self):
        """Try to load the default models"""
        positions = ["P", "C", "1B", "2B", "3B", "SS", "OF", "DH"]
        loaded_count = 0
        
        for pos in positions:
            model_path = f"mlb_{pos.lower()}_model.pkl"
            if os.path.exists(model_path):
                try:
                    model_data = joblib.load(model_path)
                    self.models[pos] = model_data
                    loaded_count += 1
                except Exception as e:
                    print(f"Failed to load {pos} model: {e}")
        
        if loaded_count > 0:
            self.model_loaded = True
            self.model_status.config(text=f"✅ {loaded_count} models loaded successfully", foreground="green")
    
    def load_models(self):
        """Load model files"""
        # For simplicity, we'll load all models in the current directory
        positions = ["P", "C", "1B", "2B", "3B", "SS", "OF", "DH"]
        loaded_count = 0
        
        for pos in positions:
            model_path = f"mlb_{pos.lower()}_model.pkl"
            if os.path.exists(model_path):
                try:
                    model_data = joblib.load(model_path)
                    self.models[pos] = model_data
                    loaded_count += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load {pos} model: {e}")
        
        if loaded_count > 0:
            self.model_loaded = True
            self.model_status.config(text=f"✅ {loaded_count} models loaded successfully", foreground="green")
        else:
            messagebox.showerror("Error", "No models found. Train models first with: python mlb_model.py")
    
    def make_prediction(self):
        """Make a fantasy points prediction"""
        if not self.model_loaded:
            messagebox.showerror("Error", "Please load models first")
            return
        
        position = self.position_var.get()
        
        if position not in self.models:
            messagebox.showerror("Error", f"No model available for position: {position}")
            return
        
        try:
            # Collect player stats
            player_stats = {}
            for key, var in self.stat_vars.items():
                try:
                    value = float(var.get()) if var.get().strip() else 0.0
                    player_stats[key] = value
                except ValueError:
                    player_stats[key] = 0.0
            
            # Add position
            player_stats['position'] = position
            
            # Make prediction
            prediction = self.predict_player(player_stats)
            
            if prediction is None:
                messagebox.showerror("Error", "Failed to make prediction")
                return
            
            # Get confidence based on position
            position_confidence = {
                'P': 'Medium (Pitching is volatile)',
                'C': 'High (Catcher stats are consistent)',
                '1B': 'High (Power hitters are predictable)',
                '2B': 'Medium (Mixed skill sets)',
                '3B': 'High (Power/contact balance)',
                'SS': 'Medium (Speed/power mix)',
                'OF': 'High (Outfielders are consistent)',
                'DH': 'High (Designated hitters are predictable)'
            }
            
            result_text = f"🎯 Fantasy Points Projection: {prediction:.1f}\n"
            result_text += f"📊 Standard 5x5 Scoring\n"
            result_text += f"🎲 Prediction Confidence: {position_confidence[position]}\n"
            result_text += f"📝 Position: {position}"
            
            self.result_label.config(
                text=result_text,
                foreground="blue",
                justify=tk.LEFT
            )
            
        except Exception as e:
            messagebox.showerror("Prediction Error", f"Failed to make prediction: {str(e)}")
    
    def predict_player(self, player_data):
        """Predict fantasy points for a single player"""
        position = player_data['position']
        
        if position not in self.models:
            return None
        
        model_data = self.models[position]
        model = model_data['model']
        features = model_data['features']
        
        # Extract features in correct order
        feature_values = []
        for feature in features:
            value = player_data.get(feature, 0)
            feature_values.append(float(value))
        
        # Make prediction
        X = np.array(feature_values).reshape(1, -1)
        prediction = model.predict(X)[0]
        
        return round(prediction, 1)

def main():
    root = tk.Tk()
    app = MLBPredictionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 