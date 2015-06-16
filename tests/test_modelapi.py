from django.test import TestCase

from .models import ChildOfSelfReferencingModel
from .models import SimpleBaseModel
from .models import SimpleDeferredModel
from .models import SelfReferencingBaseModel


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

    def test_delete_self_referencing_base_model(self):
        obj = ChildOfSelfReferencingModel.objects.create()
        obj.self_fk = obj
        obj.save()

        self.assertEqual(SelfReferencingBaseModel.objects.count(), 1)
        self.assertEqual(ChildOfSelfReferencingModel.objects.count(), 1)

        obj.delete()

        self.assertEqual(SelfReferencingBaseModel.objects.count(), 0)
        self.assertEqual(ChildOfSelfReferencingModel.objects.count(), 0)
