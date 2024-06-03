# Collection of endpoints and helpers for the Battle.net API
from typing import Any, Union

import isabot.utils.dictionary as dictionary
from isabot.battlenet.constants import (
    BATTLENET_LOCALE,
    BATTLENET_NAMESPACES,
    BATTLENET_OAUTH_URL,
    BATTLENET_URL,
    GUILD_NAME,
    GUILD_REALM,
)
from isabot.utils.client import http_client


async def get_bnet_endpt(
    url: str,
    token: str,
    namespace: str = "static",
    base_url: str = BATTLENET_URL,
) -> Union[Any, None]:
    """
    Use GET to fetch a protected Battle Net endpoint. Note that `url` will
    append the base url for you, so pass the relative path

    `await get_bnet_endpt(url="/profile/user/wow", ...)`
    """
    try:
        r = await http_client.get(
            url=f"{base_url}{url}",
            headers={
                "Authorization": get_bnet_authorization_header(token),
                "Battlenet-Namespace": get_namespace(namespace),
            },
            params={"locale": BATTLENET_LOCALE},
        )
        return await r.json()
    except Exception as err:
        print("exception:", err, "url:", f"{base_url}{url}")
        return None


def get_bnet_authorization_header(token: str) -> str:
    return token if token.startswith("Bearer ") else f"Bearer {token}"


def get_namespace(namespace_type: str):
    return BATTLENET_NAMESPACES.get(namespace_type.lower(), None)


async def character_mounts(
    token: str, character_name: str, realm_slug: str, namespace: str = "profile"
):
    """Retrieves mounts collected by a character."""
    return await get_bnet_endpt(
        f"/profile/wow/character/{realm_slug}/{character_name.lower()}/collections/mounts",
        token,
        namespace,
    )


async def account_profile_summary(
    token: str, namespace: str = "profile"
) -> Union[Any, None]:
    """Returns a profile summary for an account."""
    return await get_bnet_endpt("/profile/user/wow", token, namespace)


async def account_user_info(token: str, namespace: str = "profile") -> Union[Any, None]:
    """Returns the user information for an account. Contains sub, id, and battletag."""
    return await get_bnet_endpt(
        "/userinfo",
        token,
        namespace,
        base_url=BATTLENET_OAUTH_URL,
    )


# 2-3-24: Not needed for now...
# async def protected_character(
#     token: str,
#     realm_id: int,
#     character_id: int,
#     url: Optional[str],
#     namespace: str = "profile",
# ):
#     try:
#         return await get_bnet_endpt(
#             f"/profile/user/wow/protected-character/{realm_id}-{character_id}",
#             token,
#             namespace,
#         )
#     except Exception:
#         return None


async def account_mounts_collection(
    token: str, namespace: str = "profile"
) -> Union[Any, None]:
    """Retrieves the mounts collected by an account."""
    return await get_bnet_endpt(
        "/profile/user/wow/collections/mounts", token, namespace
    )


async def account_characters(wow_accounts: list[dict]) -> dict:
    """
    Retrieves characters for each WoW account.

    `wow_accounts` must be a list of dictionaries, where each dict contains information about
    a WoW character. This can be obtained from account_profile_summary.
    """
    accounts = {}
    for account in wow_accounts:
        acc_characters = account["characters"]
        for character in acc_characters:
            char_id = character.get("id")

            # Needs a valid character ID in order to proceed
            if not char_id:
                continue

            # Clean data
            playable_class = character.get("playable_class")
            if playable_class:
                playable_class.pop("key", None)

            playable_race = character.get("playable_race")
            if playable_race:
                playable_race.pop("key", None)

            realm = character.get("realm")
            if realm:
                realm.pop("key", None)

            accounts[str(char_id)] = {
                "name": character.get("name"),
                "id": char_id,
                "protected_character": dictionary.safe_nested_get(
                    character, "protected_character", "href"
                ),
                "playable_class": playable_class,
                "playable_race": playable_race,
                "faction": dictionary.safe_nested_get(character, "faction", "name"),
                "level": character.get("level"),
                "realm": realm,
            }
    return accounts


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
