import asyncio
from datetime import datetime
from enum import IntEnum
from typing import Optional

import isabot.api.leaderboards.leaderboard as leaderboard
import isabot.api.leaderboards.update as update
import isabot.discord.webhook as webhook
import isabot.utils.concurrency as concurr
from env import DISCORD_WEBHOOK_URL


async def update_db_and_upload_entry(cc_access_token: str, auth_url: str) -> None:
    """Background task that will update the DB with relevant data and upload the latest entry"""
    try:
        await update.update_db(cc_access_token)
    except Exception as error:
        print("couldn't run update function:", error)

    try:
        lb = leaderboard.Leaderboard(cc_access_token)
        users, mounts, bg = await asyncio.gather(
            lb.get_users(),
            lb.get_mounts(),
            lb.get_normal_bg_stats(),
        )
        entry = lb.create_entry(users, mounts, bg)
        await lb.upload_entry(entry)
    except Exception as error:
        print("couldn't run entry function:", error)
        # If uploading a new entry didn't work, just end the task here.
        return

    # Then make a POST req to a discord webhook representing the current leaderboard
    lb_types = ["normal_bg_wins", "mounts"]
    embeds = []

    def prepare_embed(lb_type: str):
        options = {
            "title": f"AR Club Leaderboard - {lb_type.replace('_', ' ').title()}",
            "description": "Weekly WoW guild leaderboard for the AR Club!",
            "auth_url": auth_url,
            "lb_type": lb_type,
            "start_date": datetime.fromtimestamp(entry.date_created).strftime("%c"),
            "scores": lb.format_entry(entry, lb_type),
        }
        embed = create_embed(options)
        embeds.append({"embeds": embed})

    # Run the webhook operations in parallel
    try:
        concurr.batch_parallel_run([lambda t=t: prepare_embed(t) for t in lb_types])
        await asyncio.gather(
            *[webhook.run_webhook(DISCORD_WEBHOOK_URL, e) for e in embeds]
        )
    except Exception as error:
        print("error when running webhook", error)
        return


def create_embed(options: dict):
    """
    https://discord.com/developers/docs/resources/channel#embed-object
    TODO: Create a type for options; it'll make the dev experience a bit
    better.
    """
    embed = {
        "title": options["title"],
        "description": options["description"],
        "color": get_color_by_leaderboard_type(options["lb_type"]),
        "fields": [
            {
                "name": f"Register your Battle Net account down below:",
                "value": f"[Click me!]({options['auth_url']})",
            },
            {
                "name": f"Leaderboard for week of {options['start_date']}",
                "value": f"```{options['scores']}```",
                "inline": True,
            },
        ],
    }

    return [embed]


def get_color_by_leaderboard_type(lb_type: Optional[str] = None):
    """lb_type accepts 'mounts' or 'pvp'. If lb_type is invalid or unspecified, default color is darker gray."""
    if lb_type == "mounts":
        return EmbedColorCodes.DARK_GREEN
    elif lb_type == "normal_bg_wins":
        return EmbedColorCodes.DARK_ORANGE
    return EmbedColorCodes.DARKER_GRAY


class EmbedColorCodes(IntEnum):
    """
    Will only cherry-pick the colors that are needed.
    https://discordpy.readthedocs.io/en/latest/api.html#colour
    """

    DARK_GREEN = 0x1F8B4C
    DARK_ORANGE = 0xA84300  # The closest to brown we can get... :(
    DARKER_GRAY = 0x546E7A
