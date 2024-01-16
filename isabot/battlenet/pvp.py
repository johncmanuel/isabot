from typing import Literal, get_args

from isabot.battlenet.constants import GUILD_REALM, PVP_BRACKETS
from isabot.battlenet.helpers import get_bnet_endpt


async def get_pvp_summary(character_name: str, token: str, realm: str = GUILD_REALM[0]):
    try:
        return await get_bnet_endpt(
            f"/profile/wow/character/{realm}/{character_name.lower()}/pvp-summary",
            token,
            "profile",
        )
    except Exception:
        return None


async def get_pvp_bracket(
    character_name: str,
    token: str,
    pvp_bracket: PVP_BRACKETS,
    realm: str = GUILD_REALM[0],
):
    try:
        return await get_bnet_endpt(
            f"/profile/wow/character/{realm}/{character_name.lower()}/pvp-bracket/{pvp_bracket}",
            token,
            "profile",
        )
    except Exception:
        return None


async def get_normal_bg_data_from_chars(
    wow_chars_in_guild: dict, cc_access_token: str, user_id: str
) -> dict:
    """Get total wins and loses from each character's battleground statistics"""
    account_bg_total_won = 0
    account_bg_total_lost = 0
    for char_id in wow_chars_in_guild:
        char = wow_chars_in_guild[char_id]
        char_total_won = 0
        char_total_lost = 0
        char_pvp_data = await get_pvp_summary(
            char["name"], cc_access_token, char["realm"]["slug"]
        )
        if not char_pvp_data:
            continue
        for battleground in char_pvp_data.get("pvp_map_statistics", []):
            match_stats = battleground.get("match_statistics")
            if not match_stats:
                continue
            won, lost = match_stats.get("won"), match_stats.get("lost")
            char_total_won += won
            char_total_lost += lost
        account_bg_total_won += char_total_won
        account_bg_total_lost += char_total_lost
    return {
        "user_id": user_id,
        "bg_total_won": account_bg_total_won,
        "bg_total_lost": account_bg_total_lost,
    }


async def pvp_bracket_data(
    wow_chars_in_guild: list[dict],
    cc_access_token: str,
    # pvp_bracket: PVP_BRACKETS,
    user_id: str,
) -> list[dict]:
    pp = []
    for char in wow_chars_in_guild:
        pvp_brackets = get_args(PVP_BRACKETS)
        for bracket in pvp_brackets:
            p = await get_pvp_bracket(
                char["name"], cc_access_token, bracket, char["realm"]["slug"]
            )
            if not p:
                continue
            pp.append(p)
    # return {"bracket_data": pp}
    return pp
