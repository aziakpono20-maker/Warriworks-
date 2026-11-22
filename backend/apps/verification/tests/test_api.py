from django.test import TestCase
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.marketplace.models import ArtisanProfile
from apps.verification.models import ArtisanVerification

class ManualArtisanVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.artisan_user = User.objects.create_user(username='artisan1', email='artisan@example.com', password='test-pass-123', role='artisan')
        self.profile = ArtisanProfile.objects.create(user=self.artisan_user, display_name='Test Artisan', skill='Plumber', location='Warri')
        self.admin_user = User.objects.create_user(username='admin1', email='admin@example.com', password='test-pass-123', role='admin')

    def application_payload(self):
        return {
            'legal_name': 'Test Artisan', 'contact_phone': '+2348000000000',
            'operating_address': 'Warri, Delta State', 'id_type': 'nin',
            'id_last_four': '1234', 'review_method': 'in_person', 'consent_given': True,
        }

    def test_artisan_can_submit_and_status_is_pending(self):
        self.client.force_authenticate(self.artisan_user)
        response = self.client.post('/api/verification/artisan/', self.application_payload(), format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'pending')
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.verified)

    def test_approval_is_blocked_until_all_manual_checks_complete(self):
        item = ArtisanVerification.objects.create(artisan=self.profile, **self.application_payload())
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(f'/api/verification/admin/{item.pk}/approve/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.verified)

    def test_admin_can_complete_checks_and_approve(self):
        item = ArtisanVerification.objects.create(artisan=self.profile, **self.application_payload())
        self.client.force_authenticate(self.admin_user)
        checks = {
            'phone_confirmed': True, 'identity_document_reviewed': True,
            'live_person_id_match_confirmed': True, 'professional_profile_reviewed': True,
            'location_reviewed': True, 'reference_checked': True,
        }
        reviewed = self.client.post(f'/api/verification/admin/{item.pk}/review/', checks, format='json')
        self.assertEqual(reviewed.status_code, 200)
        approved = self.client.post(f'/api/verification/admin/{item.pk}/approve/', {}, format='json')
        self.assertEqual(approved.status_code, 200)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.verified)
        self.assertEqual(self.profile.verification_status, 'approved')

    def test_artisan_cannot_access_admin_queue(self):
        self.client.force_authenticate(self.artisan_user)
        response = self.client.get('/api/verification/admin/')
        self.assertEqual(response.status_code, 403)
