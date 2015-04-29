# -*- coding: utf-8 -*-
import django
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django_deferred_polymorph.manager import DeferredPolymorphManager


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


from .compat import setup_fix_parent_and_child_relation
setup_fix_parent_and_child_relation()
