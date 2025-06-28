#!/usr/bin/env python3
"""
NFL Fantasy Football GUI Predictions
Tkinter-based GUI for making NFL player predictions
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from nfl_model import NFLProjectionModel

class NFLPredictionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NFL Fantasy Football Predictions")
        self.root.geometry("600x500")
        
        self.model = NFLProjectionModel()
        self.model_loaded = False
        
        self.setup_ui()
        self.try_load_default_model()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🏈 NFL Fantasy Football Predictions", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Model section
        model_frame = ttk.LabelFrame(main_frame, text="Model", padding="10")
        model_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.model_status = ttk.Label(model_frame, text="No model loaded", foreground="red")
        self.model_status.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(model_frame, text="Load Model", command=self.load_model).grid(row=0, column=1, padx=(10, 0))
        
        # Player stats section
        stats_frame = ttk.LabelFrame(main_frame, text="Player Statistics", padding="10")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create input fields
        self.stat_vars = {}
        stats = [
            ('games_played', 'Games Played'),
            ('passing_yards', 'Passing Yards'),
            ('passing_tds', 'Passing TDs'),
            ('interceptions', 'Interceptions'),
            ('rushing_yards', 'Rushing Yards'),
            ('rushing_tds', 'Rushing TDs'),
            ('receiving_yards', 'Receiving Yards'),
            ('receiving_tds', 'Receiving TDs'),
            ('receptions', 'Receptions'),
            ('targets', 'Targets')
        ]
        
        for i, (key, label) in enumerate(stats):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(stats_frame, text=f"{label}:").grid(row=row, column=col, sticky=tk.W, padx=(0, 5))
            
            var = tk.StringVar(value="0")
            self.stat_vars[key] = var
            entry = ttk.Entry(stats_frame, textvariable=var, width=10)
            entry.grid(row=row, column=col+1, padx=(0, 20), pady=2)
        
        # Prediction section
        pred_frame = ttk.LabelFrame(main_frame, text="Prediction", padding="10")
        pred_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(pred_frame, text="Predict Fantasy Points", 
                  command=self.make_prediction).grid(row=0, column=0, pady=(0, 10))
        
        self.result_label = ttk.Label(pred_frame, text="Enter player stats and click predict", 
                                     font=("Arial", 12))
        self.result_label.grid(row=1, column=0)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def try_load_default_model(self):
        """Try to load the default model"""
        default_path = "nfl_model.pkl"
        if os.path.exists(default_path):
            if self.model.load_model(default_path):
                self.model_loaded = True
                self.model_status.config(text="✅ Model loaded successfully", foreground="green")
    
    def load_model(self):
        """Load a model file"""
        filepath = filedialog.askopenfilename(
            title="Select NFL Model File",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")]
        )
        
        if filepath:
            if self.model.load_model(filepath):
                self.model_loaded = True
                self.model_status.config(text="✅ Model loaded successfully", foreground="green")
            else:
                messagebox.showerror("Error", "Failed to load model file")
    
    def make_prediction(self):
        """Make a fantasy points prediction"""
        if not self.model_loaded:
            messagebox.showerror("Error", "Please load a model first")
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
            
            # Calculate derived stats
            games = player_stats.get('games_played', 0)
            if games > 0:
                player_stats['passing_yards_per_game'] = player_stats.get('passing_yards', 0) / games
                player_stats['rushing_yards_per_game'] = player_stats.get('rushing_yards', 0) / games
                player_stats['receiving_yards_per_game'] = player_stats.get('receiving_yards', 0) / games
            
            # Make prediction
            prediction = self.model.predict_player(player_stats)
            
            # Get confidence interval
            confidence_result = self.model.predict_player_with_confidence(player_stats, 0.8)
            lower, upper = confidence_result['confidence_interval']
            
            result_text = f"🎯 Fantasy Points Projection: {prediction:.1f}\n"
            result_text += f"📊 PPR Scoring (1 pt/reception + standard)\n"
            result_text += f"📈 80% Confidence: {lower:.1f} to {upper:.1f} points\n"
            result_text += f"📝 Actual score likely between {lower:.1f}-{upper:.1f}"
            
            self.result_label.config(
                text=result_text,
                foreground="blue",
                justify=tk.LEFT
            )
            
        except Exception as e:
            messagebox.showerror("Prediction Error", f"Failed to make prediction: {str(e)}")

def main():
    root = tk.Tk()
    app = NFLPredictionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 