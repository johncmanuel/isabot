import {
  BATTLENET_OAUTH_AUTHORIZE_URI,
  BATTLENET_OAUTH_TOKEN_URI,
} from "./consts.ts";
import { getRequiredEnv, type OAuth2ClientConfig } from "jsr:@deno/kv-oauth";

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
