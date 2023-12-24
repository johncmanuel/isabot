from isabot.battlenet.constants import BATTLENET_OAUTH_URL, GUILD_REALM
from isabot.battlenet.helpers import get_bnet_endpt

dummy_token = ""


async def account_profile_summary(namespace: str = "profile"):
    return await get_bnet_endpt("/profile/user/wow", dummy_token, namespace)


async def account_user_info(namespace: str = "profile"):
    # contains "sub", "id", and "battletag" keys
    return await get_bnet_endpt(
        "/userinfo",
        dummy_token,
        namespace_type=namespace,
        base_url=BATTLENET_OAUTH_URL,
    )


async def protected_character(namespace: str = "profile"):
    return await get_bnet_endpt(
        "/profile/user/wow/protected-character/1364-102219865",
        dummy_token,
        namespace,
    )


async def account_mounts_collection(namespace: str = "profile"):
    return await get_bnet_endpt(
        "/profile/user/wow/collections/mounts", dummy_token, namespace
    )


async def account_characters(wow_accounts: list[dict]) -> list[dict]:
    """
    Retrieves characters for each WoW account that're located in Shandris or Bronzebeard.

    `wow_accounts` should originate from account profile summary response, under the key: "wow_accounts"
    """
    accounts = []
    for account in wow_accounts:
        acc_characters = account["characters"]
        for character in acc_characters:
            # Profile summary (from wow_accounts) doesn't reveal a character's guild,
            # so add the character if they're in the same realm as the guild.
            if character["realm"]["slug"] in GUILD_REALM:
                tmp = {}
                tmp["name"] = character["name"]
                tmp["id"] = character["id"]
                tmp["protected_character"] = character["protected_character"]
                tmp["class"] = character["playable_class"]
                tmp["race"] = character["playable_race"]
                tmp["faction"] = character["faction"]["name"]
                tmp["level"] = character["level"]
                tmp["realm"] = character["realm"]
                accounts.append(tmp)
    return accounts
