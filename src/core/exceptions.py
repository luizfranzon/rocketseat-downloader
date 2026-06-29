class RocketseatError(Exception):
    pass


class AuthenticationError(RocketseatError):
    pass


class ApiError(RocketseatError):
    pass


class DownloadError(RocketseatError):
    pass
