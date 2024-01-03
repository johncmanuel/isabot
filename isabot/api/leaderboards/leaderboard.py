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

Leaderboard data scheme:

Weekly leaderboard entry data scheme 
1. id (using firestore's autogen ids)
2. players (using battletags) 
3. date_updated (UTC epoch)
4. mounts (unordered)
5. normal_bg_wins (unordered)
6. arena_wins (TBA)

Mounts data scheme for webhook
1. Weekly leaderboard entry ID
2. Mounts (from weekly leaderboard entry)

Normal BG wins for webhook
1. Weekly leaderboard entry ID
2. Mounts (from weekly leaderboard entry)

Algo for the entire leaderboard
1. Register users via bnet oauth
2. Send relevant data to relevant DB collections (pvp, collection (for mounts), etc) 
3. Use relevant data to create an entry under collection: leaderboard, using data scheme above 
4. For each cron job ran, use 

"""
from pydantic import BaseModel

import isabot.battlenet.store as store


class Entry(BaseModel):
    """
    Weekly leaderboard entry data scheme
    1. entry_id (using firestore's autogen ids)
    2. players (using battletags)
    3. date_updated (UTC epoch)
    4. mounts (unordered)
    5. normal_bg_wins (unordered)
    6. arena_wins (TBA)

    Example data on Firestore:

    Collection       Document               ABCD1234
    leaderboard      "ABCD1234" ->  See Fields (or keys) below
                                    "entry_id": "ABCD1234"
                                    "players": [{"123456": {"battletag": "ABCD#9876", id: "123456"}}, ...]
                                    "date_added": 38873943453
                                    "mounts": [{"123456": {"len_mounts": 170}}, ...]
                                    "normal_bg_wins": [{"123456": {"bg_wins": 420}}, ...]
                                    ...
    """

    entry_id: str
    players: list[dict]
    date_updated: int
    mounts: list[dict]
    normal_bg_wins: list[dict]


class Leaderboard:
    def __init__(
        self, cc_access_token: str, db_collection_name: str = "leaderboard"
    ) -> None:
        self.cc_access_token = cc_access_token
        self.db_collection_name = db_collection_name

    def create_entry(self, data: Entry):
        store.store_data(data.model_dump(), collection_path=self.db_collection_name)

    def get_characters_from_leaderboard(self) -> list[dict]:
        chars = []

        return chars

    # def update_leaderboard(self, data: dict):
    #     """Store data in leaderboard collection"""
    #     store.store_data(data=data, collection_path=self.db_collection_name)
