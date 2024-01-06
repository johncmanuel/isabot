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

from time import time
from typing import Optional

from pydantic import BaseModel

import isabot.battlenet.characters as characters
import isabot.battlenet.guild as guild
import isabot.battlenet.pvp as pvp
import isabot.battlenet.store as store
import isabot.utils.dictionary as dictionary
from isabot.battlenet.constants import GUILD_REALM


class Entry(BaseModel):
    """
        Weekly leaderboard entry data scheme
        1. entry_id (using firestore's autogen ids, so will be included)
        2. players (using battletags)
        3. date_created (UTC epoch)
        4. mounts (unordered)
        5. normal_bg_wins (unordered)
        6. arena_wins (TBA)
    55
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
        players_characters: dict[str, dict],
        mounts: dict[str, dict],
        normal_bg_wins: dict[str, dict],
    ):
        return Entry(
            players=players_characters,
            date_created=time(),
            mounts=mounts,
            normal_bg_wins=normal_bg_wins,
        )

    # async def get_players_in_guild(self) -> dict[str, dict]:
    #     """Get players that're only in the guild for each account"""
    #     players = {}

    #     # TODO: Store acccount's characters that're in guild in a separate collection
    #     guild_roster = (await guild.get_guild_roster(self.cc_access_token)).get(
    #         "members", []
    #     )
    #     account_characters = await store.get_multiple_data("characters")

    #     # Filter results by cross-referencing current guild roster
    #     for account_id in account_characters:
    #         chars = account_characters[account_id]
    #         players[account_id] = guild.get_characters_in_guild(chars, guild_roster)

    #     return players

    async def get_users(self) -> dict[str, dict]:
        return await store.get_multiple_data("users")

    async def get_mounts(self) -> dict[str, dict]:
        """Get mounts from each account"""
        return await store.get_multiple_data("collection")

    async def get_normal_bg_stats(self):
        """Get normal battleground stats for each account"""
        return await store.get_multiple_data("pvp")

    async def upload_entry(self, data: Entry):
        await store.store_data(
            data.model_dump(),
            collection_path=self.db_collection_path,
            include_autogen_id_field=True,
        )
