import "./lib/cron.ts";
import {
  createOAuthHelpers,
  kv,
} from "./lib/kv-oauth.ts";
import {
  BattleNetClient,
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
