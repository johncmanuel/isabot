import { LeaderboardEntry, MountStats, Player } from "./types.d.ts";
import { kv, kvKeys, PlayerSchema } from "../lib/kv-oauth.ts";

export class Leaderboard {
  public static async createEntry(): Promise<void> {
    const players: { [playerId: string]: Player } = {};
    const mounts: { [playerId: string]: MountStats } = {};
    const entryId = crypto.randomUUID();
    const iter = kv.list<PlayerSchema>({ prefix: kvKeys.info });

    for await (const { key, value } of iter) {
      const player = value as PlayerSchema;
      const id = key[key.length - 1] as string;

      players[id] = {
        battletag: player.battleTag,
        id,
      };

      const mountsKey = [...kvKeys.mounts, id];
      // @ts-ignore: ignore typing error with key
      const mountsData = await kv.get(mountsKey);

      if (mountsData.versionstamp !== null && mountsData.value !== null) {
        mounts[id] = {
          // @ts-ignore: ignore typing error for now lol
          number_of_mounts: mountsData.value?.totalNumMounts || 0,
        };
      } else {
        // Default to 0 if no mounts data found
        mounts[id] = {
          number_of_mounts: 0,
        };
      }
    }

    const entry: LeaderboardEntry = {
      entry_id: entryId,
      players,
      mounts,
      date_added: Date.now(),
    };
    console.log("Entry:", entry);

    await kv.set([...kvKeys.leaderboard, entryId], entry);
  }

  public static async getLatestEntry(): Promise<LeaderboardEntry | null> {
    const iter = kv.list<LeaderboardEntry>({
      prefix: kvKeys.leaderboard,
    }, { reverse: true, limit: 1 });

    for await (const { value } of iter) {
      return value;
    }

    return null;
  }

  // Gets all(!) entries in the leaderboard
  public static async getEntries(): Promise<LeaderboardEntry[]> {
    const entries: LeaderboardEntry[] = [];
    const iter = kv.list<LeaderboardEntry>({
      prefix: kvKeys.leaderboard,
    });
    for await (const { value } of iter) {
      entries.push(value);
    }
    return entries;
  }
}
