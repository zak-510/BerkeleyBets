import { useState } from 'react';

const Dashboard = () => {
  const [bearBucks, setBearBucks] = useState(1500);
  const [selectedSport, setSelectedSport] = useState('');

  const sports = [
    { id: 'nfl', name: 'NFL', icon: '🏈' },
    { id: 'nba', name: 'NBA', icon: '🏀' },
    { id: 'ncaa', name: 'NCAA', icon: '🏀' },
    { id: 'mlb', name: 'MLB', icon: '⚾' }
  ];

  // Sample player data - you can replace with real API data
  const players = {
    nfl: [
      {
        id: 'mahomes',
        name: 'Patrick Mahomes',
        team: 'Kansas City Chiefs',
        position: 'QB',
        stats: {
          passingYards: 4183,
          touchdowns: 31,
          interceptions: 8,
          completionRate: 66.3
        },
        image: '🏈'
      },
      {
        id: 'mccaffrey',
        name: 'Christian McCaffrey',
        team: 'San Francisco 49ers',
        position: 'RB',
        stats: {
          rushingYards: 1459,
          touchdowns: 14,
          receptions: 67,
          receivingYards: 564
        },
        image: '🏈'
      }
    ],
    nba: [
      {
        id: 'jokic',
        name: 'Nikola Jokić',
        team: 'Denver Nuggets',
        position: 'C',
        stats: {
          points: 26.4,
          rebounds: 12.4,
          assists: 9.0,
          fieldGoalPercentage: 58.3
        },
        image: '🏀'
      },
      {
        id: 'embiid',
        name: 'Joel Embiid',
        team: 'Philadelphia 76ers',
        position: 'C',
        stats: {
          points: 35.3,
          rebounds: 11.3,
          assists: 5.7,
          fieldGoalPercentage: 53.8
        },
        image: '🏀'
      }
    ],
    mlb: [
      {
        id: 'ohtani',
        name: 'Shohei Ohtani',
        team: 'Los Angeles Dodgers',
        position: 'DH/SP',
        stats: {
          battingAvg: 0.304,
          homeRuns: 44,
          rbi: 95,
          era: 3.14
        },
        image: '⚾'
      },
      {
        id: 'judge',
        name: 'Aaron Judge',
        team: 'New York Yankees',
        position: 'RF',
        stats: {
          battingAvg: 0.267,
          homeRuns: 37,
          rbi: 75,
          onBasePercentage: 0.406
        },
        image: '⚾'
      }
    ]
  };

  const teams = [
    {
      id: 'cal',
      name: 'Berkeley Bears',
      logo: '🐻',
      color: 'text-yellow-400',
      sport: 'ncaa'
    },
    {
      id: 'ucla',
      name: 'UCLA Bruins',
      logo: '🐻',
      color: 'text-blue-400',
      sport: 'ncaa'
    }
  ];

  // Filter teams based on selected sport
  const getFilteredTeams = () => {
    if (selectedSport === 'ncaa') {
      // For NCAA, only show Berkeley teams
      return teams.filter(team => team.id === 'cal');
    } else if (selectedSport) {
      // For other sports, show all teams (you can expand this with more teams for other sports)
      return teams;
    }
    return [];
  };

  const filteredTeams = getFilteredTeams();
  const currentPlayers = players[selectedSport] || [];

  const renderPlayerCard = (player) => {
    const getStatDisplay = () => {
      switch (selectedSport) {
        case 'nfl':
          return (
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">Pass Yards</div>
                <div className="text-white font-semibold">{player.stats.passingYards?.toLocaleString() || player.stats.rushingYards?.toLocaleString()}</div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">TDs</div>
                <div className="text-white font-semibold">{player.stats.touchdowns}</div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">{player.position === 'QB' ? 'INTs' : 'Receptions'}</div>
                <div className="text-white font-semibold">{player.stats.interceptions || player.stats.receptions}</div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">{player.position === 'QB' ? 'Comp %' : 'Rec Yards'}</div>
                <div className="text-white font-semibold">{player.stats.completionRate || player.stats.receivingYards?.toLocaleString()}</div>
              </div>
            </div>
          );
        case 'nba':
          return (
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">PPG</div>
                <div className="text-white font-semibold">{player.stats.points}</div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">RPG</div>
                <div className="text-white font-semibold">{player.stats.rebounds}</div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">APG</div>
                <div className="text-white font-semibold">{player.stats.assists}</div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">FG%</div>
                <div className="text-white font-semibold">{player.stats.fieldGoalPercentage}%</div>
              </div>
            </div>
          );
        case 'mlb':
          return (
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">AVG</div>
                <div className="text-white font-semibold">{player.stats.battingAvg}</div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">HR</div>
                <div className="text-white font-semibold">{player.stats.homeRuns}</div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">RBI</div>
                <div className="text-white font-semibold">{player.stats.rbi}</div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">{player.stats.era ? 'ERA' : 'OBP'}</div>
                <div className="text-white font-semibold">{player.stats.era || player.stats.onBasePercentage}</div>
              </div>
            </div>
          );
        default:
          return null;
      }
    };

    return (
      <div
        key={player.id}
        className="bg-slate-700/30 rounded-xl border border-slate-600/50 hover:border-slate-500/70 transition-all cursor-pointer group p-4"
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-yellow-500 rounded-lg flex items-center justify-center mr-3">
              <span className="text-xl">{player.image}</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white group-hover:text-yellow-400 transition-colors">
                {player.name}
              </h3>
              <p className="text-slate-400 text-sm">{player.team}</p>
              <p className="text-yellow-400 text-xs font-medium">{player.position}</p>
            </div>
          </div>
          <div className="text-slate-400 group-hover:text-white transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
        {getStatDisplay()}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Background Pattern */}
      <div className="absolute inset-0" style={{
        backgroundImage: 'radial-gradient(circle, rgba(255, 215, 0, 0.05) 1px, transparent 1px)',
        backgroundSize: '30px 30px'
      }}></div>

      <div className="relative z-10 p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          {/* Logo and Title */}
          <div className="flex items-center">
            <div className="flex items-center mr-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-yellow-500 rounded-lg flex items-center justify-center mr-3">
                <span className="text-xl font-bold text-white">Cal</span>
              </div>
              <div className="border-2 border-purple-500 px-6 py-2 rounded-lg">
                <h1 className="text-3xl font-bold text-yellow-400">BerkeleyBets</h1>
              </div>
            </div>
          </div>

          {/* Bear Bucks Balance */}
          <div className="text-right">
            <p className="text-slate-300 text-sm">Bear Bucks</p>
            <p className="text-4xl font-bold text-green-400">{bearBucks.toLocaleString()}</p>
          </div>
        </div>

        {/* Sports Selection */}
        <div className="mb-8">
          <div className="flex justify-center space-x-8">
            {sports.map((sport) => (
              <button
                key={sport.id}
                onClick={() => setSelectedSport(sport.id)}
                className={`w-20 h-20 rounded-xl border-2 flex items-center justify-center transition-all hover:scale-105 ${
                  selectedSport === sport.id
                    ? 'border-yellow-400 bg-yellow-400/20'
                    : 'border-slate-600 bg-slate-800/50 hover:border-slate-500'
                }`}
              >
                <div className="text-center">
                  <div className="text-2xl mb-1">{sport.icon}</div>
                  <div className="text-xs text-slate-300 font-medium">{sport.name}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Content Section */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-slate-800/30 backdrop-blur-lg rounded-2xl border border-slate-700/50 p-6">
            {selectedSport ? (
              <>
                {selectedSport === 'ncaa' ? (
                  // NCAA Teams Section
                  <>
                    <div className="space-y-4">
                      {filteredTeams.map((team) => (
                        <div
                          key={team.id}
                          className="flex items-center p-4 bg-slate-700/30 rounded-xl border border-slate-600/50 hover:border-slate-500/70 transition-all cursor-pointer group"
                        >
                          {/* Team Logo */}
                          <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-yellow-500 rounded-lg flex items-center justify-center mr-4">
                            <span className="text-xl">{team.logo}</span>
                          </div>

                          {/* Team Name */}
                          <div className="flex-1">
                            <h3 className={`text-xl font-semibold ${team.color} group-hover:text-white transition-colors`}>
                              {team.name}
                            </h3>
                          </div>

                          {/* Action Arrow */}
                          <div className="text-slate-400 group-hover:text-white transition-colors">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  // Players Section for NFL, NBA, MLB
                  <>
                    <div className="space-y-4">
                      {currentPlayers.map(renderPlayerCard)}
                    </div>
                    
                    {/* Add More Players Button */}
                    <div className="mt-6 text-center">
                      <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-yellow-500 text-white rounded-lg font-medium hover:from-blue-700 hover:to-yellow-600 transition-all">
                        + Add More Players
                      </button>
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-slate-300 text-lg">Select a sport to view available teams/players</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="max-w-4xl mx-auto mt-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-800/30 backdrop-blur-lg rounded-xl border border-slate-700/50 p-4 text-center">
              <div className="text-2xl font-bold text-green-400">12</div>
              <div className="text-slate-300 text-sm">Active Bets</div>
            </div>
            <div className="bg-slate-800/30 backdrop-blur-lg rounded-xl border border-slate-700/50 p-4 text-center">
              <div className="text-2xl font-bold text-blue-400">68%</div>
              <div className="text-slate-300 text-sm">Win Rate</div>
            </div>
            <div className="bg-slate-800/30 backdrop-blur-lg rounded-xl border border-slate-700/50 p-4 text-center">
              <div className="text-2xl font-bold text-yellow-400">+$342</div>
              <div className="text-slate-300 text-sm">This Week</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
