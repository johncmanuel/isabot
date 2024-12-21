import {
  BATTLENET_OAUTH_AUTHORIZE_URI,
  BATTLENET_OAUTH_TOKEN_URI,
} from "./consts.ts";
import {
  createHelpers,
  getRequiredEnv,
  type OAuth2ClientConfig,
} from "jsr:@deno/kv-oauth";

// https://jsr.io/@deno/kv-oauth/0.11.0/lib/_kv.ts#L2
const DENO_KV_PATH_KEY = "DENO_KV_PATH";
let path = undefined;
if (
  (await Deno.permissions.query({ name: "env", variable: DENO_KV_PATH_KEY }))
    .state === "granted"
) {
  path = Deno.env.get(DENO_KV_PATH_KEY);
}

export const kv = await Deno.openKv(path);

// Keys with players as one of primary keys require appending the player's ID at the end.
export const kvKeys = {
  "info": ["players", "info"],
  "characters": ["players", "characters"],
  "mounts": ["players", "mounts"],
  "leaderboard": ["leaderboard"],
  "guild": ["guild"],
};

export interface RealmKV {
  name: string;
  slug: string;
  id: number;
}

export interface PlayerCharacterKV {
  name: string;
  id: number;
  realm: RealmKV;
}

export type PlayerCharactersKV = PlayerCharacterKV[];

export type GuildMemberIds = Set<number>;

// Logged in player schema for KV
export interface PlayerSchema {
  battleTag: string;
  accessToken: string;
  expiresIn: number;
}

export const createOAuthHelpers = (req: Request) => {
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

export const createBattleNetOAuthConfig = (config?: {
  redirectUri?: string;
  scope?: string[] | string;
}): OAuth2ClientConfig => {
  return {
    clientId: getRequiredEnv("BATTLENET_CLIENT_ID"),
    clientSecret: getRequiredEnv("BATTLENET_CLIENT_SECRET"),
    authorizationEndpointUri: BATTLENET_OAUTH_AUTHORIZE_URI,
    tokenUri: BATTLENET_OAUTH_TOKEN_URI,
    redirectUri: config?.redirectUri,
    defaults: { scope: config?.scope },
  };
};

export const getBaseUrl = (req: Request): string => {
  const url = new URL(req.url);
  // Always ensure HTTPS for this kind of project
  return `https://${url.host}`;
};

export const BATTLENET_SCOPE = ["wow.profile"];
