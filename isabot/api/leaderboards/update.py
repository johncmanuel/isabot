import asyncio

import isabot.battlenet.characters as characters
import isabot.battlenet.pvp as pvp
import isabot.battlenet.store as store
import isabot.utils.dictionary as dictionary


async def update_db(cc_access_token: str):
    """
    Updates current DB with new relevant data from a user's character list. This should also
    overwrite any existing data.
    TODO: Refactor the code by creating reusable functions for processing data
    (i.e pvp, mounts, etc).
    TODO: Make API requests in batches to avoid passing rate limit per second:
    (see the section, "Throttling" at https://develop.battle.net/documentation/guides/getting-started)
    """
    chars = await store.get_multiple_data("characters")

    # Get pvp and mounts data from each char in an account and update the DB with it
    for account_id in chars:
        account_len_mounts = 0
        account_pvp_wins = 0
        account_pvp_lost = 0
        mounts_seen = set()
        for char_id in chars[account_id]:
            char = chars[account_id][char_id]
            name = char["name"]
            realm = char["realm"]["slug"]

            char_mounts, char_pvp_sum = await asyncio.gather(
                characters.character_mounts(cc_access_token, name, realm),
                pvp.get_pvp_summary(name, cc_access_token, realm),
            )  # type: ignore

            if char_mounts:
                mounts: list[dict] = char_mounts.get("mounts", [])
                # TODO: turn this into helper func
                for m in mounts:
                    i = dictionary.safe_nested_get(m, "mount", "id")
                    if i:
                        mounts_seen.add(i)

            char_pvp_wins = 0
            char_pvp_lost = 0
            if char_pvp_sum:
                char_pvp_wins, char_pvp_lost = get_bg_statistics(
                    char_pvp_sum.get("pvp_map_statistics", [])
                )

            account_len_mounts = len(mounts_seen)
            account_pvp_wins += char_pvp_wins
            account_pvp_lost += char_pvp_lost

        # TODO: implement a naming system for collection paths on Firestore
        await asyncio.gather(
            store.store_pvp_data(
                account_id,
                {
                    "bg_total_lost": account_pvp_lost,
                    "bg_total_won": account_pvp_wins,
                    "user_id": account_id,
                },
            ),
            store.store_len_mounts(account_id, account_len_mounts),
        )


def get_bg_statistics(pvp_map_statistics: list[dict]):
    char_total_won = 0
    char_total_lost = 0
    for battleground in pvp_map_statistics:
        match_stats = battleground.get("match_statistics")
        if not match_stats:
            continue
        won, lost = match_stats.get("won"), match_stats.get("lost")
        char_total_won += won
        char_total_lost += lost
    return char_total_won, char_total_lost
