from isabot.battlenet.constants import GUILD_NAME, GUILD_REALM
from isabot.battlenet.helpers import get_bnet_endpt

# async def get_guild(
#     token: str,
#     guild: str = GUILD_NAME,
#     realm: str = GUILD_REALM[0],
#     namespace: str = "profile",
# ):
#     return await get_bnet_endpt(f"/data/wow/guild/{realm}/{guild}", token, namespace)


async def get_guild_roster(
    token: str,
    guild: str = GUILD_NAME,
    realm: str = GUILD_REALM[0],
    namespace: str = "profile",
):
    return await get_bnet_endpt(
        f"/data/wow/guild/{realm}/{guild}/roster", token, namespace
    )
