import type { AppSchema } from "@discord-applications/app";
import {
  APIInteractionResponse,
  createApp,
  InteractionResponseType,
  MessageFlags,
} from "@discord-applications/app";
import { Leaderboard } from "../leaderboard/lb.ts";
import { LeaderboardEntry } from "../leaderboard/types.d.ts";
import { dummyLeaderboardEntry } from "../leaderboard/dummyData.ts";

export const isabotSchema = {
  chatInput: {
    name: "lb",
    description: "Leaderboard commands for isabot",
    groups: {
      cmd: {
        description: "Leaderboard commands",
        subcommands: {
          latest: {
            description: "Get the latest leaderboard entry",
            // Leave options empty if no options needed
            options: {},
          },
          // TODO: Implement other slash commands?
          // all: {
          //   description: "Get all leaderboard entries",
          //   // Leave options empty if no options needed
          //   options: {},
          // },
        },
      },
    },
  },
} as const satisfies AppSchema;

export const createDiscordApp = (
  discordApplicationID: string,
  discordPublicKey: string,
  discordToken: string,
  path: string,
) => {
  return createApp({
    // https://jsr.io/@discord-applications/app/doc/~/AppHandlerOptions
    schema: isabotSchema,
    applicationID: discordApplicationID,
    publicKey: discordPublicKey,
    token: discordToken,
    register: true,
    path: path,
    // prob not needed since it's handled by the other handler, but leaving it here
    invite: { path: "/invite", scopes: ["applications.commands"] },
  }, {
    cmd: {
      // @ts-ignore: ignore weird typing error with discord app library
      latest: async (_interaction) => {
        if (Deno.env.get("ENV") === "dev") {
          return handleLeaderboardCommand([dummyLeaderboardEntry]);
        }
        const entry = await Leaderboard.getLatestEntry();
        return handleLeaderboardCommand([entry]);
      },
      // @ts-ignore: ignore weird typing error with discord app library
      // all: async (_interaction) => {
      //   if (Deno.env.get("ENV") === "dev") {
      //     return handleLeaderboardCommand([
      //       dummyLeaderboardEntry,
      //       dummyLeaderboardEntry,
      //     ]);
      //   }
      //   const entries = await Leaderboard.getEntries();
      //   return handleLeaderboardCommand(entries);
      // },
    },
  });
};

// For intercepting errors and sending them as Discord ephemeral messages
// Source: https://github.com/acmcsufoss/lc-dailies/blob/main/lib/api/discord/app.ts#L127
// Modified slightly to use sendMsg() for structuring the payload
export function withErrorResponse(
  oldHandle: (request: Request) => Promise<Response>,
): (request: Request) => Promise<Response> {
  return async function handle(request: Request): Promise<Response> {
    return await oldHandle(request)
      .catch((error) => {
        if (!(error instanceof Error)) {
          throw error;
        }
        return Response.json(
          sendMsg(`Error: ${error.message}`),
        );
      });
  };
}

export const sendMsg = (message: string): APIInteractionResponse => {
  return {
    type: InteractionResponseType.ChannelMessageWithSource,
    data: {
      content: message,
      // Ensure only the user who invoked the command can see the message
      // so it doesn't flood text channels with bot command outputs
      flags: MessageFlags.Ephemeral,
    },
  };
};

export const formatLeaderboardData = (entries: LeaderboardEntry[]): string => {
  const DISCORD_MAX_LENGTH = 2000;

  if (!entries || entries.length === 0) {
    return "❌ No leaderboard entries available";
  }

  const formattedEntries = entries.map((entry) => {
    if (!entry || Object.keys(entry).length === 0) {
      return "❌ No leaderboard entry found";
    }

    const lines: string[] = [];

    lines.push(`🏆 Leaderboard Entry: ${entry.entry_id ?? "Unknown"}`);
    lines.push(
      `📅 Date: ${
        entry.date_added
          ? new Date(entry.date_added).toLocaleDateString()
          : "Unknown"
      }\n`,
    );

    if (!entry.players || Object.keys(entry.players).length === 0) {
      lines.push("👥 No players found");
    } else {
      Object.entries(entry.players).forEach(([playerId, player], idx) => {
        const rankNum = idx + 1;
        if (!player) {
          lines.push(
            `${rankNum}) Player ID: ${playerId} (Invalid player data)`,
          );
          return;
        }

        const playerMounts = entry.mounts?.[playerId]?.number_of_mounts ?? 0;
        lines.push(`${rankNum}) ${player.battletag ?? "Unknown Player"}`);
        lines.push(`   🐎 Mounts: ${playerMounts}`);
      });
    }
    return lines.join("\n");
  });

  return formattedEntries.join("\n\n").slice(0, DISCORD_MAX_LENGTH);
};

export const handleLeaderboardCommand = (
  entries: LeaderboardEntry[],
): APIInteractionResponse => {
  const formattedMessage = formatLeaderboardData(entries);

  return sendMsg(formattedMessage);
};

export const discordInviteUrl = (applicationID: string) => {
  return `https://discord.com/api/oauth2/authorize?client_id=${applicationID}&scope=applications.commands`;
};
