from isabot.discord.discord_types import ApplicationCommandOptionType

REGISTER_NAME = "register"
REGISTER_DESC = "Register your BattleNet account"
REGISTER_BNET_NAME = "battle_tag"
REGISTER_BNET_DESC = "Your Battle Tag"

REGISTER = {
    "name": REGISTER_NAME,
    "description": REGISTER_DESC,
    "type": ApplicationCommandOptionType.SubCommand,
    "options": [
        {
            "name": REGISTER_BNET_NAME,
            "description": REGISTER_BNET_DESC,
            "type": ApplicationCommandOptionType.String,
            "required": True,
        }
    ],
}


def verify_register_command():
    pass
