# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django_deferred_polymorph.manager import DeferredPolymorphManager
from django.db.models.signals import class_prepared


class DeferredPolymorphBaseModel(models.Model):
    _poly_ct = models.ForeignKey(ContentType, related_name='+', editable=False)
    
    objects = DeferredPolymorphManager()
    base_objects = models.Manager()
    _base_manager = base_objects
    
    def _fill_poly_ct(self):
        if self._poly_ct_id is None:
            self._poly_ct = ContentType.objects.get_for_model(self.__class__)
    
    def save(self, *args, **kwargs):
        self._fill_poly_ct()
        return super(DeferredPolymorphBaseModel, self).save(*args, **kwargs)
    
    def get_real_instance_class(self):
        """ Use this instead of obj._poly_ct, as this call gets cached """
        return ContentType.objects.get_for_id(self._poly_ct_id).model_class()
    
    def get_real_instance(self):
        model = self.get_real_instance_class()
        if self.__class__ is model: # or (self._deferred and self.__class__.__bases__[0] is model):
            return self
        return model._default_manager.get(pk = self.pk)
    
    def delete(self, *args, **kwargs):
        if self._deferred:
            self.get_real_instance().delete(*args, **kwargs)
        else:
            super(DeferredPolymorphBaseModel, self).delete(*args, **kwargs)
    
    class Meta:
        abstract = True


class SubDeferredPolymorphBaseModel(DeferredPolymorphBaseModel):
    """ this class disallows saving of instances of the base (sub) class
    this may be usefull to force having a content type different than the
    base """
    def save(self, *args, **kwargs):
        if self._poly_ct_id is None:
            # not sure about this, it seems like Django kills class.__bases__
            # we use an index-access here anyways
            if self.__class__.__bases__[0] is SubDeferredPolymorphBaseModel:
                raise RuntimeError('instance may not be saved directly, use a subclass')
        return super(SubDeferredPolymorphBaseModel, self).save(*args, **kwargs)
    
    class Meta:
        abstract = True


# Background: Django will use our DeferredPolymorphManager for reverse relations,
# this includes the parent relation of the models (child.parent will result
# in getting an Parent_aDeferred_... class. This is not intended, as we cannot
# access real parents because of this. In addition it will break Django, when it
# comes to deletion of objects (deferred objects just delete the child, again).
# To fix this the solution django_polymorphic implemented is mimiced here. It
# replaces the parent relation accessors, to use Parent.base_objects instead of
# Parent._default_manager. This way we get our vanilla base model back.
def fix_parent_and_child_relation(sender, **kwargs):
    model = sender
    if not issubclass(model, DeferredPolymorphBaseModel):
        return
    for parent, field in model._meta.parents.iteritems():
        if field is None:
            # not sure, what this means
            # seems to happen for deferred classes (and subclasses?)
            continue
        if not issubclass(parent, DeferredPolymorphBaseModel):
            continue
        setattr(model, field.name, property(lambda self: parent.base_objects.get(pk=self.pk)))
        setattr(parent, field.related.var_name, property(lambda self: model.base_objects.get(pk=self.pk)))
class_prepared.connect(fix_parent_and_child_relation)

