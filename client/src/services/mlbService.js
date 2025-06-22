const API_BASE_URL = 'http://localhost:3001/api/mlb';

class MLBService {
  async fetchAllPlayers() {
    try {
      const response = await fetch(`${API_BASE_URL}/players`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching all MLB players:', error);
      throw error;
    }
  }

  async fetchPlayersByPosition(position) {
    try {
      const response = await fetch(`${API_BASE_URL}/players/${position}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error fetching MLB players for position ${position}:`, error);
      throw error;
    }
  }

  async searchPlayers(query) {
    try {
      const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error searching MLB players with query "${query}":`, error);
      throw error;
    }
  }

  async fetchTopPlayers(position = 'ALL', limit = 50) {
    try {
      const response = await fetch(`${API_BASE_URL}/players/top?limit=${limit}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error fetching top MLB players for position ${position}:`, error);
      throw error;
    }
  }

  async fetchModelStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching MLB model stats:', error);
      throw error;
    }
  }

  async healthCheck() {
    try {
      const response = await fetch(`http://localhost:3001/health`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error checking MLB API health:', error);
      throw error;
    }
  }

  // Helper method to format player data for the UI
  formatPlayerForUI(apiPlayer) {
    return {
      id: apiPlayer.player_name?.toLowerCase().replace(/\s+/g, '-') || apiPlayer.name?.toLowerCase().replace(/\s+/g, '-'),
      name: apiPlayer.player_name || apiPlayer.name,
      position: apiPlayer.position,
      playerType: apiPlayer.player_type || apiPlayer.playerType,
      stats: this.formatStatsForUI(apiPlayer),
      image: this.getPositionIcon(apiPlayer.position)
    };
  }

  formatStatsForUI(apiPlayer) {
    const playerType = apiPlayer.player_type || apiPlayer.playerType;
    
    // Helper function to safely get numeric values
    const safeNumber = (value, fallback = 0) => {
      if (value === null || value === undefined || value === 'N/A' || isNaN(value)) {
        return fallback;
      }
      return Number(value);
    };

    // Helper function to format display values
    const formatDisplayValue = (value, decimals = 0) => {
      const num = safeNumber(value);
      return num > 0 ? num.toFixed(decimals) : 'TBD';
    };

    if (playerType === 'pitcher') {
      const strikeouts = safeNumber(apiPlayer.projectedStrikeouts);
      const innings = safeNumber(apiPlayer.projectedInningsPitched);
      
      return {
        predictedFantasyPoints: safeNumber(apiPlayer.predicted_fantasy_points || apiPlayer.predictedFantasyPoints),
        fantasyConfidence: safeNumber(apiPlayer.confidence || apiPlayer.fantasyConfidence, 0.75),
        projectedStrikeouts: strikeouts,
        projectedInningsPitched: innings,
        strikeoutsConfidence: safeNumber(apiPlayer.strikeoutsConfidence, 0.80),
        inningsPitchedConfidence: safeNumber(apiPlayer.inningsPitchedConfidence, 0.75),
        displayStats: [
          { label: 'Projected Strikeouts', value: formatDisplayValue(strikeouts) },
          { label: 'Projected Innings Pitched', value: formatDisplayValue(innings, 1) }
        ]
      };
    } else {
      const hits = safeNumber(apiPlayer.projectedHits);
      const runs = safeNumber(apiPlayer.projectedRuns);
      const rbis = safeNumber(apiPlayer.projectedRBIs);
      
      return {
        predictedFantasyPoints: safeNumber(apiPlayer.predicted_fantasy_points || apiPlayer.predictedFantasyPoints),
        fantasyConfidence: safeNumber(apiPlayer.confidence || apiPlayer.fantasyConfidence, 0.75),
        projectedHits: hits,
        projectedRuns: runs,
        projectedRBIs: rbis,
        battingAvg: safeNumber(apiPlayer.battingAvg || apiPlayer.batting_average_skill, 0.250),
        onBasePct: safeNumber(apiPlayer.onBasePct || apiPlayer.on_base_percentage_skill, 0.320),
        sluggingPct: safeNumber(apiPlayer.sluggingPct || apiPlayer.slugging_percentage_skill, 0.400),
        skillConfidence: safeNumber(apiPlayer.skillConfidence, 0.80),
        displayStats: [
          { label: 'Projected Hits', value: formatDisplayValue(hits) },
          { label: 'Projected Runs', value: formatDisplayValue(runs) },
          { label: 'Projected RBIs', value: formatDisplayValue(rbis) }
        ]
      };
    }
  }

  getPositionIcon(position) {
    const icons = {
      'P': '⚾',
      '1B': '🥇',
      '2B': '🥈', 
      '3B': '🥉',
      'SS': '⚡',
      'C': '🧤',
      'OF': '🏃‍♂️',
      'LF': '🏃‍♂️',
      'CF': '🏃‍♂️',
      'RF': '🏃‍♂️',
      'DH': '💪'
    };
    return icons[position] || '⚾';
  }



  // Get available positions for filtering
  getAvailablePositions() {
    return [
      { value: 'ALL', label: 'All Positions' },
      { value: 'P', label: 'Pitcher' },
      { value: '1B', label: 'First Base' },
      { value: '2B', label: 'Second Base' },
      { value: '3B', label: 'Third Base' },
      { value: 'SS', label: 'Shortstop' },
      { value: 'C', label: 'Catcher' },
      { value: 'OF', label: 'Outfield' },
      { value: 'DH', label: 'Designated Hitter' }
    ];
  }
}

export default new MLBService(); 