import { createHelpers } from "@deno/kv-oauth";
import { createBattleNetOAuthConfig } from "./lib/oauth.ts";

const { handleCallback, getSessionId, signIn, signOut } = createHelpers(
  createBattleNetOAuthConfig(),
  {
    cookieOptions: {
      expires: 60 * 60 * 24 * 7,
      httpOnly: true,
    },
  },
);

const handler = async (req: Request) => {
  const { pathname } = new URL(req.url);
  switch (pathname) {
    case "/signin":
      return await signIn(req);
    case "/signout":
      return await signOut(req);
    case "/callback": {
      const { response } = await handleCallback(req);
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
