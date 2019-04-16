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
