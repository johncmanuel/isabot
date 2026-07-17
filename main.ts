import {
  createOAuthHelpers,
  kv,
  kvKeys,
  PlayerCharacterKV,
  PlayerCharactersKV,
} from "./lib/kv-oauth.ts";
import {
  BattleNetClient,
  getClientCredentials,
  updateGuildData,
} from "./lib/bnet.ts";
import { getExpirationDate } from "./lib/utils.ts";
import { Leaderboard } from "./leaderboard/lb.ts";
// import { dummyLeaderboardEntry } from "./leaderboard/dummyData.ts";
import {
  createDiscordApp,
  discordInviteUrl,
  withErrorResponse,
} from "./lib/discord.ts";
import {
  savePlayer,
  savePlayerGuildCharacters,
  savePlayersMounts,
} from "./lib/service.ts";

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

      const userinfo = await client.getAccountUserInfo();
      if (userinfo === null) {
        console.error("Failed to fetch user info from API");
        return response;
      }
      const { sub, battletag } = userinfo;
      console.log("Player:", battletag);

      // Since the player's battle tag will be public, remove the discriminator (is that what u call it?)
      // so they don't get spammed to death by bots selling gold
      await savePlayer({
        battleTag: battletag.split("#")[0],
        accessToken,
        expiresIn: expiresInDate,
      }, sub);

      await savePlayerGuildCharacters(client, sub);
      await savePlayersMounts(client, sub);

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
        // await updateAllPlayersData();
        const allEntries = await Array.fromAsync(kv.list({ prefix: [] }));
        console.log(allEntries);
        return new Response("Updated guild data, other stuff too");
      }
      return new Response("Not found", { status: 404 });
    case "/discord":
      return withErrorResponse(app)(req);
    case "/invite":
      return Response.redirect(
        discordInviteUrl(Deno.env.get("DISCORD_APPLICATION_ID") as string),
      );
    case "/code": {
      const github = "https://github.com/johncmanuel/isabot";
      return Response.redirect(github);
    }
    default:
      return new Response("Not Found", { status: 404 });
  }
};

if (import.meta.main) {
  Deno.serve(handler);
}
