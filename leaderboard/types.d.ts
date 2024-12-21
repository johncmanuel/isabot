interface Player {
  battletag: string;
  id: string;
}

interface MountStats {
  number_of_mounts: number;
}

// interface BattlegroundStats {
//   bg_wins: number;
// }

export interface LeaderboardEntry {
  entry_id: string;
  players: {
    [playerId: string]: Player;
  };
  date_added: number;
  mounts: {
    [player_id: string]: MountStats;
  };
  // normal_bg_wins: {
  //   [playerId: string]: BattlegroundStats;
  // };
}
