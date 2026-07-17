import {
  kv,
  kvKeys,
  PlayerCharacterKV,
  PlayerCharactersKV,
} from "./kv-oauth.ts";
import {
  BattleNetClient,
  getClientCredentials,
  updateGuildData,
} from "./bnet.ts";
import { Leaderboard } from "../leaderboard/lb.ts";

// Order of Deno Cron executions
// 1. Update Guild Data
// 2. Update all KV players' data w/ client credentials token
// 3. Create and send new leaderboard entry to Discord webhook

// Runs at 10 AM PST (UTC-8) = 18:00 UTC on Saturdays
Deno.cron("Update Guild Data", { dayOfWeek: { exact: 6 }, hour: { exact: 18 }, minute: { exact: 0 } }, async () => {
  await updateGuildData();
});

// Runs at 5 PM PST (UTC-8) = 00:00 UTC on Sundays
Deno.cron("Update all KV players data", { dayOfWeek: { exact: 0 }, hour: { exact: 0 }, minute: { exact: 0 } }, async () => {
  // Update mounts for all players using client credentials by first
  // iterating through all characters for a particular player and
  // then updating the total number of mounts (for example)
  await updateAllPlayersData();
});

// Runs at 12 PM PST (UTC-8) = 20:00 UTC on Sundays
Deno.cron("Create and send new leaderboard entry", { dayOfWeek: { exact: 0 }, hour: { exact: 20 }, minute: { exact: 0 } }, async () => {
  console.log("Creating new leaderboard entry...");
  const entry = await Leaderboard.createEntry();
  console.log("Created new leaderboard entry, sending to webhook");
  await Leaderboard.sendMountLBtoDiscord(
    Deno.env.get("DISCORD_WEBHOOK_URL") as string,
    entry,
    `${Deno.env.get("BASE_URL")}/signin`,
  );
});

// Get highest number of mounts for a player
export const updateAllPlayersData = async () => {
  console.log("Updating all players data...");
  const { access_token } = await getClientCredentials();
  const client = new BattleNetClient(access_token);
  const charIter = kv.list<PlayerCharactersKV>({ prefix: kvKeys.characters });

  const getHighestNumMounts = async (char: PlayerCharacterKV) => {
    const mounts = await client.getCharacterMounts(
      access_token,
      char.name,
      char.realm.slug,
    );
    if (mounts === null) return 0;
    return mounts.mounts.length;
  };

  const updateMountsInKV = async (playerId: string, totalNumMounts: number) => {
    const mountKey = kvKeys.mounts.concat(playerId);
    const m = await kv.atomic().set(mountKey, { totalNumMounts }).commit();
    if (!m.ok) {
      console.error("Failed to update mounts for player:", playerId);
      return;
    }
    console.log("Updated mounts for playerId:", playerId);
  };

  // Iterate through each player in the KV
  for await (const res of charIter) {
    const playerId = res.key[res.key.length - 1] as string;
    let totalNumMounts = 0;
    for (const char of res.value) {
      // Update mounts
      const numMounts = await getHighestNumMounts(char);
      totalNumMounts = Math.max(totalNumMounts, numMounts);
    }
    await updateMountsInKV(playerId, totalNumMounts);
  }
};
