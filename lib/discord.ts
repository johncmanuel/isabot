import type { AppSchema } from "@discord-applications/app";
import {
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
            options: {},
          },
        },
      },
    },
  },
} as const satisfies AppSchema;

export const discordAppHandler = createApp({
  schema: isabotSchema,
  applicationID: Deno.env.get("DISCORD_APP_ID")!,
  publicKey: Deno.env.get("DISCORD_PUBLIC_KEY")!,
  token: Deno.env.get("DISCORD_TOKEN")!,
  register: true,
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

export const sendMsg = (message: string) => {
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
