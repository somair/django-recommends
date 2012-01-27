from collections import defaultdict
from django.db import models


def model_path(obj):
    return '%s.%s' % (obj._meta.app_label, obj._meta.object_name.lower())


def get_sites(obj):
    from django.contrib.sites.models import Site

    for field in obj._meta.fields:
        if field.rel and field.rel.to == Site:
            return [getattr(obj, field)]
    for field in obj._meta.many_to_many:
        if field.rel and field.rel.to == Site:
            return getattr(obj, field).all()
    return [Site.objects.get_current()]


def get_identifier(obj, site_id):
    """
    Given a Django Model, returns a string identifier in the format
    <app_label>.<model>:<site_id>:<object_id>.
    """
    return "%s:%s:%s" % (model_path(obj), site_id, obj.id)


def resolve_identifier(identifier):
    """
    The opposite of ``get_identifier()``
    """
    from django.contrib.sites.models import Site

    app_module, site_id, object_id = identifier.split(':')
    app_label, model = app_module.split('.')
    site = Site.objects.get(pk=site_id)
    ModelClass = models.get_model(app_label, model)
    model = ModelClass.objects.get(pk=object_id)
    return model, site


def convert_vote_list_to_userprefs(vote_list):
    """
    Return a user-centerd prefernce matrix.

    ``vote_list must be`` composed of (user_id, object_identifier, rating)

    ``object_identifier`` is any string that uniquely identifies the object ie:
    <app_label>.<model>:<object_id>.

    The ``utils.get_identifier`` method is provided as convenience for creating such identifiers.
    """
    prefs = defaultdict(dict)
    for pref in vote_list:
        prefs[pref[0]][pref[1]] = pref[2]
    return prefs


def convert_vote_list_to_itemprefs(vote_list):
    """
    Return a item-centerd prefernce matrix.

    ``vote_list must be`` composed of (user_id, object_identifier, rating)

    ``object_identifier`` is any string that uniquely identifies the object ie:
    <app_label>.<model>:<object_id>.

    The ``utils.get_identifier`` method is provided as convenience for creating such identifiers.
    """
    prefs = defaultdict(dict)
    for pref in vote_list:
        prefs[pref[1]][pref[0]] = pref[2]
    return prefs


def similary_results_to_itemMatch(qs, provider):
    itemMatch = defaultdict(list)
    for i in qs:
        site = i.related_object_site
        item = provider.get_identifier(i.get_object(), site)
        similarity = i.score
        item2 = provider.get_identifier(i.get_related_object(), site)

        itemMatch[item].append((similarity, item2))

    return itemMatch
