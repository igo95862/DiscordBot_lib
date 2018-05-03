import typing
from json import JSONDecodeError

from requests import Response


class DiscordObjectsException(Exception):
    pass


class RestError(DiscordObjectsException):
    pass


class UnknownAccount(RestError):
    code = 10001
    pass


class UnknownApplication(RestError):
    code = 10002
    pass


class UnknownChannel(RestError):
    code = 10003
    pass


class UnknownGuild(RestError):
    code = 10004
    pass


class UnknownIntegration(RestError):
    code = 10005
    pass


class UnknownInvite(RestError):
    code = 10006
    pass


class UnknownMember(RestError):
    code = 10006
    pass


class UnknownMessage(RestError):
    code = 10008
    pass


class UnknownOverwrite(RestError):
    code = 10009
    pass


class UnknownProvider(RestError):
    code = 10010
    pass


class UnknownRole(RestError):
    code = 10011
    pass


class UnknownToken(RestError):
    code = 10012
    pass


class UnknownUser(RestError):
    code = 10013
    pass


class UnknownEmoji(RestError):
    code = 10014
    pass


class BotsCannotUse(RestError):
    code = 20001
    pass


class OnlyBotsCanUse(RestError):
    code = 20002
    pass


class MaxGuilds(RestError):
    code = 30001
    pass


class MaxFriends(RestError):
    code = 30002
    pass


class MaxPins(RestError):
    code = 30003
    pass


class MaxGuildRoles(RestError):
    code = 30005
    pass


class MaxReactions(RestError):
    code = 30010
    pass


class MaxGuildChannels(RestError):
    code = 30013
    pass


class Unauthorized(RestError):
    code = 40001
    pass


class MissingAccess(RestError):
    code = 50001
    pass


class InvalidAccountType(RestError):
    code = 50002
    pass


class CannotUseThisInDm(RestError):
    code = 50003
    pass


class WidgetDisabled(RestError):
    code = 50004
    pass


class CannotEditAnotherUsersMessage(RestError):
    code = 50005
    pass


class CannotSendEmptyMessage(RestError):
    code = 50006
    pass


class CannotSendThisUserMessage(RestError):
    code = 50007
    pass


class CannotSendMessageToVoiceChannel(RestError):
    code = 50008
    pass


class ChannelVerificationTooHigh(RestError):
    code = 50009
    pass


class O2AuthDoesNotHaveBot(RestError):
    code = 50010
    pass


class O2AuthLimitReached(RestError):
    code = 50011
    pass


class InvalidOAuthState(RestError):
    code = 50012
    pass


class MissingPermissions(RestError):
    code = 50013
    pass


class InvalidAuthenticationToken(RestError):
    code = 50014
    pass


class NoteIsTooLong(RestError):
    code = 50015
    pass


class IncorrectMessageNumberToDelete(RestError):
    code = 50016
    pass


class PinMessageChannelMismatch(RestError):
    code = 50019
    pass


class CannotUseThisOnSystemMessage(RestError):
    code = 50021
    pass


class MessageTooOldForBulkDelete(RestError):
    code = 50034
    pass


class InvalidBodyForm(RestError):
    code = 50035
    pass


class BotNotInGuildInviteAcceptedFrom(RestError):
    code = 50036
    pass


class InvalidApiVersion(RestError):
    code = 50041
    pass


class ReactionBlocked(RestError):
    code = 90001
    pass


_json_errors = [UnknownAccount, UnknownApplication, UnknownChannel, UnknownGuild, UnknownIntegration, UnknownInvite,
                UnknownInvite, UnknownMember, UnknownMessage, UnknownOverwrite, UnknownProvider, UnknownRole,
                UnknownToken, UnknownUser, UnknownEmoji,
                BotsCannotUse, OnlyBotsCanUse,
                MaxGuilds, MaxFriends, MaxPins, MaxGuildRoles, MaxReactions, MaxGuildChannels,
                Unauthorized, MissingAccess, InvalidAccountType, CannotUseThisInDm, WidgetDisabled,
                CannotEditAnotherUsersMessage, CannotSendEmptyMessage, CannotSendThisUserMessage,
                CannotSendMessageToVoiceChannel, ChannelVerificationTooHigh, O2AuthDoesNotHaveBot,
                O2AuthLimitReached, InvalidOAuthState, MissingPermissions, InvalidAuthenticationToken,
                NoteIsTooLong, IncorrectMessageNumberToDelete, PinMessageChannelMismatch,
                CannotUseThisOnSystemMessage, MessageTooOldForBulkDelete, InvalidBodyForm,
                BotNotInGuildInviteAcceptedFrom, InvalidApiVersion,
                ReactionBlocked
                ]

json_exceptions_map: typing.Dict[int, RestError] = {x.code: x for x in _json_errors}


class MemberNotInGuild(DiscordObjectsException):
    pass


def rest_exception_handler(request: Response):
    try:
        json_dict = request.json()
    except JSONDecodeError:
        raise request.raise_for_status()

    exception_to_raise = json_exceptions_map.get(json_dict['code'], RestError(request, json_dict))
    raise exception_to_raise
