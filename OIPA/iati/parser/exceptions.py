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
    def __init__(self, model, field,
                 msg="required attribute/element missing", apiField=None):
        """
        This error

        field: the field that is required
        msg: explanation why
        """
        self.model = model
        self.field = field
        if not apiField:
            self.apiField = field
        else:
            self.apiField = apiField
        self.message = msg

    def __str__(self):
        return repr(self.field)


class FieldValidationError(Exception):
    def __init__(self, model, field, msg="Failed to validate a field",
                 apiField=None, iati_id=None, variable=None):
        """
        field: the field that is validated
        msg: explanation what went wrong
        """

        self.model = model
        self.field = field
        self.message = msg
        self.iati_id = iati_id
        self.variable = variable

        if not apiField:
            self.apiField = field
        else:
            self.apiField = apiField

    def __str__(self):
        return repr(self.field)


class ValidationError(Exception):
    def __init__(self, model, msg, iati_id=None, variable=None):
        """
        field: the field that is validated
        msg: explanation what went wrong
        """
        self.model = model
        self.message = msg
        self.iati_id = iati_id
        self.variable = variable

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
