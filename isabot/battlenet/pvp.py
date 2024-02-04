# from typing import Literal, get_args

from isabot.battlenet.constants import GUILD_REALM
from isabot.battlenet.helpers import get_bnet_endpt


async def get_pvp_summary(character_name: str, token: str, realm: str = GUILD_REALM[0]):
    """Return a WoW character's pvp summary data."""
    return await get_bnet_endpt(
        f"/profile/wow/character/{realm}/{character_name.lower()}/pvp-summary",
        token,
        "profile",
    )


# async def get_pvp_bracket(
#     character_name: str,
#     token: str,
#     pvp_bracket: PVP_BRACKETS,
#     realm: str = GUILD_REALM[0],
# ):
#     try:
#         return await get_bnet_endpt(
#             f"/profile/wow/character/{realm}/{character_name.lower()}/pvp-bracket/{pvp_bracket}",
#             token,
#             "profile",
#         )
#     except Exception:
#         return None


async def get_normal_bg_data_from_chars(
    wow_chars_in_guild: dict, cc_access_token: str, user_id: str
) -> dict:
    """
    Get total wins and loses from each WoW character's battleground statistics
    TODO: Since the logic is being duplicated multiple times, refactor it to a helper function.
    """
    account_bg_total_won, account_bg_total_lost = 0, 0
    for char in wow_chars_in_guild.values():
        char_pvp_data = await get_pvp_summary(
            char["name"], cc_access_token, char["realm"]["slug"]
        )
        if char_pvp_data:
            pvp_map_stats = char_pvp_data.get("pvp_map_statistics", [])
            char_total_won = sum(
                match.get("match_statistics", {}).get("won", 0)
                for match in pvp_map_stats
            )
            char_total_lost = sum(
                match.get("match_statistics", {}).get("lost", 0)
                for match in pvp_map_stats
            )

            account_bg_total_won += char_total_won
            account_bg_total_lost += char_total_lost
    return {
        "user_id": user_id,
        "bg_total_won": account_bg_total_won,
        "bg_total_lost": account_bg_total_lost,
    }


# async def pvp_bracket_data(
#     wow_chars_in_guild: list[dict],
#     cc_access_token: str,
#     # pvp_bracket: PVP_BRACKETS,
#     user_id: str,
# ) -> list[dict]:
#     pp = []
#     for char in wow_chars_in_guild:
#         pvp_brackets = get_args(PVP_BRACKETS)
#         for bracket in pvp_brackets:
#             p = await get_pvp_bracket(
#                 char["name"], cc_access_token, bracket, char["realm"]["slug"]
#             )
#             if not p:
#                 continue
#             pp.append(p)
#     # return {"bracket_data": pp}
#     return pp
