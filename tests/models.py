from django.db import models

from django_deferred_polymorph.models import SubDeferredPolymorphBaseModel


class SimpleBaseModel(SubDeferredPolymorphBaseModel):
    parent_char_field = models.CharField(max_length=50, default='')


class SimpleDeferredModel(SimpleBaseModel):
    child_int_field = models.IntegerField(default=0)


class SelfReferencingBaseModel(SubDeferredPolymorphBaseModel):
    self_fk = models.ForeignKey('self', null=True, blank=True,
                                on_delete=models.CASCADE)


class ChildOfSelfReferencingModel(SelfReferencingBaseModel):
    child_int_field = models.IntegerField(default=0)
