import React, { useState } from 'react';
import PlayerBetting from './PlayerBetting';

const PlayerProfile = ({ player, sport, onClose }) => {
  const [showBetting, setShowBetting] = useState(false);
  const [placedBets, setPlacedBets] = useState([]);

  if (!player) return null;

  const handlePlaceBet = (bet) => {
    setPlacedBets(prev => [...prev, bet]);
    // Here you would typically save to Firebase or your backend
    console.log('Bet placed:', bet);
  };

  // Function to format stat names for display
  const formatStatName = (key) => {
    const statNameMap = {
      // Fantasy Points
      'predictedFantasyPoints': 'Fantasy Points',
      'predicted_fantasy_points': 'Fantasy Points',
      'predictedPoints': 'Points',
      'predicted_points': 'Points',
      
      // NBA Stats
      'predictedRebounds': 'Rebounds',
      'predicted_rebounds': 'Rebounds',
      'predictedAssists': 'Assists',
      'predicted_assists': 'Assists',
      'pointsAccuracy': 'Points Accuracy',
      'reboundsAccuracy': 'Rebounds Accuracy',
      'assistsAccuracy': 'Assists Accuracy',
      'overallAccuracy': 'Overall Accuracy',
      
      // MLB Batter Stats
      'projectedHits': 'Projected Hits',
      'projectedRuns': 'Projected Runs',
      'projectedRBIs': 'Projected RBIs',
      'battingAvg': 'Batting Average',
      'onBasePct': 'On-Base Percentage',
      'sluggingPct': 'Slugging Percentage',
      'batting_average_skill': 'Batting Avg Skill',
      'on_base_percentage_skill': 'OBP Skill',
      'slugging_percentage_skill': 'SLG Skill',
      
      // MLB Pitcher Stats
      'projectedStrikeouts': 'Projected Strikeouts',
      'projectedInningsPitched': 'Projected Innings Pitched',
      'strikeoutsConfidence': 'Strikeouts Confidence',
      'inningsPitchedConfidence': 'Innings Pitched Confidence',
      
      // NFL Stats
      'passing_yards': 'Passing Yards',
      'passing_tds': 'Passing TDs',
      'interceptions': 'Interceptions',
      'completions': 'Completions',
      'rushing_yards': 'Rushing Yards',
      'rushing_tds': 'Rushing TDs',
      'carries': 'Carries',
      'ypc': 'Yards Per Carry',
      'receiving_yards': 'Receiving Yards',
      'receiving_tds': 'Receiving TDs',
      'receptions': 'Receptions',
      'targets': 'Targets',
      'yards_per_reception': 'Yards Per Reception',
      'recent_team': 'Team',
      
      // Confidence/Accuracy
      'confidence': 'Confidence',
      'fantasyConfidence': 'Fantasy Confidence',
      'skillConfidence': 'Skill Confidence',
      'accuracy': 'Accuracy',
      'error': 'Error'
    };

    if (statNameMap[key]) {
      return statNameMap[key];
    }

    // Auto-format camelCase and snake_case
    return key
      .replace(/([A-Z])/g, ' $1') // Add space before capital letters
      .replace(/_/g, ' ') // Replace underscores with spaces
      .replace(/^./, str => str.toUpperCase()) // Capitalize first letter
      .replace(/\b\w/g, str => str.toUpperCase()); // Capitalize each word
  };

  // Function to format stat values for display
  const formatStatValue = (value, key) => {
    if (value === undefined || value === null) return 'N/A';
    
    // Handle percentages and batting averages
    if (key.toLowerCase().includes('percentage') || 
        key.toLowerCase().includes('pct') ||
        key.toLowerCase().includes('rate') ||
        key.toLowerCase().includes('confidence') ||
        key.toLowerCase().includes('accuracy')) {
      if (typeof value === 'number') {
        if (value <= 1) {
          return (value * 100).toFixed(1) + '%';
        }
        return value.toFixed(1) + '%';
      }
    }
    
    // Handle batting averages (should be displayed as decimals, not percentages)
    if (key.toLowerCase().includes('avg') && key.toLowerCase().includes('batting')) {
      if (typeof value === 'number') {
        return value.toFixed(3);
      }
    }
    
    // Handle decimal numbers
    if (typeof value === 'number') {
      if (value % 1 !== 0) {
        return value.toFixed(1);
      }
      return value.toString();
    }
    
    return value.toString();
  };

  // Function to get all available stats from player object
  const getAllPlayerStats = (player) => {
    const allStats = { ...player.stats };
    
    // Dynamically add all properties from the player object except basic info
    const excludeFields = ['id', 'name', 'team', 'position', 'image', 'stats', 'playerType'];
    
    Object.keys(player).forEach(key => {
      if (!excludeFields.includes(key) && player[key] !== undefined && player[key] !== null) {
        allStats[key] = player[key];
      }
    });
    
    return allStats;
  };

  // Function to categorize stats for organized display
  const categorizeStats = (stats) => {
    const categories = {
      'Fantasy & Performance': [],
      'Passing Statistics': [],
      'Rushing Statistics': [],
      'Receiving Statistics': [],
      'Projected Statistics': [],
      'Batting Statistics': [],
      'Pitching Statistics': [],
      'Skill Ratings': [],
      'Model Confidence': []
    };

    Object.entries(stats).forEach(([key, value]) => {
      if (value === undefined || value === null) return;
      
      // Skip displayStats as it's handled separately
      if (key === 'displayStats') return;
      
      // Skip stats that are already shown in displayStats to avoid duplication
      // For MLB: projectedHits, projectedRuns, projectedRBIs, projectedStrikeouts, projectedInningsPitched
      if (key === 'projectedHits' || key === 'projectedRuns' || key === 'projectedRBIs' || 
          key === 'projectedStrikeouts' || key === 'projectedInningsPitched') return;
      
      const lowerKey = key.toLowerCase();
      
      if (lowerKey.includes('fantasy') || (lowerKey.includes('points') && !lowerKey.includes('projected'))) {
        categories['Fantasy & Performance'].push({ key, value });
      } else if (lowerKey.includes('confidence') || lowerKey.includes('accuracy') || lowerKey.includes('error')) {
        categories['Model Confidence'].push({ key, value });
      } else if (lowerKey.includes('passing') || lowerKey.includes('completion') || lowerKey.includes('interception')) {
        categories['Passing Statistics'].push({ key, value });
      } else if (lowerKey.includes('rushing') || lowerKey.includes('carries') || lowerKey.includes('ypc')) {
        categories['Rushing Statistics'].push({ key, value });
      } else if (lowerKey.includes('receiving') || lowerKey.includes('receptions') || lowerKey.includes('targets') || lowerKey.includes('catch')) {
        categories['Receiving Statistics'].push({ key, value });
      } else if (lowerKey.includes('projected') && (lowerKey.includes('hit') || lowerKey.includes('run') || lowerKey.includes('rbi') || lowerKey.includes('point') || lowerKey.includes('rebound') || lowerKey.includes('assist') || lowerKey.includes('strikeout') || lowerKey.includes('inning'))) {
        categories['Projected Statistics'].push({ key, value });
      } else if (lowerKey.includes('batting') || lowerKey.includes('onbase') || lowerKey.includes('slugging') || lowerKey.includes('avg')) {
        categories['Batting Statistics'].push({ key, value });
      } else if (lowerKey.includes('strikeout') || lowerKey.includes('inning') || lowerKey.includes('era') || lowerKey.includes('whip')) {
        categories['Pitching Statistics'].push({ key, value });
      } else if (lowerKey.includes('skill') || lowerKey.includes('rating')) {
        categories['Skill Ratings'].push({ key, value });
      } else if (lowerKey.includes('predicted')) {
        categories['Projected Statistics'].push({ key, value });
      } else {
        // Default to Fantasy & Performance for other stats
        categories['Fantasy & Performance'].push({ key, value });
      }
    });

    // Remove empty categories
    return Object.fromEntries(
      Object.entries(categories).filter(([_, stats]) => stats.length > 0)
    );
  };

  // Handle displayStats array specially for MLB
  const renderDisplayStats = (displayStats) => {
    if (!displayStats || !Array.isArray(displayStats)) return null;
    
    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-yellow-400 mb-3">Key Projections</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {displayStats.map((stat, index) => {
            // Ensure stat is an object with label and value
            if (!stat || typeof stat !== 'object' || !stat.label) {
              console.warn('Invalid displayStats item:', stat);
              return null;
            }
            
            return (
              <div key={index} className="bg-slate-700/50 rounded-lg p-3">
                <div className="text-slate-400 text-sm">{stat.label}</div>
                <div className="text-white font-semibold text-lg">
                  {typeof stat.value === 'number' 
                    ? stat.label.includes('Average') ? stat.value.toFixed(3) : stat.value.toFixed(0)
                    : stat.value || 'N/A'
                  }
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const allStats = getAllPlayerStats(player);
  const categorizedStats = categorizeStats(allStats);

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-start justify-center p-4 pt-20">
      <div className="bg-slate-800 rounded-2xl border border-slate-700 max-w-4xl w-full max-h-[85vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-yellow-500 rounded-xl flex items-center justify-center mr-4">
                <span className="text-2xl">{player.image || '🏆'}</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">{player.name}</h1>
                <div className="flex items-center gap-4 mt-1">
                  <span className="text-yellow-400 font-medium">{player.position}</span>
                  {player.team && <span className="text-slate-400">{player.team}</span>}
                  {player.playerType && (
                    <span className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded text-xs font-medium">
                      {player.playerType.charAt(0).toUpperCase() + player.playerType.slice(1)}
                    </span>
                  )}
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white transition-colors p-2"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Key Projections (for MLB) - Only show if displayStats exists */}
          {player.stats?.displayStats && renderDisplayStats(player.stats.displayStats)}

          {/* Categorized Stats */}
          {Object.entries(categorizedStats).map(([category, stats]) => (
            <div key={category} className="mb-6">
              <h3 className="text-lg font-semibold text-yellow-400 mb-3">{category}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {stats.map(({ key, value }) => (
                  <div key={key} className="bg-slate-700/50 rounded-lg p-3">
                    <div className="text-slate-400 text-sm">{formatStatName(key)}</div>
                    <div className="text-white font-semibold text-lg">
                      {formatStatValue(value, key)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Sport-specific information */}
          <div className="mt-6 p-4 bg-slate-700/30 rounded-lg">
            <h3 className="text-yellow-400 font-semibold mb-2">Model Information</h3>
            <div className="text-slate-300 text-sm space-y-1">
              <div>Sport: <span className="text-white font-medium">{sport?.toUpperCase() || 'Unknown'}</span></div>
              <div>Predictions powered by machine learning models trained on historical performance data</div>
              {(allStats.confidence || player.confidence) && (
                <div>Model Confidence: <span className="text-white font-medium">{formatStatValue(allStats.confidence || player.confidence, 'confidence')}</span></div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center gap-4 mt-6">
            <button
              onClick={() => setShowBetting(true)}
              className="px-6 py-3 bg-gradient-to-r from-green-600 to-yellow-500 text-white rounded-lg font-medium hover:from-green-700 hover:to-yellow-600 transition-all flex items-center gap-2"
            >
              <span>💰</span>
              Place Bet
            </button>
            <button
              onClick={onClose}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-slate-500 text-white rounded-lg font-medium hover:from-blue-700 hover:to-slate-600 transition-all"
            >
              Back to Players
            </button>
          </div>
        </div>
      </div>

      {/* Betting Modal */}
      {showBetting && (
        <PlayerBetting
          player={player}
          sport={sport}
          onClose={() => setShowBetting(false)}
          onPlaceBet={handlePlaceBet}
        />
      )}
    </div>
  );
};

export default PlayerProfile;