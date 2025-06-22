const API_BASE_URL = 'http://localhost:5001/api';

class NFLService {
  async fetchAllPlayers() {
    try {
      const response = await fetch(`${API_BASE_URL}/players`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching all players:', error);
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
      console.error(`Error fetching players for position ${position}:`, error);
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
      console.error(`Error searching players with query "${query}":`, error);
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
      console.error(`Error fetching top players for position ${position}:`, error);
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
      console.error('Error fetching model stats:', error);
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
      console.error('Error checking API health:', error);
      throw error;
    }
  }

  // Helper method to format player data for the UI
  formatPlayerForUI(apiPlayer) {
    return {
      id: apiPlayer.name.toLowerCase().replace(/\s+/g, '-'),
      name: apiPlayer.name,
      team: this.getTeamByPosition(apiPlayer.position), // We'll need to map this
      position: apiPlayer.position,
      stats: {
        predictedPoints: apiPlayer.predictedPoints,
        actualPoints: apiPlayer.actualPoints,
        confidence: apiPlayer.confidence,
        accuracy: apiPlayer.accuracy,
        error: apiPlayer.error
      },
      image: this.getPositionIcon(apiPlayer.position)
    };
  }

  getPositionIcon(position) {
    const icons = {
      'QB': '🏈',
      'RB': '🏃‍♂️',
      'WR': '🏃‍♂️',
      'TE': '🏈'
    };
    return icons[position] || '🏈';
  }

  getTeamByPosition(position) {
    // This is a placeholder - in a real app you'd have a proper team mapping
    const teams = [
      'Kansas City Chiefs', 'Buffalo Bills', 'Cincinnati Bengals', 'Miami Dolphins',
      'San Francisco 49ers', 'Dallas Cowboys', 'Philadelphia Eagles', 'Minnesota Vikings',
      'Seattle Seahawks', 'Green Bay Packers', 'Tampa Bay Buccaneers', 'Los Angeles Rams',
      'Baltimore Ravens', 'Cleveland Browns', 'Pittsburgh Steelers', 'Tennessee Titans',
      'Indianapolis Colts', 'Jacksonville Jaguars', 'Houston Texans', 'Las Vegas Raiders',
      'Los Angeles Chargers', 'Denver Broncos', 'New York Jets', 'New England Patriots',
      'Detroit Lions', 'Chicago Bears', 'Atlanta Falcons', 'New Orleans Saints',
      'Carolina Panthers', 'Washington Commanders', 'New York Giants', 'Arizona Cardinals'
    ];
    // Return a random team for now - in production you'd have actual team mappings
    return teams[Math.floor(Math.random() * teams.length)];
  }
}

export default new NFLService(); 