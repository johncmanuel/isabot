from isabot.battlenet.constants import BATTLENET_NAMESPACES, BATTLENET_URL
from isabot.battlenet.helpers import get_bnet_endpt

dummy_token = ""


async def get_guild(guild: str, realm: str, namespace: str = "static"):
    return await get_bnet_endpt(
        f"/data/wow/guild/{realm}/{guild}", dummy_token, namespace
    )
