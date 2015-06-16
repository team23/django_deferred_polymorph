from django.test import TestCase

from .models import SimpleBaseModel
from .models import SimpleDeferredModel


class ModelAPITest(TestCase):
    def test_create(self):
        obj = SimpleDeferredModel.objects.create(
            parent_char_field='Parent Value',
            child_int_field=13)
        retrieved = SimpleDeferredModel.objects.get(pk=obj.pk)
        self.assertEqual(retrieved.parent_char_field, 'Parent Value')
        self.assertEqual(retrieved.child_int_field, 13)

    def test_delete(self):
        obj = SimpleDeferredModel.objects.create(
            parent_char_field='Parent Value',
            child_int_field=13)

        self.assertEqual(SimpleBaseModel.objects.count(), 1)
        self.assertEqual(SimpleDeferredModel.objects.count(), 1)

        obj.delete()

        self.assertEqual(SimpleBaseModel.objects.count(), 0)
        self.assertEqual(SimpleDeferredModel.objects.count(), 0)
