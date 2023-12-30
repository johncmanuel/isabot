from isabot.battlenet.constants import GUILD_REALM
from isabot.battlenet.helpers import get_bnet_endpt


async def get_pvp_summary(character_name: str, token: str, realm: str = GUILD_REALM[0]):
    return await get_bnet_endpt(
        f"/profile/wow/character/{realm}/{character_name.lower()}/pvp-summary",
        token,
        "profile",
    )
