import { LeaderboardEntry } from "./types.d.ts";
import { kv, kvKeys } from "../lib/kv-oauth.ts";
import { PlayerSchema } from "../lib/kv-oauth.ts";

export class Leaderboard {
  // public static async getLeaderboard(): Promise<LeaderboardEntry[]> {
  // }

  public static async createEntry(): Promise<void> {
    const iter = kv.list<PlayerSchema>({ prefix: kvKeys.info });
    for await (const { key, value } of iter) {
      const player = value as PlayerSchema;
      const id = key[key.length - 1];
      const c = kvKeys.characters;
      const m = kvKeys.mounts;
      c.push(id as string);
      m.push(id as string);
      // @ts-ignore: ignore typing error with key
      const characters = await kv.get(c);
      // @ts-ignore: ignore typing error with key
      const mounts = await kv.get(m);
      console.log(player, characters, mounts);
    }
  }
}
