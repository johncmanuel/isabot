import {
  BATTLENET_OAUTH_AUTHORIZE_URI,
  BATTLENET_OAUTH_TOKEN_URI,
} from "./consts.ts";
import { getRequiredEnv, type OAuth2ClientConfig } from "jsr:@deno/kv-oauth";

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
