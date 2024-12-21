import {
  createOAuthHelpers,
  kv,
  kvKeys,
  PlayerSchema,
} from "./lib/kv-oauth.ts";
import { BattleNetClient, getClientCredentials } from "./lib/bnet.ts";
import { getExpirationDate } from "./lib/utils.ts";
import { GUILD_NAME, GUILD_REALM } from "./lib/consts.ts";
import { Leaderboard } from "./leaderboard/lb.ts";

// TODO: Update KV database weekly to remove inactive players and update active players in the guild using a Deno Cron
Deno.cron("Update Guild Data", "0 18 * * SUN", async () => {
  await updateGuildData();
});
export const updateGuildData = async () => {
  console.log("Starting weekly guild data update...");

  const { access_token } = await getClientCredentials();
  if (!access_token) {
    throw new Error("Failed to get access token");
  }

  // Create client and fetch new guild data
  const client = new BattleNetClient(access_token);
  if (!client) {
    throw new Error("Failed to create BattleNet client");
  }
  const newGuildData = await client.getGuildRoster(
    access_token,
    GUILD_REALM,
    GUILD_NAME,
  );
  if (!newGuildData) {
    throw new Error("Failed to get new guild data");
  }

  const newGuildMemberIds = new Set(
    newGuildData.members.map((member) => member.character.id),
  );

  // Ensure to overwrite the old guild data in KV with new data
  const kvGuildKey = [...kvKeys.guild, GUILD_NAME];
  const res = await kv.atomic().set(kvGuildKey, newGuildMemberIds).commit();
  if (!res.ok) {
    throw new Error("Failed to update guild data in KV");
  }
  console.log("Updated guild data in KV");
};

const handler = async (req: Request) => {
  const { pathname } = new URL(req.url);
  const { handleCallback, getSessionId, signIn, signOut } = createOAuthHelpers(
    req,
  );

  switch (pathname) {
    case "/": {
      const sessionId = await getSessionId(req);
      if (sessionId) {
        console.log("Session ID:", sessionId);
        return new Response(`hi welcome to isabot 2.0, ${sessionId}`);
      }
      return new Response("hi welcome to isabot 2.0");
    }
    case "/signin":
      return await signIn(req);
    case "/signout":
      return await signOut(req);
    case "/callback": {
      const { response, tokens } = await handleCallback(req);
      const { expiresIn, accessToken } = tokens;

      if (!accessToken) {
        console.error("No access token found");
        return response;
      }
      // console.log("Access token:", accessToken, "expires in:", expiresIn);

      const expiresInDate = Math.floor(getExpirationDate(expiresIn));

      const client = new BattleNetClient(accessToken);

      // insert user into KV
      const { sub, battletag } = await client.getAccountUserInfo();
      // see more on secondary keys/indices
      // https://docs.deno.com/deploy/kv/manual/#improve-querying-with-secondary-indexes
      const key = kvKeys.info.concat(sub);
      const player: PlayerSchema = {
        // Since the player's battle tag will be public, remove the discriminator (is that what u call it?)
        // so they don't get spammed to death by bots selling gold
        battleTag: battletag.split("#")[0],
        accessToken,
        expiresIn: expiresInDate,
      };

      const res = await kv.atomic().check({ key, versionstamp: null }).set(
        key,
        player,
      ).commit();
      if (res.ok) {
        console.log("Player not yet in the KV, inserting:", player);
      } else {
        console.error("Player already in the KV");
      }

      // Get guild roster from KV and compare with the player's characters
      const { access_token } = await getClientCredentials();
      const memberIds = await getGuildData(client, access_token);

      // console.log("Guild:", memberIds);

      const data = await client.getAccountWoWProfileSummary();
      const playerCharacters = data.wow_accounts.flatMap((account) =>
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
      console.log("Player characters in guild:", playerCharacters);

      const characterKey = kvKeys.characters.concat(sub);
      const res2 = await kv.atomic().check({
        key: characterKey,
        versionstamp: null,
      })
        .set(characterKey, playerCharacters)
        .commit();
      if (res2.ok) {
        console.log(
          "Characters not yet in the KV, inserting:",
          playerCharacters,
        );
      } else {
        console.error("Characters already in the KV");
      }

      // Store mount data
      const mounts = await client.getAccountMountsCollection();
      const totalNumMounts = mounts.mounts.length;

      // Store in KV
      const mountKey = kvKeys.mounts.concat(sub);
      const res3 = await kv.atomic().check({
        key: mountKey,
        versionstamp: null,
      })
        .set(mountKey, { totalNumMounts })
        .commit();
      if (res3.ok) {
        console.log("Mounts not yet in the KV, inserting:", { totalNumMounts });
      } else {
        console.error("Mounts already in the KV");
      }

      return response;
    }
    case "/lb/latest":
      return new Response(JSON.stringify(await Leaderboard.getLatestEntry()));
    case "/lb":
      return new Response(JSON.stringify(await Leaderboard.getEntries()));
    case "/protected":
      return await getSessionId(req) === undefined
        ? new Response("Unauthorized", { status: 401 })
        : new Response("You are allowed");
    default:
      return new Response("Not Found", { status: 404 });
  }
};

export type GuildMemberIds = Set<number>;

// Only contains IDs of all the characters in the guild, which are
// used for comparisons with a user's characters
const getGuildData = async (
  client: BattleNetClient,
  clientCredentialsToken: string,
) => {
  const guildKey = [...kvKeys.guild, GUILD_NAME];
  const guildKV = await kv.get<GuildMemberIds>(guildKey);

  if (guildKV.value !== null && guildKV.versionstamp !== null) {
    console.log("Found guild data in KV");
    return guildKV.value;
  }

  console.log("Guild not in KV, fetching from API...");
  const guild = await client.getGuildRoster(
    clientCredentialsToken,
    GUILD_REALM,
    GUILD_NAME,
  );

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

if (import.meta.main) {
  Deno.serve(handler);
}
