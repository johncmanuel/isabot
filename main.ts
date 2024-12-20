import { createHelpers } from "@deno/kv-oauth";
import {
  BATTLENET_SCOPE,
  createBattleNetOAuthConfig,
  kv,
} from "./lib/kv-oauth.ts";

const getBaseUrl = (req: Request): string => {
  const url = new URL(req.url);
  // Always ensure HTTPS for this kind of project
  return `https://${url.host}`;
};

const createOAuthHelpers = (req: Request) => {
  const baseUrl = getBaseUrl(req);
  console.log(baseUrl);
  const cookieExpiresSecs = Deno.env.get("ENV") !== "development"
    ? 60 * 60 * 24 * 7 // 7 days
    : 0;
  return createHelpers(
    createBattleNetOAuthConfig({
      scope: BATTLENET_SCOPE,
      redirectUri: `${baseUrl}/callback`,
    }),
    {
      cookieOptions: {
        expires: cookieExpiresSecs,
        httpOnly: true,
      },
    },
  );
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
