import React, { useState, useContext, useEffect } from 'react';
import { Context } from '..';
import { useBetting } from '../contexts/BettingContext';

const BettingPortfolio = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('active');

  const ctx = useContext(Context);
  const betting = useBetting();

  // Get betting data from context
  const activeBets = betting.activeBets;
  const completedBets = betting.bettingHistory;
  const portfolioStats = betting.getPortfolioStats();

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return '⏱️';
      case 'won': return '✅';
      case 'lost': return '❌';
      default: return '⏱️';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-yellow-400';
      case 'won': return 'text-green-400';
      case 'lost': return 'text-red-400';
      default: return 'text-yellow-400';
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleCashOut = (betId) => {
    const cashOutAmount = betting.cashOutBet(betId);
    if (cashOutAmount) {
      alert(`Successfully cashed out! You received ${cashOutAmount} Bear Bucks.`);
    }
  };

  const handleSimulateBet = (betId) => {
    betting.simulateBetResult(betId);
  };

  const renderBetCard = (bet) => (
    <div key={bet.id} className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getStatusIcon(bet.status)}</span>
          <div>
            <h3 className="font-semibold text-white">{bet.playerName}</h3>
            <p className="text-slate-400 text-sm">{bet.sport.toUpperCase()} • {formatDate(bet.timestamp)}</p>
          </div>
        </div>
        <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(bet.status)} bg-current bg-opacity-20`}>
          {bet.status.toUpperCase()}
        </div>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-400">Prediction:</span>
          <span className="text-white">
            {bet.statLabel} {bet.direction} {bet.target}
          </span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-slate-400">Wager:</span>
          <span className="text-white">{bet.amount} Bear Bucks</span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-slate-400">Potential Payout:</span>
          <span className="text-green-400">{bet.potentialPayout} Bear Bucks</span>
        </div>

        {bet.actualResult && (
          <div className="flex justify-between">
            <span className="text-slate-400">Actual Result:</span>
            <span className={bet.status === 'won' ? 'text-green-400' : 'text-red-400'}>
              {bet.actualResult}
            </span>
          </div>
        )}

        <div className="flex justify-between">
          <span className="text-slate-400">Confidence:</span>
          <span className="text-white">{Math.round(bet.confidence * 100)}%</span>
        </div>
      </div>

      {bet.status === 'active' && (
        <div className="mt-3 pt-3 border-t border-slate-600">
          <div className="flex gap-2">
            <button 
              onClick={() => handleCashOut(bet.id)}
              className="flex-1 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
            >
              Cash Out Early ({Math.round(bet.amount * 0.75)} BB)
            </button>
            <button 
              onClick={() => handleSimulateBet(bet.id)}
              className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
            >
              Simulate Result
            </button>
          </div>
        </div>
      )}
    </div>
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-2xl border border-slate-700 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-16 h-16 bg-gradient-to-r from-green-600 to-yellow-500 rounded-xl flex items-center justify-center mr-4">
                <span className="text-2xl">📊</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Betting Portfolio</h1>
                <p className="text-slate-400">Track your predictions and performance</p>
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

        {/* Portfolio Stats */}
        <div className="p-6 border-b border-slate-700">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-700/50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-400">{portfolioStats.activeBets}</div>
              <div className="text-slate-400 text-sm">Active Bets</div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-yellow-400">{portfolioStats.totalWagered}</div>
              <div className="text-slate-400 text-sm">Total Wagered</div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-400">{portfolioStats.totalWon}</div>
              <div className="text-slate-400 text-sm">Total Won</div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-400">{portfolioStats.winRate.toFixed(1)}%</div>
              <div className="text-slate-400 text-sm">Win Rate</div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="p-6 pb-0">
          <div className="flex space-x-1 bg-slate-700/50 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('active')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'active'
                  ? 'bg-yellow-400 text-slate-900'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              Active Bets ({activeBets.length})
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'history'
                  ? 'bg-yellow-400 text-slate-900'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              History ({completedBets.length})
            </button>
          </div>
        </div>

        {/* Bet Lists */}
        <div className="p-6">
          {activeTab === 'active' ? (
            <div className="space-y-4">
              {activeBets.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-6xl mb-4">🎯</div>
                  <h3 className="text-xl font-semibold text-white mb-2">No Active Bets</h3>
                  <p className="text-slate-400">Place your first bet on a player to get started!</p>
                </div>
              ) : (
                activeBets.map(renderBetCard)
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {completedBets.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-6xl mb-4">📈</div>
                  <h3 className="text-xl font-semibold text-white mb-2">No Betting History</h3>
                  <p className="text-slate-400">Your completed bets will appear here.</p>
                </div>
              ) : (
                completedBets.map(renderBetCard)
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BettingPortfolio;