import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def display_improved_inference_results():
    """Display the improved model inference results in a clean format"""
    
    try:
        results_df = pd.read_csv('inference_results.csv')
        print(f"✓ Loaded improved model results: {len(results_df)} players")
    except FileNotFoundError:
        print("✗ Improved model results not found. Please run the improved model first.")
        return
    
    # Calculate additional metrics
    results_df['Error'] = results_df['actual_points'] - results_df['predicted_points']
    results_df['Abs_Error'] = np.abs(results_df['Error'])
    results_df['Error_Pct'] = (results_df['Abs_Error'] / results_df['actual_points']) * 100
    
    print(f"\n{'='*80}")
    print(f"NFL FANTASY PREDICTIONS - IMPROVED MODEL RESULTS")
    print(f"{'='*80}")
    print(f"Total Players: {len(results_df)}")
    print(f"Positions: {', '.join(sorted(results_df['position'].unique()))}")
    
    # Overall metrics
    mae = results_df['Abs_Error'].mean()
    rmse = np.sqrt(mean_squared_error(results_df['actual_points'], results_df['predicted_points']))
    r2 = r2_score(results_df['actual_points'], results_df['predicted_points'])
    median_ae = results_df['Abs_Error'].median()
    
    print(f"\nOVERALL PERFORMANCE:")
    print(f"MAE: {mae:.1f}")
    print(f"Median AE: {median_ae:.1f}")
    print(f"RMSE: {rmse:.1f}")
    print(f"R²: {r2:.3f}")
    print(f"Mean-Median Gap: {mae - median_ae:.1f}")
    
    # Position breakdown
    print(f"\nPOSITION BREAKDOWN:")
    for pos in sorted(results_df['position'].unique()):
        pos_data = results_df[results_df['position'] == pos]
        pos_mae = pos_data['Abs_Error'].mean()
        pos_r2 = r2_score(pos_data['actual_points'], pos_data['predicted_points'])
        pos_count = len(pos_data)
        print(f"{pos}: {pos_count} players, MAE = {pos_mae:.1f}, R² = {pos_r2:.3f}")
    
    # Top 20 fantasy performers
    print(f"\n{'='*80}")
    print(f"TOP 20 FANTASY PERFORMERS")
    print(f"{'='*80}")
    top_performers = results_df.nlargest(20, 'actual_points')
    
    print(f"{'Rank':<4} {'Player':<20} {'Pos':<3} {'Actual':<7} {'Predicted':<9} {'Error':<7} {'Error%':<7}")
    print("-" * 80)
    
    for i, (_, player) in enumerate(top_performers.iterrows(), 1):
        print(f"{i:<4} {player['player_name'][:19]:<20} {player['position']:<3} "
              f"{player['actual_points']:<7.1f} {player['predicted_points']:<9.1f} "
              f"{player['Error']:<+7.1f} {player['Error_Pct']:<7.1f}%")
    
    # Most accurate predictions
    print(f"\n{'='*80}")
    print(f"MOST ACCURATE PREDICTIONS (Top 15)")
    print(f"{'='*80}")
    most_accurate = results_df.nsmallest(15, 'Abs_Error')
    
    print(f"{'Rank':<4} {'Player':<20} {'Pos':<3} {'Actual':<7} {'Predicted':<9} {'Error':<7} {'Error%':<7}")
    print("-" * 80)
    
    for i, (_, player) in enumerate(most_accurate.iterrows(), 1):
        print(f"{i:<4} {player['player_name'][:19]:<20} {player['position']:<3} "
              f"{player['actual_points']:<7.1f} {player['predicted_points']:<9.1f} "
              f"{player['Error']:<+7.1f} {player['Error_Pct']:<7.1f}%")
    
    # Biggest prediction errors
    print(f"\n{'='*80}")
    print(f"BIGGEST PREDICTION ERRORS (Top 15)")
    print(f"{'='*80}")
    biggest_errors = results_df.nlargest(15, 'Abs_Error')
    
    print(f"{'Rank':<4} {'Player':<20} {'Pos':<3} {'Actual':<7} {'Predicted':<9} {'Error':<7} {'Error%':<7}")
    print("-" * 80)
    
    for i, (_, player) in enumerate(biggest_errors.iterrows(), 1):
        print(f"{i:<4} {player['player_name'][:19]:<20} {player['position']:<3} "
              f"{player['actual_points']:<7.1f} {player['predicted_points']:<9.1f} "
              f"{player['Error']:<+7.1f} {player['Error_Pct']:<7.1f}%")
    
    # Position-specific top performers
    print(f"\n{'='*80}")
    print(f"TOP PERFORMERS BY POSITION")
    print(f"{'='*80}")
    
    for pos in ['QB', 'RB', 'WR', 'TE']:
        pos_data = results_df[results_df['position'] == pos]
        if len(pos_data) > 0:
            print(f"\n{pos} - Top 5:")
            print(f"{'Player':<20} {'Actual':<7} {'Predicted':<9} {'Error':<7} {'Error%':<7}")
            print("-" * 60)
            
            top_pos = pos_data.nlargest(5, 'actual_points')
            for _, player in top_pos.iterrows():
                print(f"{player['player_name'][:19]:<20} "
                      f"{player['actual_points']:<7.1f} {player['predicted_points']:<9.1f} "
                      f"{player['Error']:<+7.1f} {player['Error_Pct']:<7.1f}%")
    
    # Summary statistics
    print(f"\n{'='*80}")
    print(f"SUMMARY STATISTICS")
    print(f"{'='*80}")
    
    # Error distribution
    error_ranges = [
        (0, 5, "Excellent"),
        (5, 10, "Very Good"),
        (10, 20, "Good"),
        (20, 50, "Fair"),
        (50, float('inf'), "Poor")
    ]
    
    print("Prediction Accuracy Distribution:")
    for min_err, max_err, label in error_ranges:
        if max_err == float('inf'):
            count = len(results_df[results_df['Abs_Error'] >= min_err])
            pct = (count / len(results_df)) * 100
            print(f"  {label} (≥{min_err} error): {count} players ({pct:.1f}%)")
        else:
            count = len(results_df[(results_df['Abs_Error'] >= min_err) & (results_df['Abs_Error'] < max_err)])
            pct = (count / len(results_df)) * 100
            print(f"  {label} ({min_err}-{max_err} error): {count} players ({pct:.1f}%)")
    
    # Outlier analysis
    outliers = results_df[results_df['Abs_Error'] > 50]
    print(f"\nOutliers (>50 point error): {len(outliers)} players ({len(outliers)/len(results_df)*100:.1f}%)")
    
    if len(outliers) > 0:
        print("Outlier breakdown by position:")
        for pos in outliers['position'].unique():
            pos_outliers = outliers[outliers['position'] == pos]
            print(f"  {pos}: {len(pos_outliers)} players")
    
    print(f"\n{'='*80}")
    print("IMPROVED MODEL INFERENCE COMPLETE")
    print(f"{'='*80}")
    
    return results_df

if __name__ == "__main__":
    display_improved_inference_results() 