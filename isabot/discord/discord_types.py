from enum import IntEnum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel

# class ApplicationCommandPermissionType(IntEnum):
#     """
#     https://discord.com/developers/docs/interactions/application-commands#application-command-permissions-object-application-command-permission-type
#     """

#     ROLE = 1
#     USER = 2
#     CHANNEL = 3


# class Choice(BaseModel):
#     name: str
#     value: str


# class Option(BaseModel):
#     name: str
#     description: str
#     type: Optional[ApplicationCommandPermissionType] = None
#     required: bool
#     choices: Optional[List[Choice]] = None


# class SlashCommandData(BaseModel):
#     """
#     https://discord.com/developers/docs/interactions/application-commands#slash-commands
#     """

#     name: str
#     type: ApplicationCommandPermissionType
#     description: str
#     options: List[Option]


class APIInteractionType(IntEnum):
    """https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-type"""

    ApplicationCommand = 2
    ApplicationCommandAutocomplete = 4
    MessageComponent = 3
    ModalSubmit = 5
    Ping = 1
