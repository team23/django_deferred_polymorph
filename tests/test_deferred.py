from django.test import TestCase


class DeferredTest(TestCase):
    def test_deferred(self):
        self.assertEqual(1 + 1, 2)
