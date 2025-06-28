#!/usr/bin/env python3
"""
Clean up NBA inference CSV by rounding decimal places for better readability
"""

import pandas as pd
import numpy as np
from datetime import datetime

def clean_inference_csv(input_file: str, output_file: str = None):
    """Clean up the CSV by rounding decimal places appropriately"""
    
    print(f"🧹 Cleaning up CSV: {input_file}")
    
    # Read the messy CSV
    df = pd.read_csv(input_file)
    
    print(f"📊 Original data: {len(df)} players")
    
    # Round columns to appropriate decimal places
    rounding_rules = {
        # Historical features - 3 decimal places (percentages)
        'hist_fg_pct': 3,
        'hist_fg3_pct': 3, 
        'hist_ft_pct': 3,
        'hist_usage_rate': 3,
        
        # Minutes - 1 decimal place
        'hist_min_avg': 1,
        
        # Predictions - 1 decimal place
        'predicted_pts': 1,
        'predicted_reb': 1,
        'predicted_ast': 1,
        'predicted_fantasy_points': 1
    }
    
    # Apply rounding
    for column, decimals in rounding_rules.items():
        if column in df.columns:
            df[column] = df[column].round(decimals)
            print(f"✅ Rounded {column} to {decimals} decimal places")
    
    # Clean up any remaining long decimals (fallback)
    for col in df.columns:
        if df[col].dtype in ['float64', 'float32']:
            if col not in rounding_rules:
                df[col] = df[col].round(2)  # Default to 2 decimal places
    
    # Sort by predicted fantasy points (descending) for better presentation
    df = df.sort_values('predicted_fantasy_points', ascending=False)
    
    # Create output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"nba_inference_clean_{timestamp}.csv"
    
    # Save cleaned CSV
    df.to_csv(output_file, index=False)
    
    print(f"✅ Saved clean CSV to: {output_file}")
    print(f"📊 {len(df)} players with properly rounded values")
    
    # Show a sample of the cleaned data
    print(f"\n📋 SAMPLE OF CLEANED DATA:")
    print("=" * 80)
    print(df.head(10).to_string(index=False))
    
    return output_file

if __name__ == "__main__":
    # Clean the most recent inference file
    input_file = "nba_player_inference_20250621_193946.csv"
    clean_inference_csv(input_file) 