from datetime import datetime

import isabot.battlenet.store as store
from isabot.api.leaderboards.data_types import CollectionNames, Entry, get_lb_mappings


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
        # TODO: Store acccount's characters that're in guild in a separate collection
        return Entry(
            players=players_characters,
            date_created=datetime.now().timestamp(),
            mounts=mounts,
            normal_bg_wins=normal_bg_wins,
        )

    async def get_users(self) -> dict[str, dict]:
        return await store.get_multiple_data(CollectionNames.USERS)

    async def get_mounts(self) -> dict[str, dict]:
        """Get mounts from each account"""
        return await store.get_multiple_data(CollectionNames.COLLECTION)

    async def get_normal_bg_stats(self):
        """Get normal battleground stats for each account"""
        return await store.get_multiple_data(CollectionNames.PVP)

    async def upload_entry(self, data: Entry):
        """Upload the entry to the leaderboard collection in the DB"""
        await store.store_data(
            data.model_dump(),
            collection_path=self.db_collection_path,
            include_autogen_id_field=True,
        )

    def format_entry(self, entry: Entry, lb_type: str) -> str:
        """
        Format and return the recent entry.
        """
        # field = result_col = field_key = None
        # if lb_type == "mounts":
        #     result_col = "Number of Mounts"
        #     field_key = "number_of_mounts"
        #     field = entry.mounts
        # elif lb_type == "normal_bg_wins":
        #     result_col = "Total Normal BG Wins"
        #     field_key = "bg_total_won"
        #     field = entry.normal_bg_wins
        # else:
        #     print("no valid lb_types")
        #     raise
        # print("im here!")
        result_col, field_key, field = get_lb_mappings(lb_type, entry)

        table = create_table(entry, field, lb_type, result_col, field_key)

        return table


def create_table(
    entry: Entry, field, lb_type: str, result_col: str, field_key: str
) -> str:
    """Creates a readable leaderboard table for the entries"""

    # Dynamically set column widths for table based on length
    # of the input.
    # To account for battletags that are shorter than the header name ("battletag" in this case),
    # get the max width between the header name and the longest battletag
    battletag_width = max(
        len("battletag"), max_len_str_in_field(entry.players, "battletag")
    )
    field_width = max_len_str_in_field(field, lb_type)

    column_widths = {"battletag": battletag_width, result_col: field_width}

    table = ""

    table = create_table_header(column_widths, table)
    rows = create_table_rows(column_widths, entry, field, result_col, field_key)

    # Sort the rows by the result column and append them to the table
    sorted_rows = sorted(
        rows, key=lambda x: int(str(x[result_col]).strip(" | ")), reverse=True
    )

    table = add_table_rows(sorted_rows, column_widths, table)

    return table


def create_table_header(column_widths: dict[str, int], table: str) -> str:
    """Create the header for the current table."""
    for key, width in column_widths.items():
        table += f"{key.ljust(width)} | "
    return table.rstrip(" | ") + "\n"


def create_table_rows(
    column_widths: dict[str, int],
    entry: Entry,
    field: dict,
    result_col: str,
    field_key: str,
) -> list:
    """Create the rows for the current table."""
    rows = []
    for user_id in entry.players:
        if user_id in field:
            player = entry.players[user_id]
            player.update(field[user_id])
            row = {}
            for key, width in column_widths.items():
                if key == result_col:
                    row[key] = f'{str(player.get(field_key, "")).ljust(width)} | '
                else:
                    row[key] = f'{str(player.get(key, "")).ljust(width)} | '
            rows.append(row)
    return rows


def add_table_rows(rows: list, column_widths: dict[str, int], table: str):
    """Add the rows to the current table."""
    for row in rows:
        for key, width in column_widths.items():
            table += str(row.get(key, "")).ljust(width)
        table = table.rstrip(" | ") + "\n"
    return table


def max_len_str_in_field(field: dict, key: str):
    """Get the max length of the string in a field."""
    return max(len(str(f.get(key, ""))) for f in field.values())


"""
Note to self for future reference:

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
