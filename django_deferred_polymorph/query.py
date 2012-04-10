from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType
from django_deferred_polymorph.deferred import deferred_child_obj_factory


class DeferredPolymorphQuerySet(QuerySet):
    def content_type(self, model):
        return self.filter(_poly_ct=ContentType.objects.get_for_model(model))
    
    def iterator(self):
        for instance in super(DeferredPolymorphQuerySet, self).iterator():
            if instance._poly_ct_id:
                child_model = ContentType.objects.get_for_id(instance._poly_ct_id).model_class()
                yield deferred_child_obj_factory(instance, child_model)
            else:
                yield instance

    def delete(self):
        # super(DeferredPolymorphQuerySet, self).delete() seems not to work, as
        # delete() does a _clone(), too. This seems to clone back to
        # DeferredPolymorphQuerySet, so super() gets useless.
        del_qs = self._clone(klass=QuerySet)
        return del_qs.delete()

