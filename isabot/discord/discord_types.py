from enum import IntEnum
from typing import Optional

from pydantic import BaseModel

# from typing import Dict, List, Literal, Optional


""" These types may either be replaced by a library that implements typings for Discord's API or be further expanded upon. """
""" TODO: Work more on Discord types. """
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


class APIInteractionResponseType(IntEnum):
    """https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object-interaction-callback-type"""

    Pong = 1
    ChannelMessageWithSource = 4
    DeferredChannelMessageWithSource = 5
    DeferredUpdateMessage = 6
    UpdateMessage = 7
    ApplicationCommandAutocompleteResult = 8
    Modal = 9


class ApplicationCommandOptionType(IntEnum):
    """https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-type"""

    SubCommand = 1
    SubCommandGroup = 2
    String = 3
    Integer = 4
    Boolean = 5
    User = 6
    Channel = 7
    Role = 8
    Mentionable = 9
    Number = 10
    Attachment = 11


class APIInteractionResponseFlags(IntEnum):
    """https://discord.com/developers/docs/resources/channel#message-object-message-flags"""

    Ephemeral = 1 << 6


class EmbedColorCodes(IntEnum):
    """
    Will only cherry-pick the colors that are needed.
    https://discordpy.readthedocs.io/en/latest/api.html#colour
    """

    DARK_GREEN = 0x1F8B4C
    DARK_ORANGE = 0xA84300  # The closest to brown we can get... :(
    DARKER_GRAY = 0x546E7A


class EmbedField(BaseModel):
    """https://discord.com/developers/docs/resources/channel#embed-object-embed-structure"""

    name: str
    value: str
    inline: Optional[bool] = False


class Embed(BaseModel):
    """https://discord.com/developers/docs/resources/channel#embed-object-embed-structure"""

    title: str
    description: str
    lb_type: str
    fields: Optional[list[EmbedField]] = []
    auth_url: str
    scores: str
    start_date: str
    color: Optional[int] = EmbedColorCodes.DARKER_GRAY
