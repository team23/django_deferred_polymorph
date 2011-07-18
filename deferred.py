from django.db.models.query_utils import DeferredAttribute

# this is based on Django's internal deferring mechanisms
# the main change is, that all fields are loaded at once, so this
# doesn't issue tons of database queries

class LoadAllDeferredAttribute(DeferredAttribute):
    def __init__(self, attr, model, attrs):
        super(LoadAllDeferredAttribute, self).__init__(attr, model)
        self.all_deferred_fields = attrs
    
    def __get__(self, instance, owner):
        """
        Retrieves and caches the value from the datastore on the first lookup.
        Returns the cached value.
        """
        from django.db.models.fields import FieldDoesNotExist

        assert instance is not None
        cls = self.model_ref()
        data = instance.__dict__
        if data.get(self.field_name, self) is self:
            # We use only() instead of values() here because we want the
            # various data coersion methods (to_python(), etc.) to be called
            # here.
            assert self.field_name in self.all_deferred_fields
            deferred_fields = [f for f in instance._meta.fields if f.attname in self.all_deferred_fields]
            query_fields = [f.name for f in deferred_fields]
            obj = cls._base_manager.filter(pk=instance.pk).only(*query_fields)\
                .using(instance._state.db).get()
            for f in deferred_fields:
                data[f.attname] = getattr(obj, f.attname)
        return data[self.field_name]

# This function is needed because data descriptors must be defined on a class
# object, not an instance, to have any effect.
def deferred_class_factory(model, attrs):
    """
    Returns a class object that is a copy of "model" with the specified "attrs"
    being replaced with DeferredAttribute objects. The "pk_value" ties the
    deferred attributes to a particular instance of the model.
    """
    class Meta:
        pass
    setattr(Meta, "proxy", True)
    setattr(Meta, "app_label", model._meta.app_label)

    # The app_cache wants a unique name for each model, otherwise the new class
    # won't be created (we get an old one back). Therefore, we generate the
    # name using the passed in attrs. It's OK to reuse an old case if the attrs
    # are identical.
    # NAME CHANGED TO AVOID NAME COLLISION WITH DJANGO DEFERRED MODELS
    # ("a" added)
    name = "%s_aDeferred_%s" % (model.__name__, '_'.join(sorted(list(attrs))))

    overrides = dict([(attr, LoadAllDeferredAttribute(attr, model, attrs))
            for attr in attrs])
    overrides["Meta"] = Meta
    overrides["__module__"] = model.__module__
    overrides["_deferred"] = True
    return type(name, (model,), overrides)

# The above function is also used to unpickle model instances with deferred
# fields.
deferred_class_factory.__safe_for_unpickling__ = True

def deferred_child_class_factory(instance, child_model):
    base_model = instance.__class__
    base_m2m_fields = [f.attname for f in base_model._meta._many_to_many()]
    base_fields = [f.attname for f in base_model._meta.fields if f not in base_m2m_fields and not f.primary_key]
    child_m2m_fields = [f.attname for f in child_model._meta._many_to_many()]
    child_fields = [f.attname for f in child_model._meta.fields if f not in child_m2m_fields and not f.primary_key]
    deferred_attrs = [f for f in child_fields if not f in base_fields]
    if not deferred_attrs:
        return child_model
    return deferred_class_factory(child_model, deferred_attrs)

def deferred_child_obj_factory(instance, child_model):
    deferred_model = deferred_child_class_factory(instance, child_model)
    deferred_obj = deferred_model()
    # copy all values to new obj and
    # make sure every primary key is set to 'pk'
    # (this is needed to set FOO_ptr_id on child instances)
    for f in deferred_obj._meta.fields:
        if f.primary_key:
            setattr(deferred_obj, f.attname, instance.pk)
        elif f.attname in instance.__dict__:
            deferred_obj.__dict__[f.attname] = instance.__dict__[f.attname]
    # clone db state
    # TODO: Clone more state?
    deferred_obj._state.db = instance._state.db
    return deferred_obj

