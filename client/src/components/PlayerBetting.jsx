import React, { useState, useContext } from 'react';
import { Context } from '..';
import { useBetting } from '../contexts/BettingContext';

const PlayerBetting = ({ player, sport, onClose, onPlaceBet }) => {
  const [selectedBetType, setSelectedBetType] = useState('');
  const [betAmount, setBetAmount] = useState(50);
  const [customTarget, setCustomTarget] = useState('');
  const [betDirection, setBetDirection] = useState('over'); // 'over', 'under', 'exact'
  const [showConfirmation, setShowConfirmation] = useState(false);

  const ctx = useContext(Context);
  const betting = useBetting();
  const userBearBucks = ctx.bearBucks || 1500;

  if (!player) return null;

  // Get available betting options based on sport and player stats
  const getBettingOptions = () => {
    const options = [];
    
    // Always include fantasy points
    if (player.stats?.predictedPoints || player.predicted_fantasy_points) {
      const prediction = player.stats?.predictedPoints || player.predicted_fantasy_points;
      options.push({
        id: 'fantasy_points',
        label: 'Fantasy Points',
        prediction: Math.round(prediction * 10) / 10,
        type: 'numeric',
        description: `Predicted: ${Math.round(prediction * 10) / 10} points`
      });
    }

    // Sport-specific options
    if (sport === 'nba') {
      if (player.stats?.predictedRebounds || player.predicted_rebounds) {
        options.push({
          id: 'rebounds',
          label: 'Rebounds',
          prediction: Math.round((player.stats?.predictedRebounds || player.predicted_rebounds) * 10) / 10,
          type: 'numeric'
        });
      }
      if (player.stats?.predictedAssists || player.predicted_assists) {
        options.push({
          id: 'assists',
          label: 'Assists',
          prediction: Math.round((player.stats?.predictedAssists || player.predicted_assists) * 10) / 10,
          type: 'numeric'
        });
      }
    }

    if (sport === 'nfl') {
      if (player.passing_yards) {
        options.push({
          id: 'passing_yards',
          label: 'Passing Yards',
          prediction: player.passing_yards,
          type: 'numeric'
        });
      }
      if (player.rushing_yards) {
        options.push({
          id: 'rushing_yards',
          label: 'Rushing Yards',
          prediction: player.rushing_yards,
          type: 'numeric'
        });
      }
      if (player.receiving_yards) {
        options.push({
          id: 'receiving_yards',
          label: 'Receiving Yards',
          prediction: player.receiving_yards,
          type: 'numeric'
        });
      }
      if (player.passing_tds) {
        options.push({
          id: 'passing_tds',
          label: 'Passing TDs',
          prediction: player.passing_tds,
          type: 'numeric'
        });
      }
      if (player.receptions) {
        options.push({
          id: 'receptions',
          label: 'Receptions',
          prediction: player.receptions,
          type: 'numeric'
        });
      }
    }

    if (sport === 'mlb') {
      if (player.projectedHits || player.stats?.projectedHits) {
        options.push({
          id: 'hits',
          label: 'Hits',
          prediction: player.projectedHits || player.stats?.projectedHits,
          type: 'numeric'
        });
      }
      if (player.projectedRuns || player.stats?.projectedRuns) {
        options.push({
          id: 'runs',
          label: 'Runs',
          prediction: player.projectedRuns || player.stats?.projectedRuns,
          type: 'numeric'
        });
      }
      if (player.projectedRBIs || player.stats?.projectedRBIs) {
        options.push({
          id: 'rbis',
          label: 'RBIs',
          prediction: player.projectedRBIs || player.stats?.projectedRBIs,
          type: 'numeric'
        });
      }
    }

    return options;
  };

  const bettingOptions = getBettingOptions();
  const selectedOption = bettingOptions.find(opt => opt.id === selectedBetType);

  // Calculate potential payout based on bet type and odds
  const calculatePayout = () => {
    if (!selectedOption || !betAmount) return 0;

    let multiplier = 1.8; // Base multiplier
    
    // Adjust multiplier based on bet type and difficulty
    if (betDirection === 'exact') {
      multiplier = 5.0; // Higher payout for exact predictions
    } else if (betDirection === 'over' || betDirection === 'under') {
      multiplier = 1.9; // Standard over/under
    }

    // Custom target adjusts multiplier based on distance from prediction
    if (customTarget && selectedOption.prediction) {
      const target = parseFloat(customTarget);
      const prediction = selectedOption.prediction;
      const variance = Math.abs(target - prediction) / prediction;
      
      if (variance > 0.3) {
        multiplier += 1.0; // Bonus for bold predictions
      } else if (variance < 0.1) {
        multiplier -= 0.3; // Lower payout for safe bets
      }
    }

    return Math.round(betAmount * multiplier);
  };

  const handlePlaceBet = () => {
    if (!selectedOption || !betAmount || betAmount > userBearBucks) return;

    const target = customTarget ? parseFloat(customTarget) : selectedOption.prediction;
    const payout = calculatePayout();

    const bet = {
      playerId: player.id || player.player_name,
      playerName: player.name || player.player_name,
      sport: sport,
      statType: selectedOption.id,
      statLabel: selectedOption.label,
      prediction: selectedOption.prediction,
      target: target,
      direction: betDirection,
      amount: betAmount,
      potentialPayout: payout,
      confidence: player.confidence || player.stats?.confidence || 0.75
    };

    // Use the betting context to place the bet (it will handle Bear Bucks deduction)
    betting.placeBet(bet);

    onPlaceBet?.(bet);
    setShowConfirmation(true);
    
    // Auto-close after success
    setTimeout(() => {
      onClose();
    }, 2000);
  };

  const getBetDescription = () => {
    if (!selectedOption) return '';
    
    const target = customTarget ? parseFloat(customTarget) : selectedOption.prediction;
    const direction = betDirection === 'exact' ? 'exactly' : betDirection;
    
    return `${player.name || player.player_name} will score ${direction} ${target} ${selectedOption.label.toLowerCase()}`;
  };

  if (showConfirmation) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div className="bg-slate-800 rounded-2xl border border-green-500 p-8 max-w-md w-full text-center">
          <div className="text-green-400 text-6xl mb-4">✓</div>
          <h2 className="text-2xl font-bold text-white mb-2">Bet Placed!</h2>
          <p className="text-slate-300 mb-4">
            You wagered {betAmount} Bear Bucks on {getBetDescription()}
          </p>
          <p className="text-yellow-400 font-semibold">
            Potential payout: {calculatePayout()} Bear Bucks
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-2xl border border-slate-700 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-gradient-to-r from-green-600 to-yellow-500 rounded-xl flex items-center justify-center mr-4">
                <span className="text-2xl">💰</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Place Bet</h1>
                <p className="text-slate-400">{player.name || player.player_name} • {player.position}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-yellow-400 font-bold">{userBearBucks} Bear Bucks</div>
              <div className="text-slate-400 text-sm">Available</div>
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
        <div className="p-6 space-y-6">
          {/* Bet Selection */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">Choose What to Bet On</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {bettingOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => setSelectedBetType(option.id)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    selectedBetType === option.id
                      ? 'border-yellow-400 bg-yellow-400/10'
                      : 'border-slate-600 bg-slate-700/50 hover:border-slate-500'
                  }`}
                >
                  <div className="font-semibold text-white">{option.label}</div>
                  <div className="text-slate-400 text-sm">Predicted: {option.prediction}</div>
                </button>
              ))}
            </div>
          </div>

          {selectedOption && (
            <>
              {/* Bet Type */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Bet Type</h3>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    onClick={() => setBetDirection('over')}
                    className={`p-3 rounded-lg border-2 text-center transition-all ${
                      betDirection === 'over'
                        ? 'border-green-400 bg-green-400/10 text-green-400'
                        : 'border-slate-600 bg-slate-700/50 text-slate-300 hover:border-slate-500'
                    }`}
                  >
                    <div className="font-semibold">Over</div>
                    <div className="text-xs">1.9x payout</div>
                  </button>
                  <button
                    onClick={() => setBetDirection('under')}
                    className={`p-3 rounded-lg border-2 text-center transition-all ${
                      betDirection === 'under'
                        ? 'border-red-400 bg-red-400/10 text-red-400'
                        : 'border-slate-600 bg-slate-700/50 text-slate-300 hover:border-slate-500'
                    }`}
                  >
                    <div className="font-semibold">Under</div>
                    <div className="text-xs">1.9x payout</div>
                  </button>
                  <button
                    onClick={() => setBetDirection('exact')}
                    className={`p-3 rounded-lg border-2 text-center transition-all ${
                      betDirection === 'exact'
                        ? 'border-purple-400 bg-purple-400/10 text-purple-400'
                        : 'border-slate-600 bg-slate-700/50 text-slate-300 hover:border-slate-500'
                    }`}
                  >
                    <div className="font-semibold">Exact</div>
                    <div className="text-xs">5.0x payout</div>
                  </button>
                </div>
              </div>

              {/* Custom Target */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">
                  Target {selectedOption.label}
                  <span className="text-slate-400 text-sm font-normal ml-2">
                    (Prediction: {selectedOption.prediction})
                  </span>
                </h3>
                <input
                  type="number"
                  value={customTarget}
                  onChange={(e) => setCustomTarget(e.target.value)}
                  placeholder={selectedOption.prediction.toString()}
                  className="w-full px-4 py-3 bg-slate-700 rounded-lg border border-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />
                <p className="text-slate-400 text-sm mt-2">
                  Leave empty to use model prediction, or enter your own target
                </p>
              </div>

              {/* Bet Amount */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Bet Amount</h3>
                <input
                  type="number"
                  value={betAmount}
                  onChange={(e) => setBetAmount(parseInt(e.target.value) || 0)}
                  min="1"
                  max={userBearBucks}
                  className="w-full px-4 py-3 bg-slate-700 rounded-lg border border-slate-600 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />
                <div className="flex gap-2 mt-2">
                  {[25, 50, 100, 250].map(amount => (
                    <button
                      key={amount}
                      onClick={() => setBetAmount(amount)}
                      disabled={amount > userBearBucks}
                      className="px-3 py-1 bg-slate-600 hover:bg-slate-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded text-sm transition-colors"
                    >
                      {amount}
                    </button>
                  ))}
                  <button
                    onClick={() => setBetAmount(userBearBucks)}
                    className="px-3 py-1 bg-yellow-600 hover:bg-yellow-500 text-white rounded text-sm transition-colors"
                  >
                    All In
                  </button>
                </div>
              </div>

              {/* Bet Summary */}
              <div className="bg-slate-700/50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-3">Bet Summary</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Prediction:</span>
                    <span className="text-white">{getBetDescription()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Wager:</span>
                    <span className="text-white">{betAmount} Bear Bucks</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Potential Payout:</span>
                    <span className="text-green-400 font-semibold">{calculatePayout()} Bear Bucks</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Model Confidence:</span>
                    <span className="text-white">{Math.round((player.confidence || player.stats?.confidence || 0.75) * 100)}%</span>
                  </div>
                </div>
              </div>

              {/* Place Bet Button */}
              <button
                onClick={handlePlaceBet}
                disabled={!selectedOption || !betAmount || betAmount > userBearBucks}
                className="w-full py-4 bg-gradient-to-r from-green-600 to-yellow-500 hover:from-green-700 hover:to-yellow-600 disabled:from-slate-600 disabled:to-slate-600 text-white font-bold rounded-lg transition-all disabled:cursor-not-allowed"
              >
                {betAmount > userBearBucks ? 'Insufficient Bear Bucks' : 'Place Bet'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default PlayerBetting;