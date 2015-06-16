from django.db import models
from django.test import TestCase

from django_deferred_polymorph.manager import DeferredPolymorphManager
from .models import SimpleDeferredModel


class ManagerTests(TestCase):
    def test_default_manager_is_deferred_manager(self):
        self.assertTrue(
            SimpleDeferredModel._default_manager is SimpleDeferredModel.objects)
        self.assertTrue(
            SimpleDeferredModel._default_manager.__class__ is DeferredPolymorphManager)

    def test_base_manager_is_django_default_manager(self):
        self.assertTrue(
            SimpleDeferredModel._base_manager.__class__ is models.Manager)
