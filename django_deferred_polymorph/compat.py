import django


# We need a way to extract all fields that are not m2m fields and not primary
# key's. In Django 1.8 we use the new Model._meta API.
if django.VERSION < (1, 8):
    def get_local_field_names(model):
        m2m_field_names = set(
            f.attname for f in model._meta._many_to_many()
        )
        return [
            f.attname
            for f in model._meta.fields
            if f.attname not in m2m_field_names and not f.primary_key
        ]
else:
    def get_local_field_names(model):
        m2m_field_names = set(
            f.attname for f in model._meta.get_fields()
            if f.many_to_many and not f.auto_created
        )
        return [
            f.attname
            for f in model._meta.get_fields()
            if (
                hasattr(f, 'attname') and
                f.attname not in m2m_field_names and
                not f.primary_key)
        ]


# We use the appconfig ready method to setup the relation fix. If that is not
# available we need to use the class_prepared signal.
if django.VERSION < (1, 7):
    def fix_parent_and_child_relation_signal_handler(sender, **kwargs):
        from .patch_relations import fix_parent_and_child_relation
        fix_parent_and_child_relation(sender)

    def setup_fix_parent_and_child_relation():
        from django.db.models.signals import class_prepared

        class_prepared.connect(fix_parent_and_child_relation_signal_handler)
else:
    def setup_fix_parent_and_child_relation():
        pass
