# 🎯 BerkeleyBets Betting System

## Overview
Comprehensive betting system using Bear Bucks as currency, allowing users to wager on player performance predictions across NFL, NBA, and MLB.

## Features

### 💰 **Bear Bucks Token System**
- Users start with 1,500 Bear Bucks
- Visible balance in header
- Used for all betting transactions
- Earnings from successful bets added to balance

### 🎲 **Betting Types**

#### **Over/Under Bets (1.9x Payout)**
- Bet whether a player will score OVER or UNDER a target number
- Example: "Josh Allen will throw OVER 4,500 passing yards"

#### **Exact Prediction Bets (5.0x Payout)**
- High-risk, high-reward exact value predictions
- Example: "Luka Dončić will score exactly 52 fantasy points"

#### **Custom Target Bets (Variable Payout)**
- Set your own target different from model prediction
- Payout multiplier adjusts based on difficulty:
  - Bold predictions (30%+ variance): +1.0x bonus
  - Safe bets (10%+ variance): -0.3x penalty

### 📊 **Available Betting Markets**

#### **NFL Players**
- **Quarterbacks**: Passing yards, Passing TDs, Completions, Rushing yards
- **Running Backs**: Rushing yards, Rushing TDs, Carries, Receiving yards, Receptions
- **WR/TE**: Receiving yards, Receiving TDs, Receptions, Targets
- **All Positions**: Fantasy points

#### **NBA Players**
- Points, Rebounds, Assists, Fantasy points

#### **MLB Players**
- **Batters**: Hits, Runs, RBIs, Fantasy points
- **Pitchers**: Strikeouts, Innings pitched, Fantasy points

### 🎯 **Betting Interface**

#### **PlayerProfile Integration**
- "Place Bet" button on every player profile
- Access to all available betting markets for that player
- Real-time payout calculations

#### **Betting Modal Features**
- Visual bet type selection (Over/Under/Exact)
- Custom target input with prediction reference
- Quick bet amount buttons (25, 50, 100, 250, All In)
- Real-time payout calculation
- Bet summary with model confidence
- Balance validation

#### **Betting Portfolio**
- "My Bets" button in header
- Active bets tracking
- Betting history with win/loss records
- Portfolio statistics:
  - Total wagered
  - Total won
  - Win rate percentage
  - Active bets count

### 🔄 **User Flow**

1. **Browse Players**: Select sport → view player predictions
2. **Player Analysis**: Click player → view detailed stats
3. **Place Bet**: Click "Place Bet" → select market → choose bet type → set amount
4. **Confirmation**: Review bet summary → confirm placement
5. **Track Bets**: Access "My Bets" → monitor active bets → view history

### 💡 **Smart Features**

#### **Dynamic Payout Calculation**
```javascript
// Base multipliers
Over/Under: 1.9x
Exact: 5.0x

// Variance adjustments
Bold prediction (30%+ variance): +1.0x
Safe bet (<10% variance): -0.3x
```

#### **Betting Limits**
- Minimum bet: 1 Bear Buck
- Maximum bet: Current balance
- Real-time balance validation

#### **Model Integration**
- Displays model confidence for each bet
- Uses prediction as default target
- Shows prediction vs custom target variance

### 🎨 **UI/UX Features**

#### **Visual Design**
- Color-coded bet types (Green=Over, Red=Under, Purple=Exact)
- Real-time payout updates
- Balance display throughout interface
- Success animations on bet placement

#### **Responsive Design**
- Mobile-friendly betting modals
- Touch-friendly bet amount selection
- Adaptive grid layouts for portfolio

#### **Error Handling**
- Insufficient funds validation
- Invalid target value checks
- Network error recovery

### 📈 **Portfolio Management**

#### **Active Bets**
- Real-time status tracking
- Cash out early option (future feature)
- Performance monitoring links

#### **Betting History**
- Win/loss records with actual results
- Profitability analysis
- Historical performance trends

#### **Statistics**
- Overall win rate calculation
- Total profit/loss tracking
- Risk assessment metrics

### 🔮 **Future Enhancements**

#### **Advanced Features**
- Live bet monitoring during games
- Push notifications for bet results
- Social betting and leaderboards
- Parlay/combo bets
- Cash out before settlement

#### **Gamification**
- Achievement badges for betting milestones
- Streak bonuses for consecutive wins
- VIP status for high-volume bettors
- Seasonal betting tournaments

## Technical Implementation

### **Components**
- `PlayerBetting.jsx`: Main betting interface
- `BettingPortfolio.jsx`: Portfolio and history management
- `PlayerProfile.jsx`: Integration with betting system

### **Data Flow**
1. Player stats → Betting options generation
2. User selection → Payout calculation
3. Bet placement → Portfolio tracking
4. Result simulation → Balance updates

### **Integration Points**
- Context API for Bear Bucks balance
- Firebase integration (ready for backend)
- Real-time bet tracking system
- Cross-sport compatibility

The betting system transforms BerkeleyBets from a simple prediction viewer into an engaging, gamified sports prediction platform where users can put their money where their predictions are! 🚀