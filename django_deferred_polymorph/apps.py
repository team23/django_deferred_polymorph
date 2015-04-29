from django.apps import AppConfig
from django.apps import apps


class DeferredPolymorphConfig(AppConfig):
    name = 'django_deferred_polymorph'
    verbose_name = 'django_deferred_polymorph'

    def ready(self):
        from .patch_relations import fix_parent_and_child_relation
        for model in apps.get_models():
            fix_parent_and_child_relation(model)
