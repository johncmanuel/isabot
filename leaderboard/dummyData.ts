import { LeaderboardEntry } from "./types.d.ts";

export const dummyLeaderboardEntry: LeaderboardEntry = {
  entry_id: "leaderboard_001",
  date_added: Date.now(),
  players: {
    player1: { battletag: "bob", id: "player1" },
    player2: { battletag: "username", id: "player2" },
    player3: { battletag: "arthas", id: "player3" },
    player4: { battletag: "guyman", id: "player4" },
    player5: { battletag: "gojo", id: "player5" },
    player6: { battletag: "rolly", id: "player6" },
    player7: { battletag: "thrall", id: "player7" },
    player8: { battletag: "jaina", id: "player8" },
    player9: { battletag: "illidan", id: "player9" },
    player10: { battletag: "sylvanas", id: "player10" },
    player11: { battletag: "someverylongname", id: "player11" },
    player12: { battletag: "varian", id: "player12" },
  },
  mounts: {
    player1: { number_of_mounts: 606 },
    player2: { number_of_mounts: 597 },
    player3: { number_of_mounts: 41 },
    player4: { number_of_mounts: 410 },
    player5: { number_of_mounts: 31 },
    player6: { number_of_mounts: 3 },
    player7: { number_of_mounts: 320 },
    player8: { number_of_mounts: 315 },
    player9: { number_of_mounts: 300 },
    player10: { number_of_mounts: 285 },
    player11: { number_of_mounts: 275 },
    player12: { number_of_mounts: 260 },
  },
};
