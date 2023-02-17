def document_link_category_combined(data):
    """
    Requested for FCDO by FCDO: 
    For each document-link, a document can have multiple categories.
    For each document-link in an activity, provide a combined list of category codes.

    document-link is 0..*
    document-link/category is 1..*
    document-link/category/@code is 1..1

    :param data: reference to the activity in the data
    """
    dl = 'document-link'
    if dl not in data:
        return data

    if type(data[dl]) is dict:
        data[dl] = [data[dl]]

    final_field = 'document-link.category-codes-combined'
    data[final_field] = []
    for doc in data[dl]:
        codes = ''
        if type(doc['category']) is dict:
            doc['category'] = [doc['category']]
        for category in doc['category']:
            if codes != '':
                codes += ','
            codes += category["code"]
        data[final_field].append(codes)
    return data
