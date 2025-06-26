import { useState, useMemo, useEffect, useContext } from "react";
import Fuse from "fuse.js";
import nflService from "../services/nflService";
import nbaService from "../services/nbaService";
import mlbService from "../services/mlbService";
import { getFirestore, doc, getDoc, setDoc } from "firebase/firestore";
import { Context } from "..";
import { useNavigate } from "react-router";
import nbaLogo from "../assets/nba.png";
import ncaaLogo from "../assets/ncaa.png";
import nflLogo from "../assets/nfl.webp";
import mlbLogo from "../assets/mlb.png";
import PlayerProfile from "../components/PlayerProfile";
import BettingPortfolio from "../components/BettingPortfolio";

const Dashboard = () => {
  const [selectedSport, setSelectedSport] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [nflPlayers, setNflPlayers] = useState([]);
  const [nbaPlayers, setNbaPlayers] = useState([]);
  const [mlbPlayers, setMlbPlayers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nflApiHealthy, setNflApiHealthy] = useState(false);
  const [nbaApiHealthy, setNbaApiHealthy] = useState(false);
  const [mlbApiHealthy, setMlbApiHealthy] = useState(false);
  const [activeBets, setActiveBets] = useState(0);
  const [wins, setWins] = useState(0);
  const [losses, setLosses] = useState(0);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [showPlayerProfile, setShowPlayerProfile] = useState(false);
  const [showBettingPortfolio, setShowBettingPortfolio] = useState(false);

  const ctx = useContext(Context);
  const navigate = useNavigate();

  const sports = [
    { id: "nfl", name: "NFL", icon: nflLogo },
    { id: "nba", name: "NBA", icon: nbaLogo },
    { id: "mlb", name: "MLB", icon: mlbLogo },
  ];

  // Load user data from Firebase
  useEffect(() => {
    if (ctx.user) {
      const docRef = doc(ctx.db, "Users", ctx.user.uid);

      getDoc(docRef).then(async (docSnap) => {
        console.log(docSnap);
        if (docSnap.exists()) {
          console.log("Document data:", docSnap.data());
          const data = docSnap.data();
          setActiveBets(data.activeBets || 0);
          setWins(data.wins || 0);
          setLosses(data.losses || 0);
          // Only set Bear Bucks if we don't already have a value (to avoid overriding betting changes)
          if (ctx.bearBucks === 1500) {
            ctx.setBearBucks(data.bearBucks || 1500);
          }
        } else {
          // Create new user document with default values
          console.log("Creating new user document...");
          try {
            await setDoc(docRef, {
              bearBucks: 1500,
              activeBets: 0,
              wins: 0,
              losses: 0
            });
            setActiveBets(0);
            setWins(0);
            setLosses(0);
            ctx.setBearBucks(1500);
            console.log("User document created successfully");
          } catch (error) {
            console.error("Error creating user document:", error);
          }
        }
      }).catch((error) => {
        console.error("Error loading user data:", error);
      });
    }
  }, [ctx.user]); // Only run when user changes

  // Check API health on component mount and periodically
  useEffect(() => {
    if (!ctx.user) navigate("/log-in");

    const checkApiHealth = async () => {
      // Check NFL API
      try {
        await nflService.healthCheck();
        setNflApiHealthy(true);
      } catch (error) {
        console.error("NFL API health check failed:", error);
        setNflApiHealthy(false);
      }

      // Check NBA API
      try {
        await nbaService.healthCheck();
        setNbaApiHealthy(true);
      } catch (error) {
        console.error("NBA API health check failed:", error);
        setNbaApiHealthy(false);
      }

      // Check MLB API
      try {
        await mlbService.healthCheck();
        setMlbApiHealthy(true);
      } catch (error) {
        console.error("MLB API health check failed:", error);
        setMlbApiHealthy(false);
      }
    };

    // Initial health check
    checkApiHealth();
    
    // Periodic health check every 30 seconds
    const healthCheckInterval = setInterval(checkApiHealth, 30000);
    
    // Cleanup interval on unmount
    return () => clearInterval(healthCheckInterval);
  }, []);

  // Load players when sport is selected
  useEffect(() => {
    if (selectedSport === "nfl" && nflApiHealthy) {
      loadNFLPlayers();
    } else if (selectedSport === "nba" && nbaApiHealthy) {
      loadNBAPlayers();
    } else if (selectedSport === "mlb" && mlbApiHealthy) {
      loadMLBPlayers();
    }
  }, [selectedSport, nflApiHealthy, nbaApiHealthy, mlbApiHealthy]);

  const loadNFLPlayers = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await nflService.fetchTopPlayers("ALL", 50);
      const formattedPlayers = response.players.map((player) =>
        nflService.formatPlayerForUI(player)
      );
      setNflPlayers(formattedPlayers);
      // If successful, mark API as healthy
      setNflApiHealthy(true);
    } catch (err) {
      setError(
        "Failed to load NFL players. Make sure the API server is running."
      );
      console.error("Error loading NFL players:", err);
      // If failed, mark API as unhealthy
      setNflApiHealthy(false);
    } finally {
      setLoading(false);
    }
  };

  const loadNBAPlayers = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await nbaService.fetchTopPlayers("ALL", 50);
      const formattedPlayers = response.players.map((player) =>
        nbaService.formatPlayerForUI(player)
      );
      setNbaPlayers(formattedPlayers);
      // If successful, mark API as healthy
      setNbaApiHealthy(true);
    } catch (err) {
      setError(
        "Failed to load NBA players. Make sure the API server is running."
      );
      console.error("Error loading NBA players:", err);
      // If failed, mark API as unhealthy
      setNbaApiHealthy(false);
    } finally {
      setLoading(false);
    }
  };

  const loadMLBPlayers = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await mlbService.fetchTopPlayers("ALL", 50);
      const formattedPlayers = response.players.map((player) =>
        mlbService.formatPlayerForUI(player)
      );
      setMlbPlayers(formattedPlayers);
      // If successful, mark API as healthy
      setMlbApiHealthy(true);
    } catch (err) {
      setError(
        "Failed to load MLB players. Make sure the API server is running."
      );
      console.error("Error loading MLB players:", err);
      // If failed, mark API as unhealthy
      setMlbApiHealthy(false);
    } finally {
      setLoading(false);
    }
  };

  // Handle search for NFL players
  const handleNFLSearch = async (query) => {
    if (!query.trim()) {
      loadNFLPlayers(); // Reset to all players
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await nflService.searchPlayers(query);
      const formattedPlayers = response.players.map((player) =>
        nflService.formatPlayerForUI(player)
      );
      setNflPlayers(formattedPlayers);
      // If successful, mark API as healthy
      setNflApiHealthy(true);
    } catch (err) {
      setError("Failed to search players.");
      console.error("Error searching NFL players:", err);
      // If failed, mark API as unhealthy
      setNflApiHealthy(false);
    } finally {
      setLoading(false);
    }
  };

  // Handle search for NBA players
  const handleNBASearch = async (query) => {
    if (!query.trim()) {
      loadNBAPlayers(); // Reset to all players
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await nbaService.searchPlayers(query);
      const formattedPlayers = response.players.map((player) =>
        nbaService.formatPlayerForUI(player)
      );
      setNbaPlayers(formattedPlayers);
      // If successful, mark API as healthy
      setNbaApiHealthy(true);
    } catch (err) {
      setError("Failed to search players.");
      console.error("Error searching NBA players:", err);
      // If failed, mark API as unhealthy
      setNbaApiHealthy(false);
    } finally {
      setLoading(false);
    }
  };

  // Handle search for MLB players
  const handleMLBSearch = async (query) => {
    if (!query.trim()) {
      loadMLBPlayers(); // Reset to all players
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await mlbService.searchPlayers(query);
      const formattedPlayers = response.players.map((player) =>
        mlbService.formatPlayerForUI(player)
      );
      setMlbPlayers(formattedPlayers);
      // If successful, mark API as healthy
      setMlbApiHealthy(true);
    } catch (err) {
      setError("Failed to search players.");
      console.error("Error searching MLB players:", err);
      // If failed, mark API as unhealthy
      setMlbApiHealthy(false);
    } finally {
      setLoading(false);
    }
  };

  // Sample player data for other sports
  const players = {
    // No sample MLB data since we're using the API
  };

  const teams = [
    {
      id: "cal",
      name: "Berkeley Bears",
      logo: "🐻",
      color: "text-yellow-400",
      sport: "ncaa",
    },
    {
      id: "ucla",
      name: "UCLA Bruins",
      logo: "🐻",
      color: "text-blue-400",
      sport: "ncaa",
    },
  ];

  // Fuzzy search configuration for non-NFL sports
  const fuseOptions = {
    keys: ["name", "team", "position"],
    threshold: 0.4,
    distance: 100,
    includeScore: true,
    minMatchCharLength: 2,
  };

  // Create fuzzy search instance for non-API sports
  const fuse = useMemo(() => {
    if (
      selectedSport &&
      selectedSport !== "nfl" &&
      selectedSport !== "nba" &&
      selectedSport !== "mlb" &&
      players[selectedSport]
    ) {
      return new Fuse(players[selectedSport], fuseOptions);
    }
    return null;
  }, [selectedSport, players]);

  // Filter players based on search
  const filteredPlayers = useMemo(() => {
    if (!selectedSport || selectedSport === "ncaa") return [];

    if (selectedSport === "nfl") {
      return nflPlayers; // NFL players are already filtered by the API
    }

    if (selectedSport === "nba") {
      return nbaPlayers; // NBA players are already filtered by the API
    }

    if (selectedSport === "mlb") {
      return mlbPlayers; // MLB players are already filtered by the API
    }

    const currentPlayers = players[selectedSport] || [];

    if (!searchTerm.trim()) {
      return currentPlayers;
    }

    if (fuse) {
      const results = fuse.search(searchTerm);
      return results.map((result) => result.item);
    }

    return currentPlayers;
  }, [selectedSport, searchTerm, fuse, players, nflPlayers, nbaPlayers, mlbPlayers]);

  // Debounce search for API-based sports
  useEffect(() => {
    if (selectedSport === "nfl" && searchTerm !== "") {
      const timeoutId = setTimeout(() => {
        handleNFLSearch(searchTerm);
      }, 500);

      return () => clearTimeout(timeoutId);
    } else if (selectedSport === "nfl" && searchTerm === "") {
      loadNFLPlayers();
    } else if (selectedSport === "nba" && searchTerm !== "") {
      const timeoutId = setTimeout(() => {
        handleNBASearch(searchTerm);
      }, 500);

      return () => clearTimeout(timeoutId);
    } else if (selectedSport === "nba" && searchTerm === "") {
      loadNBAPlayers();
    } else if (selectedSport === "mlb" && searchTerm !== "") {
      const timeoutId = setTimeout(() => {
        handleMLBSearch(searchTerm);
      }, 500);

      return () => clearTimeout(timeoutId);
    } else if (selectedSport === "mlb" && searchTerm === "") {
      loadMLBPlayers();
    }
  }, [searchTerm, selectedSport]);

  // Handle search input change
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
  };

  // Filter teams based on selected sport
  const getFilteredTeams = () => {
    if (selectedSport === "ncaa") {
      return teams.filter((team) => team.id === "cal");
    } else if (selectedSport) {
      return teams;
    }
    return [];
  };

  const filteredTeams = getFilteredTeams();

  // Handle player card click
  const handlePlayerClick = (player) => {
    setSelectedPlayer(player);
    setShowPlayerProfile(true);
  };

  // Handle closing player profile
  const handleClosePlayerProfile = () => {
    setSelectedPlayer(null);
    setShowPlayerProfile(false);
  };

  const renderPlayerCard = (player) => {
    const getStatDisplay = () => {
      switch (selectedSport) {
        case "nfl":
          return (
            <div className="grid grid-cols-1 gap-2 text-xs">
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">
                  Predicted Fantasy Points 2025 Season
                </div>
                <div className="text-white font-semibold">
                  {player.stats.predictedPoints?.toFixed(1)}
                </div>
              </div>
            </div>
          );
        case "nba":
          return (
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">Projected Points</div>
                <div className="text-white font-semibold">
                  {player.stats.predictedPoints?.toFixed(1)}
                </div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">Projected Rebounds</div>
                <div className="text-white font-semibold">
                  {player.stats.predictedRebounds?.toFixed(1)}
                </div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">Projected Assists</div>
                <div className="text-white font-semibold">
                  {player.stats.predictedAssists?.toFixed(1)}
                </div>
              </div>
            </div>
          );

        case "mlb":
          return (
            <div className="grid grid-cols-1 gap-2 text-xs">
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">
                  Predicted Fantasy Points 2025 Season
                </div>
                <div className="text-white font-semibold">
                  {player.stats.predictedFantasyPoints?.toFixed(1)}
                </div>
              </div>
              {player.stats.displayStats && (
                <div className="grid grid-cols-3 gap-2">
                  {player.stats.displayStats.map((stat, index) => (
                    <div key={index} className="bg-slate-700/50 rounded p-2">
                      <div className="text-slate-400">{stat.label}</div>
                      <div className="text-white font-semibold">
                        {typeof stat.value === 'number' ? stat.value.toFixed(stat.label.includes('Average') ? 3 : 0) : stat.value}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        default:
          return null;
      }
    };

    return (
      <div
        key={player.id}
        onClick={() => handlePlayerClick(player)}
        className="bg-slate-700/30 rounded-xl border border-slate-600/50 hover:border-slate-500/70 transition-all cursor-pointer group p-4 hover:bg-slate-700/50"
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
              {selectedSport !== "nfl" && selectedSport !== "nba" && (
                <p className="text-slate-400 text-sm">{player.team}</p>
              )}
              <p className="text-yellow-400 text-xs font-medium">
                {player.position}
              </p>
            </div>
          </div>
          <div className="text-slate-400 group-hover:text-white transition-colors">
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
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
      <div
        className="absolute inset-0"
        style={{
          backgroundImage:
            "radial-gradient(circle, rgba(255, 215, 0, 0.05) 1px, transparent 1px)",
          backgroundSize: "30px 30px",
        }}
      ></div>

      <div className="relative z-10 p-6">
        {/* My Bets Button */}
        <div className="flex justify-end mb-6">
          <button
            onClick={() => setShowBettingPortfolio(true)}
            className="px-4 py-2 bg-gradient-to-r from-green-600 to-yellow-500 text-white rounded-lg font-medium hover:from-green-700 hover:to-yellow-600 transition-all flex items-center gap-2"
          >
            <span>📊</span>
            My Bets
          </button>
        </div>

        {/* API Status Indicator */}
        {(selectedSport === "nfl" || selectedSport === "nba" || selectedSport === "mlb") && (
          <div className="flex justify-center mb-4">
            <div
              className={`px-3 py-1 rounded-full text-xs font-medium ${
                (selectedSport === "nfl" ? nflApiHealthy : 
                 selectedSport === "nba" ? nbaApiHealthy : 
                 selectedSport === "mlb" ? mlbApiHealthy : false)
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "bg-red-500/20 text-red-400 border border-red-500/30"
              }`}
            >
              {selectedSport === "nfl"
                ? nflApiHealthy
                  ? "🟢 NFL API Connected"
                  : "🔴 NFL API Disconnected"
                : selectedSport === "nba"
                ? nbaApiHealthy
                  ? "🟢 NBA API Connected"
                  : "🔴 NBA API Disconnected"
                : selectedSport === "mlb"
                ? mlbApiHealthy
                  ? "🟢 MLB API Connected"
                  : "🔴 MLB API Disconnected"
                : "🔴 API Disconnected"}
            </div>
          </div>
        )}

        {/* Sports Selection */}
        <div className="mb-8">
          <div className="flex justify-center space-x-8">
            {sports.map((sport) => (
              <button
                key={sport.id}
                onClick={() => {
                  setSelectedSport(sport.id);
                  setSearchTerm("");
                  setError(null);
                }}
                className={`w-20 h-20 rounded-xl border-2 flex items-center justify-center transition-all hover:scale-105 ${
                  selectedSport === sport.id
                    ? "border-yellow-400 bg-yellow-400/20"
                    : "border-slate-600 bg-slate-800/50 hover:border-slate-500"
                }`}
              >
                <div className="flex flex-col gap-2">
                  <img className="w-10 h-10 object-contain" src={sport.icon} />
                  <div className="text-xs text-slate-300 font-medium">
                    {sport.name}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Search Bar - Only show for non-NCAA sports */}
        {selectedSport && selectedSport !== "ncaa" && (
          <div className="max-w-4xl mx-auto mb-6">
            <div className="relative">
              <input
                type="text"
                placeholder={`Search ${selectedSport.toUpperCase()} players...`}
                value={searchTerm}
                onChange={handleSearchChange}
                className="w-full px-4 py-3 pl-12 bg-slate-800/30 backdrop-blur-lg rounded-xl border border-slate-700/50 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-all"
              />
              <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400">
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
              {searchTerm && (
                <button
                  onClick={() => {
                    setSearchTerm("");
                    if (selectedSport === "nfl") {
                      loadNFLPlayers();
                    } else if (selectedSport === "nba") {
                      loadNBAPlayers();
                    } else if (selectedSport === "mlb") {
                      loadMLBPlayers();
                    }
                  }}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              )}
            </div>

            {/* Search Results Count */}
            {searchTerm && (
              <div className="mt-2 text-sm text-slate-400 text-center">
                {filteredPlayers.length} player
                {filteredPlayers.length !== 1 ? "s" : ""} found
                {filteredPlayers.length === 0 && searchTerm.length > 2 && (
                  <span className="text-yellow-400">
                    {" "}
                    - try a different spelling
                  </span>
                )}
              </div>
            )}
          </div>
        )}

        {/* Content Section */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-slate-800/30 backdrop-blur-lg rounded-2xl border border-slate-700/50 p-6">
            {selectedSport ? (
              // Players Section
              <>
                {error && (
                  <div className="mb-4 p-4 bg-red-500/20 border border-red-500/30 rounded-xl">
                    <p className="text-red-400 text-center">{error}</p>
                    {(selectedSport === "nfl" ||
                      selectedSport === "nba" ||
                      selectedSport === "mlb") && (
                      <button
                        onClick={
                          selectedSport === "nfl"
                            ? loadNFLPlayers
                            : selectedSport === "nba"
                            ? loadNBAPlayers
                            : loadMLBPlayers
                        }
                        className="mt-2 mx-auto block px-4 py-2 bg-red-500/30 hover:bg-red-500/50 rounded-lg text-red-300 transition-colors"
                      >
                        Retry
                      </button>
                    )}
                  </div>
                )}

                <div className="space-y-4">
                      {loading ? (
                        <div className="text-center py-8">
                          <div className="animate-spin w-8 h-8 border-4 border-yellow-400 border-t-transparent rounded-full mx-auto mb-4"></div>
                          <p className="text-slate-300 text-lg">
                            Loading players...
                          </p>
                        </div>
                      ) : filteredPlayers.length > 0 ? (
                        filteredPlayers.map(renderPlayerCard)
                      ) : searchTerm ? (
                        <div className="text-center py-8">
                          <p className="text-slate-300 text-lg">
                            No players found for "{searchTerm}"
                          </p>
                          <p className="text-slate-400 text-sm mt-2">
                            Try checking the spelling or search for a different
                            player
                          </p>
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <p className="text-slate-300 text-lg">
                            {selectedSport === "nfl" && !nflApiHealthy
                              ? "NFL API is not available. Please start the API server."
                              : selectedSport === "nba" && !nbaApiHealthy
                              ? "NBA API is not available. Please start the API server."
                              : selectedSport === "mlb" && !mlbApiHealthy
                              ? "MLB API is not available. Please start the API server."
                              : "Select a sport to view available players"}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Load More Players Button */}
                    {filteredPlayers.length > 0 &&
                      (selectedSport === "nfl" || selectedSport === "nba" || selectedSport === "mlb") && (
                        <div className="mt-6 text-center">
                          <button
                            onClick={
                              selectedSport === "nfl"
                                ? loadNFLPlayers
                                : selectedSport === "nba"
                                ? loadNBAPlayers
                                : loadMLBPlayers
                            }
                            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-yellow-500 text-white rounded-lg font-medium hover:from-blue-700 hover:to-yellow-600 transition-all"
                          >
                            🔄 Refresh Players
                          </button>
                        </div>
                      )}
                  </>
            ) : (
              <div className="text-center py-8">
                <p className="text-slate-300 text-lg">
                  Select a sport to view available teams/players
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats - Only show if user has actual betting activity */}
        {activeBets > 0 && (
          <div className="max-w-4xl mx-auto mt-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-slate-800/30 backdrop-blur-lg rounded-xl border border-slate-700/50 p-4 text-center">
                <div className="text-2xl font-bold text-green-400">
                  {activeBets}
                </div>
                <div className="text-slate-300 text-sm">Active Bets</div>
              </div>
              <div className="bg-slate-800/30 backdrop-blur-lg rounded-xl border border-slate-700/50 p-4 text-center">
                <div className="text-2xl font-bold text-blue-400">
                  {wins + losses < 1 ? 0 : Math.round((100 * wins) / (wins + losses))}%
                </div>
                <div className="text-slate-300 text-sm">Win Rate</div>
              </div>
              <div className="bg-slate-800/30 backdrop-blur-lg rounded-xl border border-slate-700/50 p-4 text-center">
                <div className="text-2xl font-bold text-yellow-400">
                  {wins}/{wins + losses}
                </div>
                <div className="text-slate-300 text-sm">Record</div>
              </div>
            </div>
          </div>
        )}

        {/* Player Profile Modal */}
        {showPlayerProfile && selectedPlayer && (
          <PlayerProfile
            player={selectedPlayer}
            sport={selectedSport}
            onClose={handleClosePlayerProfile}
          />
        )}

        {/* Betting Portfolio Modal */}
        {showBettingPortfolio && (
          <BettingPortfolio
            isOpen={showBettingPortfolio}
            onClose={() => setShowBettingPortfolio(false)}
          />
        )}
      </div>
    </div>
  );
};

export default Dashboard;
