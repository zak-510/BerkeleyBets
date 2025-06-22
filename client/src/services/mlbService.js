const API_BASE_URL = 'http://localhost:8082/api';

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

  async fetchTopPlayers(position = 'ALL', limit = 20) {
    try {
      const response = await fetch(`${API_BASE_URL}/top/${position}/${limit}`);
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
      const response = await fetch(`${API_BASE_URL}/health`);
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
      id: apiPlayer.name.toLowerCase().replace(/\s+/g, '-'),
      name: apiPlayer.name,
      position: apiPlayer.position,
      playerType: apiPlayer.playerType,
      stats: this.formatStatsForUI(apiPlayer),
      image: this.getPositionIcon(apiPlayer.position)
    };
  }

  formatStatsForUI(apiPlayer) {
    if (apiPlayer.playerType === 'pitcher') {
      return {
        predictedFantasyPoints: apiPlayer.predictedFantasyPoints,
        fantasyConfidence: apiPlayer.fantasyConfidence,
        projectedStrikeouts: apiPlayer.projectedStrikeouts,
        projectedInningsPitched: apiPlayer.projectedInningsPitched,
        strikeoutsConfidence: apiPlayer.strikeoutsConfidence,
        inningsPitchedConfidence: apiPlayer.inningsPitchedConfidence,
        displayStats: [
          { label: 'Projected Strikeouts', value: apiPlayer.projectedStrikeouts },
          { label: 'Projected Innings Pitched', value: apiPlayer.projectedInningsPitched }
        ]
      };
    } else {
      return {
        predictedFantasyPoints: apiPlayer.predictedFantasyPoints,
        fantasyConfidence: apiPlayer.fantasyConfidence,
        projectedHits: apiPlayer.projectedHits,
        projectedRuns: apiPlayer.projectedRuns,
        projectedRBIs: apiPlayer.projectedRBIs,
        battingAvg: apiPlayer.battingAvg,
        onBasePct: apiPlayer.onBasePct,
        sluggingPct: apiPlayer.sluggingPct,
        skillConfidence: apiPlayer.skillConfidence,
        displayStats: [
          { label: 'Projected Hits', value: apiPlayer.projectedHits },
          { label: 'Projected Runs', value: apiPlayer.projectedRuns },
          { label: 'Projected RBIs', value: apiPlayer.projectedRBIs }
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