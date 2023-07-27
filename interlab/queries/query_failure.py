class QueryFailure(Exception):
    """
    Indicates a general failure related to the result of a model query.

    This mostly means that the model failed to supply parseable or othervise proper output,
    or that the subcomputation failed in some other way.

    Note that this should not include cases like network errors (e.g. model unavailability).
    """

    pass


class ParsingFailure(Exception):
    """Specific QueryFailure indicating that the model output could not be parsed."""

    pass
