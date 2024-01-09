import asyncio

import isabot.api.leaderboards.leaderboard as leaderboard
import isabot.api.leaderboards.update as update


async def update_db_and_upload_entry(cc_access_token: str):
    """Background task that will update the DB with relevant data and upload the latest entry"""
    try:
        await update.update_db(cc_access_token)
    except Exception as error:
        print("couldn't run update function:", error)

    try:
        lb = leaderboard.Leaderboard(cc_access_token)
        u, m, p = await asyncio.gather(
            lb.get_users(),
            lb.get_mounts(),
            lb.get_normal_bg_stats(),
        )
        entry = lb.create_entry(u, m, p)
        await lb.upload_entry(entry)
    except Exception as error:
        print("couldn't run entry function:", error)

    # Then make a POST req to a discord webhook
    # ...
