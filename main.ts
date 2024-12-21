import {
  createOAuthHelpers,
  kv,
  kvKeys,
  PlayerSchema,
} from "./lib/kv-oauth.ts";
import { BattleNetClient, getClientCredentials } from "./lib/bnet.ts";
import { getExpirationDate } from "./lib/utils.ts";
import { GUILD_NAME, GUILD_REALM } from "./lib/consts.ts";

// TODO: Update KV database weekly to remove inactive players and update active players in the guild using a Deno Cron

const handler = async (req: Request) => {
  const { pathname } = new URL(req.url);
  const { handleCallback, getSessionId, signIn, signOut } = createOAuthHelpers(
    req,
  );

  switch (pathname) {
    case "/": {
      const sessionId = await getSessionId(req);

      // Test KV
      // const r = kv.list<PlayerSchema>({ prefix: ["players", "info"] });
      // const k = [];
      // for await (const res of r) k.push(res);
      // console.log(k);

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
      const guild = await client.getGuildRoster(
        access_token,
        GUILD_REALM,
        GUILD_NAME,
      );
      const memberIds = new Set(
        guild.members.map((member) => member.character.id),
      );
      // console.log("Guild:", memberIds);

      // Cache the guild in KV
      // const guildKey = ["guilds", GUILD_NAME, "roster"];
      // const guildRes = await kv.atomic().check({
      //   key: guildKey,
      //   versionstamp: null,
      // }).set(
      //   guildKey,
      //   guild,
      // ).commit();
      // if (guildRes.ok) {
      //   console.log("Guild not yet in the KV, inserting:", guild);
      // } else {
      //   console.error("Guild already in the KV");
      // }
      //
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
      // console.log("Player characters in guild:", playerCharacters);

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
