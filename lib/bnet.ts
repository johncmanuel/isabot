import {
  BATTLENET_LOCALE,
  BATTLENET_NAMESPACES,
  BATTLENET_OAUTH_TOKEN_URI,
  BATTLENET_OAUTH_URL,
  BATTLENET_REGION,
  BATTLENET_URL,
  GUILD_REALM,
  GUILD_SLUG_NAME,
} from "./consts.ts";
import { kv, kvKeys } from "./kv-oauth.ts";
import { getExpirationDate, isTokenExpired } from "./utils.ts";

interface RequestOptions {
  namespace?: "profile" | "static" | "dynamic";
  region?: string;
  locale?: string;
  baseUrl?: string; // in case we need to override the default
  token?: string; // either use account access token or client credentials token
}

export interface WowAccount {
  id: number;
  characters: WowCharacter[];
}

export interface WowCharacter {
  character: {
    href: string;
  };
  protected_character: {
    href: string;
  };
  name: string;
  id: number;
  realm: {
    key: {
      href: string;
    };
    name: string;
    id: number;
    slug: string;
  };
  playable_class: {
    key: {
      href: string;
    };
    name: string;
    id: number;
  };
  playable_race: {
    key: {
      href: string;
    };
    name: string;
    id: number;
  };
  gender: {
    type: string;
    name: string;
  };
  faction: {
    type: string;
    name: string;
  };
  level: number;
}

export interface WowProfileResponse {
  _links: {
    self: {
      href: string;
    };
    user: {
      href: string;
    };
    profile: {
      href: string;
    };
  };
  id: number;
  wow_accounts: WowAccount[];
  collections: {
    href: string;
  };
}

export interface GuildMember {
  character: {
    name: string;
    id: number;
    realm: {
      key: {
        href: string;
      };
      name: string;
      id: number;
      slug: string;
    };
    level: number;
    playable_class: {
      key: {
        href: string;
      };
      name: string;
      id: number;
    };
    playable_race: {
      key: {
        href: string;
      };
      name: string;
      id: number;
    };
  };
  rank: number;
}

export interface GuildRosterResponse {
  _links: {
    self: {
      href: string;
    };
  };
  guild: {
    key: {
      href: string;
    };
    name: string;
    id: number;
    realm: {
      key: {
        href: string;
      };
      name: string;
      id: number;
      slug: string;
    };
    faction: {
      type: string;
      name: string;
    };
  };
  members: GuildMember[];
}

export interface MountMediaAsset {
  key: {
    href: string;
  };
  id: number;
}

export interface MountColor {
  name: string;
}

export interface Mount {
  creature_displays: {
    key: {
      href: string;
    };
    id: number;
  }[];
  id: number;
  is_useable: boolean;
  name: string;
  source: {
    type: string;
    name: string;
  };
  colors?: MountColor[];
  should_exclude_if_uncollected?: boolean;
  faction?: {
    type: string;
    name: string;
  };
  requirements?: {
    faction?: {
      type: string;
      name: string;
    };
    classes?: {
      name: string;
    }[];
    races?: {
      name: string;
    }[];
  };
}

export interface MountsCollectionResponse {
  _links: {
    self: {
      href: string;
    };
  };
  mounts: Mount[];
}

export interface BattleNetAccountUserInfoResponse {
  id: number;
  sub: string;
  battletag: string;
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
      token = this.accessToken,
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
        "Authorization": `Bearer ${token}`,
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

  public async getAccountWoWProfileSummary(): Promise<WowProfileResponse> {
    return await this.fetch<WowProfileResponse>("/profile/user/wow", {
      namespace: "profile",
    });
  }

  public async getAccountUserInfo(): Promise<BattleNetAccountUserInfoResponse> {
    return await this.fetch<BattleNetAccountUserInfoResponse>("/userinfo", {
      namespace: "profile",
      baseUrl: this.battleNetOAuthUrl,
    });
  }

  public async getAccountMountsCollection(): Promise<MountsCollectionResponse> {
    return await this.fetch<MountsCollectionResponse>(
      "/profile/user/wow/collections/mounts",
      {
        namespace: "profile",
      },
    );
  }

  public async getCharacterMounts(
    clientCredentialsToken: string,
    characterName: string,
    realmSlug: string,
  ) {
    return await this.fetch(
      `/profile/wow/character/${realmSlug}/${characterName.toLowerCase()}/collections/mounts`,
      {
        namespace: "profile",
        token: clientCredentialsToken,
      },
    );
  }

  public async getGuildRoster(
    clientCredentialsToken: string,
    realmSlug: string | string[],
    guildName: string,
  ): Promise<GuildRosterResponse> {
    if (Array.isArray(realmSlug)) {
      // Use the first realm in the list
      realmSlug = realmSlug[0];
    }
    return await this.fetch<GuildRosterResponse>(
      `/data/wow/guild/${realmSlug.toLowerCase()}/${guildName.toLowerCase()}/roster`,
      {
        namespace: "profile",
        token: clientCredentialsToken,
      },
    );
  }
}

export interface ClientCredentialsResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  scope: string;
}

export const requestClientCredentials = async (): Promise<
  ClientCredentialsResponse
> => {
  const clientId = Deno.env.get("BATTLENET_CLIENT_ID");
  const clientSecret = Deno.env.get("BATTLENET_CLIENT_SECRET");
  const body = new URLSearchParams({ grant_type: "client_credentials" });
  const response = await fetch(BATTLENET_OAUTH_TOKEN_URI, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "Authorization": `Basic ${btoa(`${clientId}:${clientSecret}`)}`,
    },
    body: body.toString(),
  });
  if (!response.ok) {
    throw new Error(
      `BattleNet API error: ${response.status} ${response.statusText}`,
    );
  }
  return await response.json();
};

// Get client credentials from KV if client credentials already exist and are valid.
// Otherwise, request a new one, store in KV, and return it
export const getClientCredentials = async (): Promise<
  ClientCredentialsResponse
> => {
  // Get from KV if it exists and not expired
  const clientKey = ["clientCredentials"];
  const clientCredentialsInKV = await kv.get<ClientCredentialsResponse>(
    clientKey,
  );
  if (
    (clientCredentialsInKV.value === null &&
      clientCredentialsInKV.versionstamp === null) ||
    isTokenExpired(clientCredentialsInKV.value.expires_in)
  ) {
    // Request new client credentials and store in KV
    const clientCredentials = await requestClientCredentials();
    clientCredentials.expires_in = getExpirationDate(
      clientCredentials.expires_in,
    );
    const res1 = await kv.atomic().set(
      clientKey,
      clientCredentials,
    ).commit();
    if (res1.ok) {
      console.log("Client credentials inserted:", clientCredentials);
    } else {
      console.error("Client credentials already in the KV");
    }
    return clientCredentials;
  }
  return clientCredentialsInKV.value;
};

export const updateGuildData = async () => {
  console.log("Starting weekly guild data update...");

  const { access_token } = await getClientCredentials();
  if (!access_token) {
    throw new Error("Failed to get access token");
  }

  // Create client and fetch new guild data
  const client = new BattleNetClient(access_token);
  if (!client) {
    throw new Error("Failed to create BattleNet client");
  }
  const newGuildData = await client.getGuildRoster(
    access_token,
    GUILD_REALM,
    GUILD_SLUG_NAME,
  );
  if (!newGuildData) {
    throw new Error("Failed to get new guild data");
  }

  const newGuildMemberIds = new Set(
    newGuildData.members.map((member) => member.character.id),
  );

  console.log("Received new guild data, now inserting into KV...");

  // Ensure to overwrite the old guild data in KV with new data
  const kvGuildKey = [...kvKeys.guild, GUILD_SLUG_NAME];
  const res = await kv.atomic().set(kvGuildKey, newGuildMemberIds).commit();
  if (!res.ok) {
    throw new Error("Failed to update guild data in KV");
  }
  console.log("Updated guild data in KV");
};
