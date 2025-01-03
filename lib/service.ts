import { BattleNetClient, getClientCredentials } from "./bnet.ts";
import {
  GuildMemberIds,
  kv,
  kvKeys,
  PlayerCharacterKV,
  PlayerSchema,
} from "./kv-oauth.ts";
import { GUILD_REALM, GUILD_SLUG_NAME } from "./consts.ts";

export const savePlayer = async (
  p: PlayerSchema,
  sub: string, // player's ID
): Promise<PlayerSchema> => {
  // see more on secondary keys/indices
  // https://docs.deno.com/deploy/kv/manual/#improve-querying-with-secondary-indexes
  const key = kvKeys.info.concat(sub);
  const res = await kv.atomic().check({ key, versionstamp: null }).set(
    key,
    p,
  ).commit();
  if (res.ok) {
    console.log("Player not yet in the KV, inserting them now.");
  } else {
    console.error("Player already in the KV");
  }
  return p;
};

// Saves player without checks like above
export const savePlayerNoCheck = async (p: PlayerSchema, sub: string) => {
  const key = kvKeys.info.concat(sub);
  const res = await kv.atomic().set(key, p).commit();
  if (res.ok) {
    console.log("Saved player data in KV");
  } else {
    console.error("Couldn't save player in the KV");
  }
};

export const getPlayer = async (sub: string): Promise<PlayerSchema | null> => {
  const key = kvKeys.info.concat(sub);
  const player = await kv.get<PlayerSchema>(key);
  if (player.value === null && player.versionstamp === null) {
    return null;
  }
  return player.value;
};

export const savePlayerGuildCharacters = async (
  client: BattleNetClient,
  sub: string,
) => {
  let playerCharacters: PlayerCharacterKV[] = [];
  const player = await getPlayer(sub);

  if (player === null) {
    console.error("Player not found in KV");
    return playerCharacters;
  }

  const charKey = kvKeys.characters.concat(sub);
  const currentTimeSeconds = Math.floor(Date.now() / 1000);

  if (
    player.updateExpiresAt !== undefined &&
    player.updateExpiresAt > currentTimeSeconds
  ) {
    console.log("Can't update characters yet for", player.battleTag);
    console.log(
      "Expires at:",
      player.updateExpiresAt,
      "current time in seconds:",
      currentTimeSeconds,
      "remaining time (seconds):",
      player.updateExpiresAt - currentTimeSeconds,
    );
    return playerCharacters;
  }
  console.log(
    "Expiration time passed for",
    player.battleTag,
    "updating now...",
  );

  // TODO: Remove current check and instead compare last time the characters was inserted for a specific player since we want players to update
  // their list of characters. For example, when logging in for first time at 16:00, insert new characters. If they try to login again
  // at 16:30, their character list won't be updated. They'll have to wait until 17:00 or 18:00 to update their characters again. This is to
  // prevent abuse of Blizzard's API

  const { access_token } = await getClientCredentials();
  const memberIds = await getGuildData(client, access_token);
  const data = await client.getAccountWoWProfileSummary();
  if (data === null) {
    console.error("Failed to fetch WoW profile summary from API");
    return playerCharacters;
  }

  playerCharacters = data.wow_accounts.flatMap((account) =>
    account.characters.filter((character) =>
      GUILD_REALM.includes(character.realm.slug)
    ).filter((character) => memberIds.has(character.id)).map((
      character,
    ) => ({
      name: character.name,
      id: character.id,
      realm: {
        name: character.realm.name,
        slug: character.realm.slug,
        id: character.realm.id,
      },
    }))
  );

  const res = await kv.atomic()
    .set(charKey, playerCharacters)
    .commit();
  if (res.ok) {
    console.log(
      "inserting characters for",
      player?.battleTag,
      "now...",
    );
  } else {
    console.error("Failed to insert characters in the KV");
  }

  // Update expiration time by adding the current time by 1 hour (3600 seconds)
  // and insert it in the KV
  player.updateExpiresAt = currentTimeSeconds + 3600;
  await savePlayerNoCheck(player, sub);

  return playerCharacters;
};

// Only contains IDs of all the characters in the guild, which are
// used for comparisons with a user's characters. This queries the KV for data;
// if not found, fetch from the API and store in the KV.
export const getGuildData = async (
  client: BattleNetClient,
  clientCredentialsToken: string,
) => {
  const guildKey = [...kvKeys.guild, GUILD_SLUG_NAME];
  const guildKV = await kv.get<GuildMemberIds>(guildKey);

  if (guildKV.value !== null && guildKV.versionstamp !== null) {
    console.log("Found guild data in KV");
    return guildKV.value;
  }

  console.log("Guild not in KV, fetching from API...");
  const guild = await client.getGuildRoster(
    clientCredentialsToken,
    GUILD_REALM,
    GUILD_SLUG_NAME,
  );

  if (guild === null) {
    console.error("Failed to fetch guild data from API, returning empty set");
    return new Set<number>();
  }

  // fun fact: sets can be stored in KV
  // https://docs.deno.com/deploy/kv/manual/key_space/#values
  const guildMemberIds = new Set(
    guild.members.map((member) => member.character.id),
  );

  const res = await kv.atomic().set(guildKey, guildMemberIds).commit();
  if (!res.ok) {
    console.error(
      "Failed to store guild data in KV cache, returning data from API response instead",
    );
  } else {
    console.log("Stored guild data in KV cache");
  }
  return guildMemberIds;
};

export const savePlayersMounts = async (
  client: BattleNetClient,
  sub: string,
) => {
  // Check if player's mounts already exist
  const mountsKey = kvKeys.mounts.concat(sub);
  const mountsKV = await kv.get<{ totalNumMounts: number }>(mountsKey);
  let totalNumMounts = 0;

  if (mountsKV.value !== null && mountsKV.versionstamp !== null) {
    console.log("Found mounts in KV, no need to fetch from API");
    return totalNumMounts;
  }

  const mounts = await client.getAccountMountsCollection();
  if (mounts === null) {
    console.error("Failed to fetch mounts data from API");
  } else {
    totalNumMounts = mounts.mounts.length;
  }

  const res = await kv.atomic()
    .set(mountsKey, { totalNumMounts })
    .commit();
  if (res.ok) {
    console.log("Mounts not yet in the KV, inserting:", {
      totalNumMounts,
    });
  } else {
    console.error("Failed to insert mounts into KV");
  }
  return totalNumMounts;
};
