from isabot.battlenet.helpers import get_bnet_endpt


async def character_mounts(
    token: str, character_name: str, realm_slug: str, namespace: str = "profile"
):
    try:
        return await get_bnet_endpt(
            f"/profile/wow/character/{realm_slug}/{character_name.lower()}/collections/mounts",
            token,
            namespace,
        )
    except Exception:
        return None
