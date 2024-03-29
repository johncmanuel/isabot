from typing import Any, Union

import isabot.utils.dictionary as dictionary
from isabot.battlenet.constants import GUILD_NAME, GUILD_REALM
from isabot.battlenet.helpers import get_bnet_endpt


async def get_guild_roster(
    token: str,
    guild: str = GUILD_NAME,
    realm: str = GUILD_REALM[0],
    namespace: str = "profile",
) -> Union[Any, None]:
    """Returns the guild roster for a guild."""
    return await get_bnet_endpt(
        f"/data/wow/guild/{realm}/{guild}/roster", token, namespace
    )


def get_characters_in_guild(characters: dict, guild_roster: list[dict]) -> dict:
    """
    Returns WoW characters that are in the guild roster.
    This assumes guild_roster is a list of dictionaries obtained from get_guild_roster.
    """
    return {
        k: v
        for k, v in characters.items()
        if k
        in map(
            lambda x: str(
                dictionary.safe_nested_get(x, "character", "id", default="N/A")
            ),
            guild_roster,
        )
    }
