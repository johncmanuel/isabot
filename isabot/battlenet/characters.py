from isabot.battlenet.helpers import get_bnet_endpt


async def character_mounts(
    token: str, character_name: str, realm_slug: str, namespace: str = "profile"
):
    """Retrieves mounts collected by a character."""
    return await get_bnet_endpt(
        f"/profile/wow/character/{realm_slug}/{character_name.lower()}/collections/mounts",
        token,
        namespace,
    )
