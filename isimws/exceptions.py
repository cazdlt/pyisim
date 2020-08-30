class AuthenticationError(Exception):
    pass


class NotFoundError(Exception):
    pass


class PersonNotFoundError(NotFoundError):
    pass


class MultipleFoundError(Exception):
    pass


class ContratoNoEncontradoError(Exception):
    pass


class NotImplementedError(Exception):
    pass


class InvalidOptionError(Exception):
    pass
