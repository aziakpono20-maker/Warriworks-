from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.marketplace.models import ArtisanProfile


class ArtisanProfileApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.artisan = User.objects.create_user(
            username='artisan-profile', email='profile@example.com',
            password='test-pass-123', role='artisan',
        )
        self.profile = ArtisanProfile.objects.create(
            user=self.artisan, display_name='Original Name',
            skill='Plumber', location='Warri', verified=False,
        )

    def test_artisan_can_read_own_profile(self):
        self.client.force_authenticate(self.artisan)
        response = self.client.get('/api/artisans/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['display_name'], 'Original Name')

    def test_artisan_can_update_editable_profile_fields(self):
        self.client.force_authenticate(self.artisan)
        response = self.client.patch('/api/artisans/me/', {
            'display_name': 'Updated Name', 'skill': 'Electrician',
            'location': 'Effurun', 'years_experience': 5,
            'is_available': False,
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.display_name, 'Updated Name')
        self.assertEqual(self.profile.skill, 'Electrician')
        self.assertFalse(self.profile.is_available)
        self.assertFalse(self.profile.verified)

    def test_artisan_cannot_change_verification_state(self):
        self.client.force_authenticate(self.artisan)
        response = self.client.patch('/api/artisans/me/', {
            'verified': True, 'verification_status': 'approved',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.verified)
        self.assertEqual(self.profile.verification_status, 'pending')

    def test_customer_cannot_manage_artisan_profile(self):
        customer = User.objects.create_user(
            username='customer-profile', email='customer@example.com',
            password='test-pass-123', role='customer',
        )
        self.client.force_authenticate(customer)
        response = self.client.get('/api/artisans/me/')
        self.assertEqual(response.status_code, 403)
