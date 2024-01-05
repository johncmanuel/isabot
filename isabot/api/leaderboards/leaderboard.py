"""
How the leaderboard system will work:

Registering users to the leaderboard
1. user will login through web server
2. add relevant data to DB

Updating the leaderboard
1. Use FastAPI's background tasks, cron jobs, or other ways of performing background tasks 
to query each account's characters and update the relevant data for character's 
appropiate Battle Net account on the DB
2. For each update (weekly at Sunday), a new leaderboard entry will be created
under the "leaderboard" collection with a unique autogen ID 

Note that the leaderboard will use the account's data for the leaderboard,
not the individual character's data

Sending the leaderboard data
1. Use discord's webhook to send the weekly leaderboards

Mounts data scheme for webhook
1. Weekly leaderboard entry ID
2. Mounts (from weekly leaderboard entry)

Normal BG wins for webhook
1. Weekly leaderboard entry ID
2. Mounts (from weekly leaderboard entry)

Algo for the entire leaderboard
1. Register users via bnet oauth
2. Send relevant data to relevant DB collections (pvp, collection (for mounts), etc) 
3. For each cron job, use relevant data to create an entry under collection: leaderboard, using data scheme above  

"""

import asyncio
from time import time
from typing import Optional

from pydantic import BaseModel

import isabot.battlenet.characters as characters
import isabot.battlenet.pvp as pvp
import isabot.battlenet.store as store
import isabot.utils.dictionary as dictionary


class Entry(BaseModel):
    """
    Weekly leaderboard entry data scheme
    1. entry_id (using firestore's autogen ids)
    2. players (using battletags)
    3. date_created (UTC epoch)
    4. mounts (unordered)
    5. normal_bg_wins (unordered)
    6. arena_wins (TBA)

    Example data on Firestore:

    Collection       Document               ABCD1234
    leaderboard      "ABCD1234" ->  See Fields (or keys) below
                                    "entry_id": "ABCD1234"
                                    "players": {"123456": {"battletag": "ABCD#9876", id: "123456"}}, ...}
                                    "date_added": 38873943453.28472
                                    "mounts": {"123456": {"len_mounts": 170}}, ...
                                    "normal_bg_wins": {"123456": {"bg_wins": 420}, ...}
                                    ...
    """

    entry_id: Optional[str] = None
    players: dict[str, dict]
    date_created: float
    mounts: dict[str, dict]
    normal_bg_wins: dict[str, dict]


class Leaderboard:
    def __init__(
        self, cc_access_token: str, db_collection_path: str = "leaderboard"
    ) -> None:
        self.cc_access_token = cc_access_token
        self.db_collection_path = db_collection_path

    def create_entry(
        self,
        players: dict[str, dict],
        mounts: dict[str, dict],
        normal_bg_wins: dict[str, dict],
    ):
        return Entry(
            players=players,
            date_created=time(),
            mounts=mounts,
            normal_bg_wins=normal_bg_wins,
        )

    def upload_entry(self, data: Entry):
        store.store_data(data.model_dump(), collection_path=self.db_collection_path)

    async def update_db(self):
        """Updates current DB with new relevant data from a user's character list"""
        chars = store.get_multiple_data("characters")

        # Get pvp and mounts data from each char in an account and update the DB with it
        for account_id in chars:
            account_len_mounts = 0
            account_pvp_wins = 0
            account_pvp_lost = 0
            mounts_seen = set()
            for char in chars[account_id]["characters"]:
                name = char["name"].lower()
                realm = char["realm"]["slug"]
                # char_id = char["id"]

                char_mounts, char_pvp_sum = await asyncio.gather(
                    characters.character_mounts(self.cc_access_token, name, realm),
                    pvp.get_pvp_summary(name, self.cc_access_token, realm),
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
                    char_pvp_wins, char_pvp_lost = self.get_bg_statistics(
                        char_pvp_sum.get("pvp_map_statistics", [])
                    )

                account_len_mounts = len(mounts_seen)
                account_pvp_wins += char_pvp_wins
                account_pvp_lost += char_pvp_lost

            # TODO: implement a naming system for collection paths on Firestore
            store.store_pvp_data(
                account_id,
                {
                    "bg_total_lost": account_pvp_lost,
                    "bg_total_won": account_pvp_wins,
                    "user_id": account_id,
                },
            )
            store.store_len_mounts(account_id, account_len_mounts)

    def get_bg_statistics(self, pvp_map_statistics: list[dict]):
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
