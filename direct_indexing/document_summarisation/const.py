HASH = 'dataset.resources.hash'
IDENTIFIER = 'iati-identifier'
FORMAT = 'document-link.format'
DOC_URL = 'document-link.url'
DOC_LINK_FIELDS = [
    DOC_URL, FORMAT, 'document-link.title.narrative',
    'document-link.title.narrative.lang', 'document-link.description.narrative',
    'document-link.description.narrative.lang', 'document-link.category.code',
    'document-link.language.code', 'document-link.document-date.iso-date'
]
DATASET_FIELDS = [
    'dataset.id', 'dataset.metadata_modified', 'dataset.name',
    'dataset.extras.iati_version', HASH, 'dataset.resources.url']
EXTRA_FIELDS = [IDENTIFIER]
ALL_FIELDS = DATASET_FIELDS + DOC_LINK_FIELDS + EXTRA_FIELDS
