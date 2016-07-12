class ParserError(Exception):
    def __init__(self, model, field, msg):
        """
        This error indicates there's an OIPA

        field: the field that is required
        msg: explanation why
        """
        self.model = model
        self.field = field
        self.message = msg

    def __str__(self):
        return repr(self.field)


class RequiredFieldError(Exception):
    def __init__(self, model, field, msg):
        """
        This error 

        field: the field that is required
        msg: explanation why
        """
        self.model = model
        self.field = field
        self.message = msg

    def __str__(self):
        return repr(self.field)


class EmptyFieldError(Exception):
    def __init__(self, model, field, msg):
        """
        This error 

        field: the field that is required
        msg: explanation why
        """
        self.model = model
        self.field = field
        self.message = msg

    def __str__(self):
        return repr(self.field)


class ValidationError(Exception):
    def __init__(self, model, field, msg, iati_id=None):
        """


        field: the field that is validated
        msg: explanation what went wrong
        """
        self.model = model
        self.field = field
        self.message = msg
        self.iati_id = iati_id

    def __str__(self):
        return repr(self.field)


class IgnoredVocabularyError(Exception):
    def __init__(self, model, field, msg):
        """
        To get a clear view of all vocabularies OIPA does not support yet
        """
        self.model = model
        self.field = field
        self.message = msg

    def __str__(self):
        return repr(self.field)


class NoUpdateRequired(Exception):
    def __init__(self, field, msg):
        """
        field: the field that is validated
        msg: explanation what went wrong
        """
    def __str__(self):
        return 'Current version of activity exists'

