from django.test import TestCase
from django.contrib.auth.models import User
from .models import ArtWork, Review

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

class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.artwork = ArtWork.objects.create(
            title="Test Artwork",
            description="This is a test artwork description."
        )
        self.review = Review.objects.create(
            artwork=self.artwork,
            reviewer=self.user,
            content="This is a test review.",
            rating=4
        )

    def test_review_creation(self):
        self.assertTrue(isinstance(self.review, Review))
        self.assertEqual(
            self.review.__str__(),
            f"Review for {self.artwork.title} by {self.user.username}"
        )
