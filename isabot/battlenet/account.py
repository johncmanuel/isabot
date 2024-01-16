from typing import Optional

import isabot.utils.dictionary as dictionary
from isabot.battlenet.constants import BATTLENET_OAUTH_URL
from isabot.battlenet.helpers import get_bnet_endpt


async def account_profile_summary(token: str, namespace: str = "profile"):
    try:
        return await get_bnet_endpt("/profile/user/wow", token, namespace)
    except Exception:
        return None


async def account_user_info(token: str, namespace: str = "profile"):
    # contains "sub", "id", and "battletag" keys
    try:
        return await get_bnet_endpt(
            "/userinfo",
            token,
            namespace,
            base_url=BATTLENET_OAUTH_URL,
        )
    except Exception:
        return None


async def protected_character(
    token: str,
    realm_id: int,
    character_id: int,
    url: Optional[str],
    namespace: str = "profile",
):
    try:
        return await get_bnet_endpt(
            f"/profile/user/wow/protected-character/{realm_id}-{character_id}",
            token,
            namespace,
        )
    except Exception:
        return None


async def account_mounts_collection(token: str, namespace: str = "profile"):
    try:
        return await get_bnet_endpt(
            "/profile/user/wow/collections/mounts", token, namespace
        )
    except Exception:
        return None


async def account_characters(wow_accounts: list[dict]) -> dict:
    """
    Retrieves characters for each WoW account that're located in Shandris or Bronzebeard.

    `wow_accounts` must be a list of dictionaries, where each dict contains information about
    a WoW character
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
