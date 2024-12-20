import {
  BATTLENET_LOCALE,
  BATTLENET_NAMESPACES,
  BATTLENET_OAUTH_URL,
  BATTLENET_REGION,
  BATTLENET_URL,
} from "./consts.ts";

interface RequestOptions {
  namespace?: "profile" | "static" | "dynamic";
  region?: string;
  locale?: string;
  baseUrl?: string; // in case we need to override the default
}

export class BattleNetClient {
  private baseUrl: string;
  private defaultRegion: string;
  private defaultLocale: string;
  private namespaces: Record<string, string>;
  private accessToken: string;
  private battleNetOAuthUrl: string;

  constructor(accessToken: string) {
    this.baseUrl = BATTLENET_URL;
    this.defaultRegion = BATTLENET_REGION;
    this.defaultLocale = BATTLENET_LOCALE;
    this.namespaces = BATTLENET_NAMESPACES;
    this.accessToken = accessToken;
    this.battleNetOAuthUrl = BATTLENET_OAUTH_URL;
  }

  private async fetch<T>(
    endpoint: string,
    {
      namespace = "static",
      region = this.defaultRegion,
      locale = this.defaultLocale,
      baseUrl = this.baseUrl,
    }: RequestOptions,
  ): Promise<T> {
    let url = new URL(`${this.baseUrl}${endpoint}`);
    if (baseUrl) {
      url = new URL(`${baseUrl}${endpoint}`);
    }
    if (namespace) {
      url.searchParams.set("namespace", `${namespace}-${region}`);
    }
    url.searchParams.set("locale", locale);

    const response = await fetch(url, {
      headers: {
        "Authorization": `Bearer ${this.accessToken}`,
        "Accept": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(
        `BattleNet API error: ${response.status} ${response.statusText}`,
      );
    }

    return response.json();
  }

  public async getAccountProfileSummary() {
    return await this.fetch("/profile/user/wow", {
      namespace: "profile",
    });
  }

  public async getAccountUserInfo() {
    return await this.fetch("/userinfo", {
      namespace: "profile",
      baseUrl: this.battleNetOAuthUrl,
    });
  }

  public async getAccountMountsCollection() {
    return await this.fetch("/profile/user/wow/collections/mounts", {
      namespace: "profile",
    });
  }

  public async getCharacterMounts(characterName: string, realmSlug: string) {
    return await this.fetch(
      `/profile/user/wow/character/${realmSlug}/${characterName.toLowerCase()}/collections/mounts`,
      {
        namespace: "profile",
      },
    );
  }
}

const getClientCredentials = async () => {
  const clientId = Deno.env.get("BATTLENET_CLIENT_ID");
  const clientSecret = Deno.env.get("BATTLENET_CLIENT_SECRET");
  const response = await fetch(BATTLENET_OAUTH_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "Authorization": `Basic ${btoa(`${clientId}:${clientSecret}`)}`,
    },
    body: "grant_type=client_credentials",
  });
  if (!response.ok) {
    throw new Error(
      `BattleNet API error: ${response.status} ${response.statusText}`,
    );
  }
  return await response.json();
};
