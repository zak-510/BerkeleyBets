# Player Profile Feature

## Overview
New interactive player profile feature that displays comprehensive statistics for NBA, NFL, and MLB players.

## Features

### Clickable Player Cards
- All player cards in the dashboard are now clickable
- Click on any player name/card to open their detailed profile
- Enhanced hover effects for better UX

### Dynamic Player Profile Modal
- **Automatic stat detection**: Displays ALL available statistics from the API response
- **Sport-agnostic**: Works with NBA, NFL, and MLB data automatically
- **Smart categorization**: Groups related stats into logical sections:
  - Fantasy & Performance
  - Projected Statistics  
  - Batting Statistics (MLB)
  - Pitching Statistics (MLB)
  - Skill Ratings
  - Model Confidence

### Dynamic Stat Formatting
- **Auto-formatting**: Converts API field names to human-readable labels
  - `predicted_points` → "Points"
  - `projectedRBIs` → "Projected RBIs"
  - `batting_average_skill` → "Batting Avg Skill"
- **Smart value formatting**: 
  - Percentages display as % (0.267 → 26.7%)
  - Decimal numbers rounded appropriately
  - Integers displayed cleanly

### Comprehensive Data Display

#### NBA Players
- Points, Rebounds, Assists predictions
- Fantasy points projections
- Model confidence scores
- Accuracy metrics (if available)

#### MLB Players
**Batters:**
- Fantasy points projections
- Projected hits, runs, RBIs
- Batting average, OBP, slugging percentage
- Skill ratings

**Pitchers:**
- Fantasy points projections  
- Projected strikeouts and innings pitched
- Confidence scores

#### NFL Players
- Fantasy points projections
- Passing, rushing, receiving yards (when available)
- Touchdown projections
- Model confidence

### Responsive Design
- Mobile-friendly modal layout
- Scrollable content for long stat lists
- Responsive grid layouts for different screen sizes
- Touch-friendly close buttons

### Technical Implementation

#### Components
- `PlayerProfile.jsx`: Main profile modal component
- Enhanced `Dashboard.jsx`: Added click handlers and modal integration

#### Key Functions
- `getAllPlayerStats()`: Extracts all available stats from player object
- `formatStatName()`: Converts field names to display names
- `formatStatValue()`: Formats values for display (percentages, decimals)
- `categorizeStats()`: Groups stats into logical categories

#### Data Handling
- Supports both formatted UI data and raw API responses
- Automatically detects available stats without hardcoding
- Graceful handling of missing data
- Sport detection based on available stats

## Usage

1. Navigate to the dashboard
2. Select a sport (NBA, NFL, or MLB)
3. Click on any player card
4. View comprehensive player statistics
5. Click "Back to Players" or X to close

## API Compatibility

The feature dynamically adapts to whatever statistics the backend API provides:

- **NBA API**: Returns predicted_points, predicted_rebounds, predicted_assists, confidence
- **MLB API**: Returns batting stats, projected stats, skill ratings for batters; pitching stats for pitchers
- **NFL API**: Returns fantasy points and confidence scores

The component automatically displays whatever fields are available without requiring code changes for new stats.

## Future Enhancements

- Player comparison modal
- Historical performance charts
- Betting integration
- Social sharing
- Player favorites/watchlist