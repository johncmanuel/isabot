import asyncio
from datetime import datetime
from typing import Optional

import isabot.api.leaderboards.leaderboard as leaderboard
import isabot.api.leaderboards.update as update
import isabot.discord.webhook as webhook
import isabot.utils.concurrency as concurr
from env import DISCORD_WEBHOOK_URL
from isabot.api.leaderboards.leaderboard import Entry
from isabot.discord.discord_types import Embed, EmbedColorCodes, EmbedField


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

    # TODO: Use below mock data for making tests in future
    # entry = Entry(
    #     players={
    #         "12345678": {"battletag": "player1", "id": "12345678"},
    #         "87654321": {"battletag": "player2", "id": "87654321"},
    #         "98765432": {"battletag": "player3", "id": "98765432"},
    #     },
    #     date_created=1643347200.0,
    #     mounts={
    #         "12345678": {"number_of_mounts": 1238},
    #         "87654321": {"number_of_mounts": 38482},
    #         "98765432": {"number_of_mounts": 20},
    #     },
    #     normal_bg_wins={
    #         "12345678": {
    #             "bg_total_won": 120,
    #             "bg_total_lost": 20,
    #             "user_id": "12345678",
    #         },
    #         "87654321": {
    #             "bg_total_won": 80,
    #             "bg_total_lost": 50,
    #             "user_id": "87654321",
    #         },
    #         "98765432": {
    #             "bg_total_won": 200,
    #             "bg_total_lost": 30,
    #             "user_id": "98765432",
    #         },
    #     },
    # )

    # Then make a POST req to a discord webhook representing the current leaderboard
    lb_types = ["normal_bg_wins", "mounts"]
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
        concurr.batch_parallel_run([lambda t=t: prepare_embed(t) for t in lb_types])
        await asyncio.gather(
            *[webhook.run_webhook(DISCORD_WEBHOOK_URL, e) for e in embeds]
        )
    except Exception as error:
        print("error when running webhook", error)
        return


def get_color_by_leaderboard_type(lb_type: Optional[str] = None) -> int:
    """lb_type accepts 'mounts' or 'pvp'. If lb_type is invalid or unspecified, default color is darker gray."""
    if lb_type == "mounts":
        return EmbedColorCodes.DARK_GREEN
    elif lb_type == "normal_bg_wins":
        return EmbedColorCodes.DARK_ORANGE
    return EmbedColorCodes.DARKER_GRAY
