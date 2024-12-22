import {
  createOAuthHelpers,
  getBaseUrl,
  GuildMemberIds,
  kv,
  kvKeys,
  PlayerCharacterKV,
  PlayerCharactersKV,
  PlayerSchema,
} from "./lib/kv-oauth.ts";
import {
  BattleNetClient,
  getClientCredentials,
  updateGuildData,
} from "./lib/bnet.ts";
import { getExpirationDate } from "./lib/utils.ts";
import { GUILD_REALM, GUILD_SLUG_NAME } from "./lib/consts.ts";
import { Leaderboard } from "./leaderboard/lb.ts";
import { dummyLeaderboardEntry } from "./leaderboard/dummyData.ts";
import {
  createDiscordApp,
  discordInviteUrl,
  withErrorResponse,
} from "./lib/discord.ts";

// Order of Deno Cron executions
// 1. Update Guild Data
// 2. Update all KV players' data w/ client credentials token
// 3. Create and send new leaderboard entry to Discord webhook

// Send at 10 AM PST on Saturday
Deno.cron("Update Guild Data", "0 18 * * SAT", async () => {
  await updateGuildData();
});

// Send at 5 PM PST on Saturday
Deno.cron("Update all KV players data", "0 0 * * SUN", async () => {
  // Update mounts for all players using client credentials by first
  // iterating through all characters for a particular player and
  // then updating the total number of mounts (for example)
  await updateAllPlayersData();
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

// Send at 12 PM PST on Sunday
Deno.cron("Create and send new leaderboard entry", "0 20 * * SUN", async () => {
  console.log("Creating new leaderboard entry...");
  const entry = await Leaderboard.createEntry();
  console.log("Created new leaderboard entry, sending to webhook");
  await Leaderboard.sendMountLBtoDiscord(
    Deno.env.get("DISCORD_WEBHOOK_URL") as string,
    entry,
    `${Deno.env.get("BASE_URL")}/signin`,
  );
});

const handler = async (req: Request) => {
  const { pathname } = new URL(req.url);
  const { handleCallback, getSessionId, signIn, signOut } = createOAuthHelpers(
    req,
  );
  const app = await createDiscordApp(
    Deno.env.get("DISCORD_APPLICATION_ID") as string,
    Deno.env.get("DISCORD_PUBLIC_KEY") as string,
    Deno.env.get("DISCORD_TOKEN") as string,
    "/discord",
  );

  switch (pathname) {
    case "/": {
      const sessionId = await getSessionId(req);
      if (sessionId) {
        console.log("Session ID:", sessionId);
        return new Response(
          `you're signed in! welcome to isabot 2.0! sessionId: ${sessionId}`,
        );
      }
      return new Response("hi welcome to isabot 2.0!");
    }
    case "/signin":
      return await signIn(req);
    case "/signout":
      return await signOut(req);
    // Need to add some protection guards on the API requests since I may forsee abuse of the API
    // when constantly logging in back and forth. You'll see when you start reading the code
    case "/callback": {
      const { response, tokens } = await handleCallback(req);
      const { expiresIn, accessToken } = tokens;

      // Need to end early if none are found
      if (!accessToken) {
        console.error("No access token found");
        return response;
      } else if (!expiresIn) {
        console.error("No expiration date found");
        return response;
      }

      const expiresInDate = Math.floor(getExpirationDate(expiresIn));
      const client = new BattleNetClient(accessToken);

      // insert user into KV
      const userinfo = await client.getAccountUserInfo();
      if (userinfo === null) {
        console.error("Failed to fetch user info from API");
        return response;
      }
      const { sub, battletag } = userinfo;
      console.log("Player:", battletag);

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
        console.log("Player not yet in the KV, inserting them now.");
      } else {
        console.error("Player already in the KV");
      }

      // check if player's characters already exist. insert if not
      const charKey = kvKeys.characters.concat(sub);
      const charKV = await kv.get<PlayerCharacterKV[]>(charKey);

      if (
        charKV.value !== null && charKV.versionstamp !== null &&
        charKV.value.length > 0
      ) {
        console.log("Found player characters in KV, no need to fetch from API");
      } else {
        const { access_token } = await getClientCredentials();
        const memberIds = await getGuildData(client, access_token);
        const data = await client.getAccountWoWProfileSummary();
        if (data === null) {
          console.error("Failed to fetch WoW profile summary from API");
        } else {
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

          const res2 = await kv.atomic()
            .set(charKey, playerCharacters)
            .commit();
          if (res2.ok) {
            console.log(
              "Characters not yet in the KV, inserting them now",
            );
          } else {
            console.error("Failed to insert characters in the KV");
          }
        }
      }

      // Check if player's mounts already
      const mountsKey = kvKeys.mounts.concat(sub);
      const mountsKV = await kv.get<{ totalNumMounts: number }>(mountsKey);
      if (mountsKV.value !== null && mountsKV.versionstamp !== null) {
        console.log("Found mounts in KV, no need to fetch from API");
      } else {
        const mounts = await client.getAccountMountsCollection();
        let totalNumMounts = 0;
        if (mounts === null) {
          console.error("Failed to fetch mounts data from API");
        } else {
          totalNumMounts = mounts.mounts.length;
        }
        const res3 = await kv.atomic()
          .set(mountsKey, { totalNumMounts })
          .commit();
        if (res3.ok) {
          console.log("Mounts not yet in the KV, inserting:", {
            totalNumMounts,
          });
        } else {
          console.error("Failed to insert mounts into KV");
        }
      }

      return response;
    }
    case "/lb/latest":
      return new Response(JSON.stringify(await Leaderboard.getLatestEntry()));
    case "/lb":
      return new Response(JSON.stringify(await Leaderboard.getEntries()));
    // case "/protected":
    //   return await getSessionId(req) === undefined
    //     ? new Response("Unauthorized", { status: 401 })
    //     : new Response("You are allowed");
    case "/test":
      if (Deno.env.get("ENV") === "dev") {
        // await updateGuildData();
        // await Leaderboard.sendMountLBtoDiscord(
        //   Deno.env.get("DISCORD_WEBHOOK_URL") as string,
        //   dummyLeaderboardEntry,
        //   `${getBaseUrl(req)}/signin`,
        // );
        await updateAllPlayersData();
        return new Response("Updated guild data, other stuff too");
      }
      return new Response("Not found", { status: 404 });
    case "/discord":
      return withErrorResponse(app)(req);
    case "/invite":
      return Response.redirect(
        discordInviteUrl(Deno.env.get("DISCORD_APPLICATION_ID") as string),
      );
    default:
      return new Response("Not Found", { status: 404 });
  }
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

if (import.meta.main) {
  Deno.serve(handler);
}
