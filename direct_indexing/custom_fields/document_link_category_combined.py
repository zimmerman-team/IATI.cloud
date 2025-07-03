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
    if not isinstance(data, dict):
        return data

    dl = 'document-link'
    if dl not in data:
        return data

    # Convert single document link to list for consistent processing
    if isinstance(data[dl], dict):
        data[dl] = [data[dl]]
    elif not isinstance(data[dl], list):
        return data  # If it's neither a dict nor a list, we can't process it

    final_field = 'document-link.category-codes-combined'
    data[final_field] = []
    for doc in data[dl]:
        codes = ''
        if 'category' not in doc:
            continue
        if isinstance(doc['category'], dict):
            doc['category'] = [doc['category']]
        elif not isinstance(doc['category'], list):
            continue  # If it's neither a dict nor a list, skip this document
        codes = ",".join(
            category["code"]
            for category in doc.get("category", [])
            if isinstance(category, dict) and "code" in category
        )
        if codes:
            data[final_field].append(codes)
    return data
