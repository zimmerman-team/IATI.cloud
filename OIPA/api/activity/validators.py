

def activity_required_fields(activity):
    if not activity.title:
        return False

    if not activity.publisher:
        return False

    if not activity.publisher.organisation:
        return False

    if not len(activity.title.narratives.all()) > 0:
        return False

    if not len(activity.description_set.all()) > 0:
        return False

    if not activity.activity_status:
        return False

    if not len(activity.activitydate_set.all()) > 0:
        return False

    if not len(activity.participating_organisations.all()) > 0:
        return False

    return True
