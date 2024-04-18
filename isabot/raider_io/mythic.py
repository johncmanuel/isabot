from typing import Optional

from isabot.raider_io.helpers import get_raider_io_endpt
from isabot.utils.dictionary import safe_nested_get


async def get_character_info(
    char_name: str, realm: str, region: str, fields: Optional[str]
):
    """
    Get the mythic plus scores for a character.
    Fields must be a comma-separated string of fields to include in the response.
    https://raider.io/api#/character/getApiV1CharactersProfile
    """
    url = "/characters/profile"
    if not fields:
        return await get_raider_io_endpt(
            url=url,
            region=region,
            realm=realm,
            name=char_name,
        )
    # Clean the passed fields
    fields_cleaned = fields.strip().replace(" ", "")

    return await get_raider_io_endpt(
        url=url,
        region=region,
        realm=realm,
        name=char_name,
        fields=fields_cleaned,
    )


def get_overall_mythic_plus_score(raider_io_character_res: dict) -> float:
    """
    Get the overall mythic plus score for a character.
    """
    scores = raider_io_character_res.get("mythic_plus_scores_by_season", [])
    if not scores:
        return 0
    return safe_nested_get(scores[0], "scores", "all", default=0)  # type: ignore


def get_current_season(raider_io_character_res: dict) -> str:
    """
    Get the current season.
    """
    scores = raider_io_character_res.get("mythic_plus_scores_by_season", [])
    if not scores:
        return ""
    return scores[0].get("season", "")  # type: ignore
