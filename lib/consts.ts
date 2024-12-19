// Region and locale to retrieve Battle Net data from.
// https://develop.battle.net/documentation/guides/regionality-and-apis
type BattleNetRegion = "us" | "eu" | "kr" | "tw" | "cn";
type BattleNetLocale =
  | "en_US"
  | "es_MX"
  | "pt_BR"
  | "de_DE"
  | "en_GB"
  | "es_ES"
  | "fr_FR"
  | "it_IT"
  | "ru_RU"
  | "ko_KR"
  | "zh_TW"
  | "zh_CN";
export const BATTLENET_REGION: BattleNetRegion = "us";
export const BATTLENET_LOCALE: BattleNetLocale = "en_US";

// Available options are: Static, Dynamic, and Profile
// More information here:
// https://develop.battle.net/documentation/world-of-warcraft/guides/namespaces
//
// Something to note: profile-related data are updated after a character logs out
export const BATTLENET_NAMESPACES = {
  "static": `static-${BATTLENET_REGION}`,
  "dynamic": `dynamic-${BATTLENET_REGION}`,
  "profile": `profile-${BATTLENET_REGION}`,
};

// Base URL for Battle Net API
export const BATTLENET_URL: string =
  `https://${BATTLENET_REGION}.api.blizzard.com`;

// Slug name for AR Club
export const GUILD_NAME: string = "ar-club";

// Slug name for AR Club's realm, Bronzebeard-Shandris
export const GUILD_REALM: [string, string] = ["shandris", "bronzebeard"];

// Battle Net OAuth URL
export const BATTLENET_OAUTH_URL: string = "https://oauth.battle.net";

// Battle Net OAuth authorize and token URIs
export const BATTLENET_OAUTH_AUTHORIZE_URI: string =
  `${BATTLENET_OAUTH_URL}/authorize`;
export const BATTLENET_OAUTH_TOKEN_URI: string = `${BATTLENET_OAUTH_URL}/token`;

// Battle Net OAuth name
export const BATTLENET_OAUTH_NAME: string = "battlenet";
