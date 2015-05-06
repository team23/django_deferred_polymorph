# this is based on Django's internal deferring mechanisms
# the main change is, that all fields are loaded at once, so this
# doesn't issue tons of database queries
from django.db.models.query_utils import DeferredAttribute
from .compat import get_local_field_names


class DeferredManager(object):
    def __init__(self, instance, model, deferred_attrs):
        self.instance = instance
        self.model = model
        self.deferred_attrs = deferred_attrs
        self.is_loaded = False
    
    def load(self):
        if self.is_loaded:
            return
        self.is_loaded = True
        # We use only() instead of values() here because we want the
        # various data coersion methods (to_python(), etc.) to be called
        # here.
        deferred_fields = [f for f in self.model._meta.fields if f.attname in self.deferred_attrs]
        query_fields = [f.name for f in deferred_fields]
        obj = self.model.base_objects.filter(pk=self.instance.pk).only(*query_fields)\
            .using(self.instance._state.db).get()
        for f in deferred_fields:
            self.setattr(f.attname, getattr(obj, f.attname))
    
    # TODO: Recursively support properties?
    def getattr(self, attname):
        if attname in self.model.__dict__:
            prop = self.model.__dict__[attname]
            if hasattr(prop, '__get__'):
                return prop.__get__(self.instance)
        return self.instance.__dict__[attname]
    
    # TODO: Recursively support properties?
    def setattr(self, attname, value):
        if attname in self.model.__dict__:
            prop = self.model.__dict__[attname]
            if hasattr(prop, '__set__'):
                prop.__set__(self.instance, value)
                return
        self.instance.__dict__[attname] = value


class DeferredManagerAccess(object):
    def __init__(self, model, deferred_attrs):
        self.model = model
        self.deferred_attrs = deferred_attrs
    
    def __get__(self, instance, owner):
        try:
            return instance._deferred_manager_obj
        except AttributeError:
            instance._deferred_manager_obj = DeferredManager(instance, self.model, self.deferred_attrs)
            return instance._deferred_manager_obj


# We overwrite evry method of DeferredAttribute, but still need to extend it as
# otherwise isinstance() calls will fail
class LoadAllDeferredAttribute(DeferredAttribute):
    def __init__(self, attr, model):
        self.attr = attr
        self.model = model
    
    def __get__(self, instance, owner):
        """
        Retrieves and caches the value from the datastore on the first lookup.
        Returns the cached value.
        """
        assert instance is not None
        data = instance.__dict__
        if not instance._deferred_manager.is_loaded:
            # We use only() instead of values() here because we want the
            # various data coersion methods (to_python(), etc.) to be called
            # here.
            assert self.attr in instance._deferred_manager.deferred_attrs
            instance._deferred_manager.load()
        return instance._deferred_manager.getattr(self.attr)
    
    def __set__(self, instance, value):
        """
        Deferred loading attributes can be set normally (which means there will
        never be a database lookup involved.
        """
        instance._deferred_manager.setattr(self.attr, value)


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
    # type() requires a non-unicode string.
    name = str(name)

    overrides = dict([(attr, LoadAllDeferredAttribute(attr, model))
            for attr in attrs])
    overrides["Meta"] = Meta
    overrides["__module__"] = model.__module__
    overrides["_deferred"] = True
    overrides["_deferred_manager"] = DeferredManagerAccess(model, attrs)
    return type(name, (model,), overrides)

# The above function is also used to unpickle model instances with deferred
# fields.
deferred_class_factory.__safe_for_unpickling__ = True


# TODO: Cache deferred models!
def deferred_child_class_factory(instance, child_model):
    base_model = instance.__class__
    base_fields = get_local_field_names(base_model)
    child_fields = get_local_field_names(child_model)
    deferred_attrs = [f for f in child_fields if f not in base_fields]
    if not deferred_attrs:
        return child_model
    return deferred_class_factory(child_model, deferred_attrs)


def deferred_child_obj_factory(instance, child_model):
    # if we already got the needed child model instance, just return it
    base_model = instance.__class__
    if issubclass(base_model, child_model):
        return instance
    # create new (deferred) instance
    deferred_model = deferred_child_class_factory(instance, child_model)
    deferred_obj = deferred_model()
    # copy all values to new obj and
    # make sure every primary key is set to 'pk'
    # (this is needed to set FOO_ptr_id on child instances)
    #print base_model._meta.fields
    for f in base_model._meta.fields:
        if f.primary_key:
            # we set both "pk" and f.attname, as this way we get both
            # "..._ptr_id" and id to the right value
            setattr(deferred_obj, f.attname, instance.pk)
            setattr(deferred_obj, 'pk', instance.pk)
        else:
            setattr(deferred_obj, f.attname, getattr(instance, f.attname, None))
        # old version, which does not encount for __get__/__set__ attributes
        #elif f.attname in instance.__dict__:
        #    deferred_obj.__dict__[f.attname] = instance.__dict__[f.attname]
    # clone db state
    # TODO: Clone more state?
    deferred_obj._state.db = instance._state.db
    return deferred_obj

