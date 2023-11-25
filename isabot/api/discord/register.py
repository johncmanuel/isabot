REGISTER_NAME = "register"
REGISTER_DESC = "Register your BattleNet account"
REGISTER_BNET_NAME = "bnet_name"
REGISTER_BNET_DESC = "Your BattleNet account"

REGISTER = {
    "name": REGISTER_NAME,
    "description": REGISTER_DESC,
    "type": 1,
    "options": [
        {
            "name": REGISTER_BNET_NAME,
            "description": REGISTER_BNET_DESC,
            "type": 3,
            "required": True,
        }
    ],
}


def verify_register_command():
    pass
