from lxml import etree


class ElementReference(object):
    """
    http://reference.iatistandard.org/203/activity-standard/elements/
    """
    element = None
    parent_element = None
    data = None

    def __init__(self, parent_element, data, element=None):
        self.parent_element = parent_element
        self.data = data

        if element:
            self.element = element

    def create(self):
        pass


class NarrativeReference(ElementReference):
    """
    http://reference.iatistandard.org/203/activity-standard/iati-activities/iati-activity/title/narrative/
    """
    element = 'narrative'
    text_key = 'text'
    lang_key = 'en'
    language_key = 'language'
    language_code_key = 'code'
    default_language_code = 'en'

    def create(self):
        narrative_element = etree.SubElement(self.parent_element, self.element)
        narrative_element.text = self.data.get(self.text_key)

        language = self.data.get('language')
        if language:
            language_code = language.get(self.language_code_key)
            if language_code not in [self.default_language_code, None]:
                narrative_element.set(
                    '{http://www.w3.org/XML/1998/namespace}lang',
                    language_code
                )


class ElementWithNarrativeReference(ElementReference):
    narrative_element = 'narrative'
    narratives_key = 'narratives'

    def create_narrative(self, parent_element):
        if self.narratives_key in self.data:
            for narrative in self.data.get(self.narratives_key):
                narrative_reference = NarrativeReference(
                    parent_element=parent_element,
                    data=narrative
                )
                narrative_reference.create()

    def create(self):
        self.create_narrative(
            etree.SubElement(self.parent_element, self.element)
        )


class DataElement(object):
    """
    Base of data
    """
    data = None

    def __init__(self, data, key):
        if isinstance(data, dict):
            self.data = data.get(key)
        elif isinstance(data, list):
            self.data = data.get(key)
            self._type = list
        else:
            self.data = str(data)


class DataAttribute(object):
    """
    Data attribute is possible in the dict
    """
    value = None

    def __init__(self, data, key, dict_key):
        value = None

        # if type data is dict then use the dict key
        if dict_key and isinstance(data, dict):
            d_data = data.get(dict_key)
            value = str(d_data.get(key))
        elif not dict_key and isinstance(data, dict):
            value = data.get(key)
        elif not isinstance(data, list):
            value = str(data)

        # Convert the boolean to '1' or '0'
        if isinstance(value, bool):
            value = '1' if value  else '0'

        self.value = value


class AttributeRecord(object):
    """
    Dict of the attribute
    """
    name = str
    dict_key = str
    key = str

    def __init__(self, name,  key, dict_key=None):
        self.name = name
        self.key = key
        self.dict_key = dict_key


class ElementRecord(object):
    """
    Dict of the element
    """
    name = str
    key = str
    # List of AttributeRecord
    attributes = list
    # List of ElementRecord
    children = list
    element_type = None

    def __init__(self, name, key=None, attributes=None, children=None, element_type=None):  # NOQA: E501
        self.name = name
        self.key = key
        self.attributes = attributes
        self.children = children
        self.element_type = element_type


class ElementBase(object):
    """
    Base of the XML element
    """
    element_record = ElementRecord
    # Etree element
    parent_element = None
    # Can be dict, list or just str, int, etc.
    data = None
    element = None

    def __init__(self, element_record, parent_element, data):
        self.element_record = element_record
        self.parent_element = parent_element
        self.data = data

    def create(self):
        if not self.element_record.element_type:
            self.element = etree.SubElement(
                self.parent_element,
                self.element_record.name
            )
        elif self.element_record.element_type == ElementWithNarrativeReference:
            # Narrative element
            ElementWithNarrativeReference(
                parent_element=self.parent_element,
                data=self.data,
                element=self.element_record.name
            ).create()

        # Create attribute
        if self.element_record.attributes:
            for attribute in self.element_record.attributes:
                data_attribute = DataAttribute(
                    data=self.data,
                    key=attribute.key,
                    dict_key=attribute.dict_key
                )
                if data_attribute.value:
                    self.element.set(
                        attribute.name,
                        data_attribute.value
                    )

        # Create children element
        if self.element_record.children:
            for element_record in self.element_record.children:
                data_element = DataElement(
                    data=self.data,
                    key=element_record.key
                )
                if isinstance(data_element.data, list):
                    for data in data_element.data:
                        element_base = ElementBase(
                            element_record=element_record,
                            parent_element=self.element,
                            data=data
                        )
                        element_base.create()
                else:
                    element_base = ElementBase(
                        element_record=element_record,
                        parent_element=self.element,
                        data=data_element.data
                    )
                    element_base.create()
        elif not self.element_record.element_type:
            data_element = DataElement(
                data=self.data,
                key=self.element_record.key
            )
            data = data_element.data

            # Set content on the element without children
            if data:
                self.element.text = data

    def get(self):
        return self.element
