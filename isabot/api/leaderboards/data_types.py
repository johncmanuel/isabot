from enum import StrEnum

from pydantic import BaseModel


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


class CollectionNames(StrEnum):
    """Collection paths in the database"""

    USERS = "users"
    COLLECTION = "collection"
    PVP = "pvp"


class LeaderboardTypes(StrEnum):
    NORMAL_BG_WINS = "normal_bg_wins"
    MOUNTS = "mounts"
    # MYTHIC = "mythic"


# Different types of leaderboard to post in a Discord embed.
LEADERBOARD_TYPES = [l.value for l in LeaderboardTypes]


def get_lb_mappings(
    lb_type: str,
    entry: Entry,
) -> tuple[str, str, dict]:
    """Gets the data type mappings for the leaderboard entry."""
    lb_mappings = {
        LeaderboardTypes.MOUNTS.value: {
            "result_col": "Number of Mounts",
            "field_key": "number_of_mounts",
            "field": entry.mounts,
        },
        LeaderboardTypes.NORMAL_BG_WINS.value: {
            "result_col": "Total Normal BG Wins",
            "field_key": "bg_total_won",
            "field": entry.normal_bg_wins,
        },
    }
    l = lb_mappings.get(lb_type)
    if not l:
        raise ValueError("Invalid leaderboard type")
    return l["result_col"], l["field_key"], l["field"]
