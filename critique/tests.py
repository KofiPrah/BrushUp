from django.test import TestCase
from django.contrib.auth.models import User
from .models import ArtWork

# Create your tests here.
class ArtWorkModelTest(TestCase):
    def setUp(self):
        self.artwork = ArtWork.objects.create(
            title="Test Artwork",
            description="This is a test artwork description."
        )

    def test_artwork_creation(self):
        self.assertTrue(isinstance(self.artwork, ArtWork))
        self.assertEqual(self.artwork.__str__(), self.artwork.title)


