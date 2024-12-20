import { createOAuthHelpers, kv, PlayerSchema } from "./lib/kv-oauth.ts";
import { BattleNetClient } from "./lib/bnet.ts";
import { getExpirationDate } from "./lib/utils.ts";

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
      console.log("Access token:", accessToken, "expires in:", expiresIn);

      const expiresInDate = getExpirationDate(expiresIn);

      const client = new BattleNetClient(accessToken);

      // insert user into KV
      const { sub, battletag } = await client.getAccountUserInfo();
      // Players are mapped to key ["players", sub] where sub is the string form of the player's ID
      // https://docs.deno.com/deploy/kv/manual/#improve-querying-with-secondary-indexes
      const key = ["players", sub];
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

      return response;
    }
    case "/protected":
      return await getSessionId(req) === undefined
        ? new Response("Unauthorized", { status: 401 })
        : new Response("You are allowed");
    default:
      return new Response("Not Found", { status: 404 });
  }
};

if (import.meta.main) {
  Deno.serve(handler);
}
