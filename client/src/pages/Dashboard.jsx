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

  const teams = [
    {
      id: 'cal',
      name: 'Berkeley Bears',
      logo: '🐻',
      color: 'text-yellow-400'
    },
    {
      id: 'ucla',
      name: 'UCLA Bruins',
      logo: '🐻',
      color: 'text-blue-400'
    }
  ];

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

        {/* Teams/Games Section */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-slate-800/30 backdrop-blur-lg rounded-2xl border border-slate-700/50 p-6">
            <div className="space-y-4">
              {teams.map((team) => (
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

            {/* Add More Teams Button */}
            <div className="mt-6 text-center">
              <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-yellow-500 text-white rounded-lg font-medium hover:from-blue-700 hover:to-yellow-600 transition-all">
                + Add More Teams
              </button>
            </div>
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
