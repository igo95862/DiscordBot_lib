from requests import Response
from json import JSONDecodeError


class DiscordObjectsException(Exception):
    pass


class RestError(DiscordObjectsException):
    pass


class DmForbidden(RestError):
    pass


class MemberNotInGuild(DiscordObjectsException):
    pass


def rest_exception_handler(request: Response):
    try:
        json_dict = request.json()
    except JSONDecodeError:
        raise request.raise_for_status()

    expection_dict = {
        50007: DmForbidden
    }

    exception_to_raise = expection_dict.get(json_dict['code'], RestError(request, json_dict))
    raise exception_to_raise

