from __future__ import unicode_literals


# Create your models here.
from django.contrib.auth.models import Group
from django.core.cache import cache


def trim(text, trim_size_min=250, trim_size_max=400, trim_size_hard=400, splitters=[".", ",", " "]):
    if len(text) < trim_size_min:
        return text
    for splitter in splitters:
        i = text.find(splitter, trim_size_min, trim_size_max)
        if i > 0:
            return text[:i] + " (...)"
    if len(text) < trim_size_hard:
        return text
    return text[: trim_size_hard] + " (...)"


class ObjectGrantedContextualized:
    def __init__(self, o, user):
        self.o = o
        self.user = user
        self.granted = self.user.is_superuser or self.o.owner == self.user
        self.delete_perm = o.__module__[0: o.__module__.index('.') + 1] + 'delete_' + o.__class__.__name__.lower()
        self.change_perm = o.__module__[0: o.__module__.index('.') + 1] + 'change_' + o.__class__.__name__.lower()
        try:
            self.class_for_link = o.__class__.granted.through
        except AttributeError:
            self.class_for_link = None

    def can_see(self):
        return self.user.is_superuser or self.o.owner == self.user or self.class_for_link is not None and (
            self.class_for_link.objects.filter(group__in=get_public_groups(), object=self.o).count() > 0 or
            self.user.groups.count() > 0 and
            self.class_for_link.objects.filter(group__in=self.user.groups.all(), object=self.o).count() > 0)

    def can_delete(self):
        return self.user.is_superuser or self.o.owner == self.user and self.user.has_perm(self.delete_perm)

    def can_edit(self):
        return (
            self.user.is_superuser or
            self.user.has_perm(self.change_perm) and (
                self.o.owner == self.user or
                hasattr(self.o, 'editors') and self.user in self.o.editors.all() or
                self.class_for_link is not None and (
                    self.class_for_link.objects.filter(group__in=get_public_groups(),
                                                       object=self.o,
                                                       can_also_edit=True).exists() or
                    self.class_for_link.objects.filter(group__in=self.user.groups.all(),
                                                       object=self.o,
                                                       can_also_edit=True).exists())
            )
        )

    def __unicode__(self):
        return self.o.__unicode__()


def get_public_group():
    return get_group_with_cache(group_name="Public", fcn_name="get_public_group")


def get_group_publish_request():
    return get_group_with_cache(group_name="Demande de publication", fcn_name="get_group_publish_request")


def get_group_unpublish_request():
    return get_group_with_cache(group_name="Demande de de-publication", fcn_name="get_group_unpublish_request")


def get_group_with_cache(group_name, fcn_name):
    pk = cache.get(fcn_name)
    if pk is None:
        pk = Group.objects.get_or_create(name=group_name)[0].pk
        cache.set(fcn_name, pk)
    return Group.objects.get(pk=pk)


def get_cloud_user_group():
    return get_group_with_cache(group_name="CloudUser", fcn_name="get_cloud_user_group")


def get_app_creator_group():
    return get_group_with_cache(group_name="AppCreator", fcn_name="get_app_creator_group")


def get_public_groups():
    return [get_public_group(), ]
