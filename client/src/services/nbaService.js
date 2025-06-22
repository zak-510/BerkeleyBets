const API_BASE_URL = 'http://localhost:8081/api';

class NBAService {
  async fetchAllPlayers() {
    try {
      const response = await fetch(`${API_BASE_URL}/players`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching all NBA players:', error);
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
      console.error(`Error fetching NBA players for position ${position}:`, error);
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
      console.error(`Error searching NBA players with query "${query}":`, error);
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
      console.error(`Error fetching top NBA players for position ${position}:`, error);
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
      console.error('Error fetching NBA model stats:', error);
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
      console.error('Error checking NBA API health:', error);
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
        predictedRebounds: apiPlayer.predictedRebounds,
        predictedAssists: apiPlayer.predictedAssists,
        predictedFantasyPoints: apiPlayer.predictedFantasyPoints,
        pointsAccuracy: apiPlayer.pointsAccuracy,
        reboundsAccuracy: apiPlayer.reboundsAccuracy,
        assistsAccuracy: apiPlayer.assistsAccuracy,
        overallAccuracy: apiPlayer.overallAccuracy
      },
      image: this.getPositionIcon(apiPlayer.position)
    };
  }

  getPositionIcon(position) {
    const icons = {
      'PG': '🏀',
      'SG': '🏀',
      'SF': '🏀',
      'PF': '🏀',
      'C': '🏀'
    };
    return icons[position] || '🏀';
  }

  getTeamByPosition(position) {
    // This is a placeholder - in a real app you'd have a proper team mapping
    const teams = [
      'Los Angeles Lakers', 'Golden State Warriors', 'Boston Celtics', 'Miami Heat',
      'Milwaukee Bucks', 'Phoenix Suns', 'Philadelphia 76ers', 'Brooklyn Nets',
      'Denver Nuggets', 'Memphis Grizzlies', 'Dallas Mavericks', 'New Orleans Pelicans',
      'Cleveland Cavaliers', 'Atlanta Hawks', 'Toronto Raptors', 'Chicago Bulls',
      'Minnesota Timberwolves', 'New York Knicks', 'Oklahoma City Thunder', 'Sacramento Kings',
      'Los Angeles Clippers', 'Utah Jazz', 'Washington Wizards', 'Indiana Pacers',
      'Charlotte Hornets', 'San Antonio Spurs', 'Portland Trail Blazers', 'Orlando Magic',
      'Detroit Pistons', 'Houston Rockets'
    ];
    // Return a random team for now - in production you'd have actual team mappings
    return teams[Math.floor(Math.random() * teams.length)];
  }
}

export default new NBAService(); 