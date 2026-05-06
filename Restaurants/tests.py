from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from Accounts.models import Profile
from Core.models import Location, Restaurant
from Restaurants.models import ReviewSystem


class ReviewSystemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="poyraz", password="testpass123")
        self.profile = Profile.objects.create(user=self.user, name="Poyraz")
        self.other_user = User.objects.create_user(username="pyb2", password="testpass123")
        self.other_profile = Profile.objects.create(user=self.other_user, name="PyB2")
        self.location = Location.objects.create(
            city="Istanbul",
            district="Kadikoy",
            area="Moda",
        )
        self.restaurant = Restaurant.objects.create(
            name="Deneme Restoran",
            description="Aciklama",
            location=self.location,
        )

    def test_user_can_only_create_one_review_per_restaurant(self):
        self.client.login(username="poyraz", password="testpass123")
        url = reverse("add_review", args=[self.restaurant.id])

        response_one = self.client.post(
            url,
            {"title": "Ilk", "review": "Guzeldi", "rating": 4},
        )
        response_two = self.client.post(
            url,
            {"title": "Ikinci", "review": "Tekrar", "rating": 5},
        )

        self.assertRedirects(response_one, reverse("restaurant_detail", args=[self.restaurant.id]))
        self.assertRedirects(response_two, reverse("restaurant_detail", args=[self.restaurant.id]))
        self.assertEqual(
            ReviewSystem.objects.filter(
                restaurant=self.restaurant,
                user=self.profile,
            ).count(),
            1,
        )

    def test_user_can_delete_own_review(self):
        review = ReviewSystem.objects.create(
            title="Baslik",
            review="Yorum",
            rating=4,
            restaurant=self.restaurant,
            user=self.profile,
        )
        self.client.login(username="poyraz", password="testpass123")

        response = self.client.post(reverse("delete_review", args=[review.id]))

        self.assertRedirects(response, reverse("restaurant_detail", args=[self.restaurant.id]))
        self.assertFalse(ReviewSystem.objects.filter(id=review.id).exists())
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.rating, 0)

    def test_user_can_edit_own_review(self):
        review = ReviewSystem.objects.create(
            title="Old title",
            review="Old review",
            rating=3,
            restaurant=self.restaurant,
            user=self.profile,
        )
        self.client.login(username="poyraz", password="testpass123")

        response = self.client.post(
            reverse("edit_review", args=[review.id]),
            {"title": "New title", "review": "New review", "rating": 5},
        )

        review.refresh_from_db()
        self.restaurant.refresh_from_db()
        self.assertRedirects(response, reverse("restaurant_detail", args=[self.restaurant.id]))
        self.assertEqual(review.title, "New title")
        self.assertEqual(review.review, "New review")
        self.assertEqual(review.rating, 5)
        self.assertEqual(self.restaurant.rating, 5.0)

    def test_user_cannot_delete_someone_elses_review(self):
        review = ReviewSystem.objects.create(
            title="Baslik",
            review="Yorum",
            rating=4,
            restaurant=self.restaurant,
            user=self.other_profile,
        )
        self.client.login(username="poyraz", password="testpass123")

        response = self.client.post(reverse("delete_review", args=[review.id]))

        self.assertRedirects(response, reverse("restaurant_detail", args=[self.restaurant.id]))
        self.assertTrue(ReviewSystem.objects.filter(id=review.id).exists())

    def test_restaurant_rating_updates_to_average_of_reviews(self):
        ReviewSystem.objects.create(
            title="First",
            review="Nice",
            rating=4,
            restaurant=self.restaurant,
            user=self.profile,
        )
        ReviewSystem.objects.create(
            title="Second",
            review="Great",
            rating=5,
            restaurant=self.restaurant,
            user=self.other_profile,
        )

        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.rating, 4.5)

    def test_restaurants_page_can_filter_by_price_range(self):
        affordable_restaurant = Restaurant.objects.create(
            name="Uygun Restoran",
            description="Butce dostu",
            location=self.location,
            price_range=Restaurant.PRICE_BUDGET,
        )
        premium_restaurant = Restaurant.objects.create(
            name="Pahali Restoran",
            description="Daha premium",
            location=self.location,
            price_range=Restaurant.PRICE_EXPENSIVE,
        )

        response = self.client.get(
            reverse("restaurants"),
            {"price_range": Restaurant.PRICE_BUDGET},
        )

        page_items = list(response.context["page_obj"])
        self.assertIn(affordable_restaurant, page_items)
        self.assertNotIn(premium_restaurant, page_items)
        self.assertNotIn(self.restaurant, page_items)
