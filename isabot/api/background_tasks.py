import asyncio
import traceback
from datetime import datetime
from typing import Optional

import isabot.api.leaderboards.leaderboard as leaderboard
import isabot.api.leaderboards.update as update
import isabot.discord.webhook as webhook
import isabot.utils.concurrency as concurr
from env import DISCORD_WEBHOOK_URL
from isabot.api.leaderboards.data_types import LEADERBOARD_TYPES  # , Entry

# from isabot.api.leaderboards.mock.mock_data import mock_entry1
from isabot.discord.discord_types import Embed, EmbedColorCodes, EmbedField


async def update_db_and_upload_entry(cc_access_token: str, auth_url: str) -> None:
    """Background task that will update the DB with relevant data and upload the latest entry"""
    try:
        print("running update function")
        await update.update_db(cc_access_token)
    except Exception as error:
        print("couldn't run update function:", error)

    print("processed update and uploaded to firestore")
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

    print("processed entry and uploaded to firestore")

    # entry = mock_entry1

    # Then make a POST req to a discord webhook representing the current leaderboard
    embeds = []

    def prepare_embed(lb_type: str):
        scores = lb.format_entry(entry, lb_type)
        start_date = datetime.fromtimestamp(entry.date_created).strftime("%c")
        embed = Embed(
            title=f"AR Club Leaderboard - {lb_type.replace('_', ' ').title()}",
            description="Weekly WoW guild leaderboard for the AR Club!",
            auth_url=auth_url,
            lb_type=lb_type,
            start_date=start_date,
            color=get_color_by_leaderboard_type(lb_type),
            scores=scores,
            fields=[
                EmbedField(
                    name=f"Register your Battle Net account down below:",
                    value=f"[Click me!]({auth_url})",
                ),
                EmbedField(
                    name=f"Leaderboard for week of {start_date}",
                    value=f"```{scores}```",
                    inline=True,
                ),
            ],
        ).model_dump()
        embeds.append({"embeds": [embed]})

    # Run the webhook operations in parallel
    try:
        concurr.batch_parallel_run(
            [lambda t=t: prepare_embed(t) for t in LEADERBOARD_TYPES]
        )
        await asyncio.gather(
            *[webhook.run_webhook(DISCORD_WEBHOOK_URL, e) for e in embeds]
        )
        print("processed embeds and sent data to discord webhook")
    except Exception:
        print("error when running webhook", traceback.format_exc())
        return


def get_color_by_leaderboard_type(lb_type: Optional[str] = None) -> int:
    """lb_type accepts 'mounts' or 'pvp'. If lb_type is invalid or unspecified, default color is darker gray."""
    if lb_type == "mounts":
        return EmbedColorCodes.DARK_GREEN
    elif lb_type == "normal_bg_wins":
        return EmbedColorCodes.DARK_ORANGE
    return EmbedColorCodes.DARKER_GRAY
