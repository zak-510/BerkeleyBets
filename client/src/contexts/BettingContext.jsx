import React, { createContext, useContext, useState, useEffect } from 'react';
import { Context } from '../index';

const BettingContext = createContext();

export const useBetting = () => {
  const context = useContext(BettingContext);
  if (!context) {
    throw new Error('useBetting must be used within a BettingProvider');
  }
  return context;
};

export const BettingProvider = ({ children }) => {
  const [activeBets, setActiveBets] = useState([]);
  const [bettingHistory, setBettingHistory] = useState([]);
  const ctx = useContext(Context);

  // Load bets from localStorage on mount
  useEffect(() => {
    const savedActiveBets = localStorage.getItem('berkeleyBets_activeBets');
    const savedHistory = localStorage.getItem('berkeleyBets_bettingHistory');
    
    if (savedActiveBets) {
      try {
        setActiveBets(JSON.parse(savedActiveBets));
      } catch (error) {
        console.error('Error loading active bets:', error);
      }
    }
    
    if (savedHistory) {
      try {
        setBettingHistory(JSON.parse(savedHistory));
      } catch (error) {
        console.error('Error loading betting history:', error);
      }
    }
  }, []);

  // Save bets to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('berkeleyBets_activeBets', JSON.stringify(activeBets));
  }, [activeBets]);

  useEffect(() => {
    localStorage.setItem('berkeleyBets_bettingHistory', JSON.stringify(bettingHistory));
  }, [bettingHistory]);

  const placeBet = (bet) => {
    const newBet = {
      ...bet,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      status: 'active'
    };
    
    setActiveBets(prev => [...prev, newBet]);
    
    // Deduct Bear Bucks
    const newBalance = ctx.bearBucks - bet.amount;
    ctx.setBearBucks(newBalance);
    
    return newBet;
  };

  const cashOutBet = (betId) => {
    const bet = activeBets.find(b => b.id === betId);
    if (!bet) return false;

    // Calculate cash out value (typically 70-80% of original bet)
    const cashOutAmount = Math.round(bet.amount * 0.75);
    
    // Remove from active bets
    setActiveBets(prev => prev.filter(b => b.id !== betId));
    
    // Add to history as cashed out
    const cashedOutBet = {
      ...bet,
      status: 'cashed_out',
      actualResult: 'Cashed out early',
      finalPayout: cashOutAmount,
      cashOutTimestamp: new Date().toISOString()
    };
    setBettingHistory(prev => [...prev, cashedOutBet]);
    
    // Return Bear Bucks to user
    const newBalance = ctx.bearBucks + cashOutAmount;
    ctx.setBearBucks(newBalance);
    
    return cashOutAmount;
  };

  const settleBet = (betId, actualResult, won) => {
    const bet = activeBets.find(b => b.id === betId);
    if (!bet) return false;

    // Remove from active bets
    setActiveBets(prev => prev.filter(b => b.id !== betId));
    
    // Add to history
    const settledBet = {
      ...bet,
      status: won ? 'won' : 'lost',
      actualResult: actualResult,
      finalPayout: won ? bet.potentialPayout : 0,
      settledTimestamp: new Date().toISOString()
    };
    setBettingHistory(prev => [...prev, settledBet]);
    
    // Add winnings to Bear Bucks if won
    if (won) {
      const newBalance = ctx.bearBucks + bet.potentialPayout;
      ctx.setBearBucks(newBalance);
    }
    
    return won ? bet.potentialPayout : 0;
  };

  // Simulate bet results for demo purposes
  const simulateBetResult = (betId) => {
    const bet = activeBets.find(b => b.id === betId);
    if (!bet) return;

    // Use model confidence to determine win probability
    const confidence = bet.confidence || 0.75;
    const winProbability = Math.min(confidence + 0.1, 0.95); // Slight boost to model confidence
    
    const won = Math.random() < winProbability;
    
    // Generate realistic actual result based on prediction and target
    let actualResult;
    if (bet.direction === 'over') {
      actualResult = won 
        ? bet.target + Math.random() * (bet.prediction * 0.2)
        : bet.target - Math.random() * (bet.prediction * 0.1);
    } else if (bet.direction === 'under') {
      actualResult = won 
        ? bet.target - Math.random() * (bet.prediction * 0.1)
        : bet.target + Math.random() * (bet.prediction * 0.2);
    } else { // exact
      const variance = bet.prediction * 0.05; // 5% variance for exact bets
      actualResult = bet.prediction + (Math.random() - 0.5) * variance;
      // For exact bets, win if within 2% of target
      const exactWon = Math.abs(actualResult - bet.target) <= (bet.target * 0.02);
      return settleBet(betId, Math.round(actualResult * 10) / 10, exactWon);
    }
    
    settleBet(betId, Math.round(actualResult * 10) / 10, won);
  };

  const getPortfolioStats = () => {
    const allBets = [...activeBets, ...bettingHistory];
    const completedBets = bettingHistory.filter(bet => bet.status !== 'active');
    const wonBets = completedBets.filter(bet => bet.status === 'won');
    
    return {
      totalWagered: allBets.reduce((sum, bet) => sum + bet.amount, 0),
      totalWon: wonBets.reduce((sum, bet) => sum + (bet.finalPayout || 0), 0),
      activeBets: activeBets.length,
      winRate: completedBets.length > 0 ? (wonBets.length / completedBets.length) * 100 : 0,
      totalProfit: wonBets.reduce((sum, bet) => sum + (bet.finalPayout || 0), 0) - allBets.reduce((sum, bet) => sum + bet.amount, 0)
    };
  };

  const value = {
    activeBets,
    bettingHistory,
    placeBet,
    cashOutBet,
    settleBet,
    simulateBetResult,
    getPortfolioStats
  };

  return (
    <BettingContext.Provider value={value}>
      {children}
    </BettingContext.Provider>
  );
};

export default BettingContext;