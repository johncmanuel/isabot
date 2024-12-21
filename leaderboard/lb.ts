import { LeaderboardEntry, MountStats, Player } from "./types.d.ts";
import { kv, kvKeys, PlayerSchema } from "../lib/kv-oauth.ts";
import { GUILD_NAME } from "../lib/consts.ts";

export class Leaderboard {
  public static async createEntry(): Promise<LeaderboardEntry> {
    const players: { [playerId: string]: Player } = {};
    const mounts: { [playerId: string]: MountStats } = {};
    const entryId = crypto.randomUUID();
    const now = Date.now();
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
      date_added: now,
    };
    console.log("Entry:", entry);

    await kv.set([...kvKeys.leaderboard, entryId], entry);

    return entry;
  }

  public static async getLatestEntry(): Promise<LeaderboardEntry> {
    const iter = kv.list<LeaderboardEntry>({
      prefix: kvKeys.leaderboard,
    }, { reverse: true, limit: 1 });

    for await (const { value } of iter) {
      return value;
    }

    return {} as LeaderboardEntry;
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

  // TODO: Fix table formatting to be mobile friendly
  public static async sendMountLBtoDiscord(
    webhookUrl: string,
    entry: LeaderboardEntry,
    websiteUrl: string, // website where the proj is being hosted
  ) {
    const mountRankings = Object.entries(entry.mounts).map((
      [playerId, stats],
    ) => ({
      playerName: entry.players[playerId].battletag,
      value: stats.number_of_mounts,
    }));

    // Sorted in descending order
    const sortedRankings = mountRankings.sort((a, b) => b.value - a.value);

    const longestNameLength = Math.max(
      ...sortedRankings.map((ranking) => ranking.playerName.length),
    );

    // Create table headers
    let tableContent = "```\n";
    tableContent += `${
      "Battletag".padEnd(longestNameLength)
    } | Number of Mounts\n`;
    tableContent += `${"-".repeat(longestNameLength)}-|-----------------\n`;

    sortedRankings.forEach((ranking) => {
      const name = ranking.playerName.padEnd(longestNameLength);
      const value = ranking.value.toString().padStart(10); // Adjust for alignment

      tableContent += `${name} |${value}\n`;
    });
    tableContent += "```\n";
    tableContent += `Want to join in? Sign up at ${websiteUrl}`;

    const payload = {
      embeds: [{
        title: `🏆 **Mount Collection Leaderboard** for ${
          new Date(entry.date_added).toLocaleDateString()
        }`,
        description: tableContent,
        color: 0x00ff00, // Green color
        footer: {
          text: `Guild: ${GUILD_NAME}`,
        },
      }],
    };

    try {
      const response = await fetch(webhookUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Failed to send to Discord: ${response.statusText}`);
      }

      console.log("Successfully sent leaderboard to Discord");
    } catch (error) {
      console.error("Error sending leaderboard to Discord:", error);
      throw error;
    }
  }
}
