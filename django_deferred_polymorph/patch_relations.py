# Background: Django will use our DeferredPolymorphManager for reverse relations,
# this includes the parent relation of the models (child.parent will result
# in getting an Parent_aDeferred_... class. This is not intended, as we cannot
# access real parents because of this. In addition it will break Django, when it
# comes to deletion of objects (deferred objects just delete the child, again).
# To fix this the solution django_polymorphic implemented is mimiced here. It
# replaces the parent relation accessors, to use Parent.base_objects instead of
# Parent._default_manager. This way we get our vanilla base model back.
def fix_parent_and_child_relation(model):
    from .models import DeferredPolymorphBaseModel

    if not issubclass(model, DeferredPolymorphBaseModel):
        return
    for parent, field in model._meta.parents.items():
        if field is None:
            # not sure, what this means
            # seems to happen for deferred classes (and subclasses?)
            continue
        if not issubclass(parent, DeferredPolymorphBaseModel):
            continue
        setattr(model, field.name, property(lambda self: parent.base_objects.get(pk=self.pk)))
        setattr(parent, field.related.get_accessor_name(), property(lambda self: model.base_objects.get(pk=self.pk)))
