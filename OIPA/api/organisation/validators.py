
def organisation_required_fields(organisation):
    if not organisation.name:
        return False

    if not organisation.publisher:
        return False

    if not organisation.reporting_org:
        return False

    return True

