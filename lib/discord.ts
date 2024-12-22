import type { AppSchema } from "@discord-applications/app";
import {
  APIInteractionResponse,
  createApp,
  InteractionResponseType,
  MessageFlags,
} from "@discord-applications/app";
import { Leaderboard } from "../leaderboard/lb.ts";
import { LeaderboardEntry } from "../leaderboard/types.d.ts";

export const isabotSchema = {
  chatInput: {
    name: "isabot",
    description: "Very cool commands for isabot",
    groups: {
      lb: {
        description: "Leaderboard commands",
        subcommands: {
          latest: {
            description: "Get the latest leaderboard entry",
            // Leave options empty if no options needed
            options: {},
          },
          all: {
            description: "Get all leaderboard entries",
            // Leave options empty if no options needed
            options: {},
          },
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
    schema: isabotSchema,
    applicationID: discordApplicationID,
    publicKey: discordPublicKey,
    token: discordToken,
    register: true,
    path: path,
    invite: { path: "/invite", scopes: ["applications.commands"] },
  }, {
    lb: {
      // @ts-ignore: ignore weird typing error with discord app library
      latest: async (_interaction) => {
        const entry = await Leaderboard.getLatestEntry();
        return sendMsg(formatLeaderboardData(entry));
      },
      // @ts-ignore: ignore weird typing error with discord app library
      all: async (_interaction) => {
        const entries = await Leaderboard.getEntries();
        return sendMsg(entries.map(formatLeaderboardData).join("\n"));
      },
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

export const formatLeaderboardData = (entry: LeaderboardEntry): string => {
  const lines: string[] = [];

  lines.push(`🏆 Leaderboard Entry: ${entry.entry_id}`);
  lines.push(`📅 Date: ${new Date(entry.date_added).toLocaleDateString()}\n`);

  Object.entries(entry.players).forEach(([playerId, player]) => {
    const playerMounts = entry.mounts[playerId]?.number_of_mounts ?? 0;
    lines.push(`👤 ${player.battletag}`);
    lines.push(`   🐎 Mounts: ${playerMounts}`);
  });

  // Join all lines with newlines
  // Discord messages have a 2000 character limit
  return lines.join("\n").slice(0, 2000);
};
