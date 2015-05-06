from django.db import models
from django_deferred_polymorph.query import DeferredPolymorphQuerySet


class DeferredPolymorphManager(models.Manager):
    use_for_related_fields = True

    def content_type(self, model):
        return self.get_queryset().content_type(model)

    def get_queryset(self):
        return super(DeferredPolymorphManager, self).get_queryset()._clone(klass=DeferredPolymorphQuerySet)
