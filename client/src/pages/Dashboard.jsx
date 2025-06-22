import { useState, useMemo, useEffect, useContext } from "react";
import Fuse from "fuse.js";
import nflService from "../services/nflService";
import nbaService from "../services/nbaService";
import { getFirestore, doc, getDoc } from "firebase/firestore";
import { Context } from "..";

const Dashboard = () => {
  const [bearBucks, setBearBucks] = useState(1500);
  const [selectedSport, setSelectedSport] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [nflPlayers, setNflPlayers] = useState([]);
  const [nbaPlayers, setNbaPlayers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nflApiHealthy, setNflApiHealthy] = useState(false);
  const [nbaApiHealthy, setNbaApiHealthy] = useState(false);
  const [activeBets, setActiveBets] = useState(12);
  const [wins, setWins] = useState(7);
  const [losses, setLosses] = useState(3);

  const ctx = useContext(Context);

  const sports = [
    { id: "nfl", name: "NFL", icon: "🏈" },
    { id: "nba", name: "NBA", icon: "🏀" },
    { id: "ncaa", name: "NCAA", icon: "🏀" },
    { id: "mlb", name: "MLB", icon: "⚾" },
  ];

  if (ctx.user) {
    const docRef = doc(ctx.db, "Users", ctx.user.uid);

    getDoc(docRef).then((docSnap) => {
      console.log(docSnap);
      if (docSnap.exists()) {
        console.log("Document data:", docSnap.data());
        const data = docSnap.data();
        setActiveBets(data.activeBets);
        setWins(data.wins);
        setLosses(data.losses);
        ctx.setBearBucks(data.bearBucks);
      } else {
        // docSnap.data() will be undefined in this case
        console.log("No such document!");
      }
    });
  }

  // Check API health on component mount
  useEffect(() => {
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
    };

    checkApiHealth();
  }, []);

  // Load players when sport is selected
  useEffect(() => {
    if (selectedSport === "nfl" && nflApiHealthy) {
      loadNFLPlayers();
    } else if (selectedSport === "nba" && nbaApiHealthy) {
      loadNBAPlayers();
    }
  }, [selectedSport, nflApiHealthy, nbaApiHealthy]);

  const loadNFLPlayers = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await nflService.fetchTopPlayers("ALL", 50);
      const formattedPlayers = response.players.map((player) =>
        nflService.formatPlayerForUI(player)
      );
      setNflPlayers(formattedPlayers);
    } catch (err) {
      setError(
        "Failed to load NFL players. Make sure the API server is running."
      );
      console.error("Error loading NFL players:", err);
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
    } catch (err) {
      setError(
        "Failed to load NBA players. Make sure the API server is running."
      );
      console.error("Error loading NBA players:", err);
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
    } catch (err) {
      setError("Failed to search players.");
      console.error("Error searching NFL players:", err);
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
    } catch (err) {
      setError("Failed to search players.");
      console.error("Error searching NBA players:", err);
    } finally {
      setLoading(false);
    }
  };

  // Sample player data for other sports
  const players = {
    mlb: [
      {
        id: "ohtani",
        name: "Shohei Ohtani",
        team: "Los Angeles Dodgers",
        position: "DH/SP",
        stats: {
          battingAvg: 0.304,
          homeRuns: 44,
          rbi: 95,
          era: 3.14,
        },
        image: "⚾",
      },
      {
        id: "judge",
        name: "Aaron Judge",
        team: "New York Yankees",
        position: "RF",
        stats: {
          battingAvg: 0.267,
          homeRuns: 37,
          rbi: 75,
          onBasePercentage: 0.406,
        },
        image: "⚾",
      },
    ],
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

    const currentPlayers = players[selectedSport] || [];

    if (!searchTerm.trim()) {
      return currentPlayers;
    }

    if (fuse) {
      const results = fuse.search(searchTerm);
      return results.map((result) => result.item);
    }

    return currentPlayers;
  }, [selectedSport, searchTerm, fuse, players, nflPlayers, nbaPlayers]);

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
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">AVG</div>
                <div className="text-white font-semibold">
                  {player.stats.battingAvg}
                </div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">HR</div>
                <div className="text-white font-semibold">
                  {player.stats.homeRuns}
                </div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">RBI</div>
                <div className="text-white font-semibold">
                  {player.stats.rbi}
                </div>
              </div>
              <div className="bg-slate-700/50 rounded p-2">
                <div className="text-slate-400">
                  {player.stats.era ? "ERA" : "OBP"}
                </div>
                <div className="text-white font-semibold">
                  {player.stats.era || player.stats.onBasePercentage}
                </div>
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
        {/* API Status Indicator */}
        {(selectedSport === "nfl" || selectedSport === "nba") && (
          <div className="flex justify-center mb-4">
            <div
              className={`px-3 py-1 rounded-full text-xs font-medium ${
                (selectedSport === "nfl" ? nflApiHealthy : nbaApiHealthy)
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "bg-red-500/20 text-red-400 border border-red-500/30"
              }`}
            >
              {selectedSport === "nfl"
                ? nflApiHealthy
                  ? "🟢 NFL API Connected"
                  : "🔴 NFL API Disconnected"
                : nbaApiHealthy
                ? "🟢 NBA API Connected"
                : "🔴 NBA API Disconnected"}
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
                <div className="text-center">
                  <div className="text-2xl mb-1">{sport.icon}</div>
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
              <>
                {selectedSport === "ncaa" ? (
                  // NCAA Teams Section
                  <>
                    <div className="space-y-4">
                      {filteredTeams.map((team) => (
                        <div
                          key={team.id}
                          className="flex items-center p-4 bg-slate-700/30 rounded-xl border border-slate-600/50 hover:border-slate-500/70 transition-all cursor-pointer group"
                        >
                          <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-yellow-500 rounded-lg flex items-center justify-center mr-4">
                            <span className="text-xl">{team.logo}</span>
                          </div>
                          <div className="flex-1">
                            <h3
                              className={`text-xl font-semibold ${team.color} group-hover:text-white transition-colors`}
                            >
                              {team.name}
                            </h3>
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
                      ))}
                    </div>
                  </>
                ) : (
                  // Players Section
                  <>
                    {error && (
                      <div className="mb-4 p-4 bg-red-500/20 border border-red-500/30 rounded-xl">
                        <p className="text-red-400 text-center">{error}</p>
                        {(selectedSport === "nfl" ||
                          selectedSport === "nba") && (
                          <button
                            onClick={
                              selectedSport === "nfl"
                                ? loadNFLPlayers
                                : loadNBAPlayers
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
                              : "Select a sport to view available players"}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Load More Players Button */}
                    {filteredPlayers.length > 0 &&
                      (selectedSport === "nfl" || selectedSport === "nba") && (
                        <div className="mt-6 text-center">
                          <button
                            onClick={
                              selectedSport === "nfl"
                                ? loadNFLPlayers
                                : loadNBAPlayers
                            }
                            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-yellow-500 text-white rounded-lg font-medium hover:from-blue-700 hover:to-yellow-600 transition-all"
                          >
                            🔄 Refresh Players
                          </button>
                        </div>
                      )}
                  </>
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

        {/* Quick Stats */}
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
                {wins + losses < 1 ? 0 : (100 * wins) / (wins + losses)}%
              </div>
              <div className="text-slate-300 text-sm">Win Rate</div>
            </div>
            {/* <div className="bg-slate-800/30 backdrop-blur-lg rounded-xl border border-slate-700/50 p-4 text-center">
              <div className="text-2xl font-bold text-yellow-400">+$342</div>
              <div className="text-slate-300 text-sm">This Week</div>
            </div> */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
