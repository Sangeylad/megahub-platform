# backend/onboarding_business/tests/test_invitations_endpoints.py
"""
Tests des endpoints du système onboarding invitations
"""
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
import uuid

from onboarding_invitations.models import UserInvitation
from .factories import (
    UserFactory, CompanyFactory, BrandFactory, 
    CompanySlotsFactory, UserInvitationFactory
)

User = get_user_model()

class OnboardingInvitationsSendEndpointTest(APITestCase):
    """Tests de l'endpoint send-invitation"""
    
    def setUp(self):
        """Setup commun pour tous les tests"""
        self.url = reverse('onboarding_invitations:send_invitation')
        
        # Setup company avec admin
        self.company = CompanyFactory()
        self.admin_user = UserFactory(
            company=self.company, 
            user_type='agency_admin'
        )
        self.brand = BrandFactory(
            company=self.company,
            brand_admin=self.admin_user
        )
        self.brand.users.add(self.admin_user)
        
        # Setup slots avec capacité
        self.slots = CompanySlotsFactory(
            company=self.company,
            users_slots=3,
            current_users_count=1  # Admin seul
        )
        
        self.client.force_authenticate(user=self.admin_user)
    
    def test_send_invitation_requires_authentication(self):
        """
        Test que l'endpoint send-invitation requiert authentication
        
        Given: Aucune authentication
        When: POST /onboarding/invitations/send/
        Then: 401 Unauthorized
        """
        self.client.force_authenticate(user=None)
        
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'brand_id': self.brand.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_send_invitation_requires_brand_admin_permission(self):
        """
        Test que seuls les brand admin peuvent inviter
        
        Given: User brand_member (pas admin)
        When: POST send-invitation
        Then: 403 Forbidden
        """
        member_user = UserFactory(
            company=self.company,
            user_type='brand_member'
        )
        self.brand.users.add(member_user)
        
        self.client.force_authenticate(user=member_user)
        
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'brand_id': self.brand.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_send_invitation_user_without_company_fails(self):
        """
        Test user sans company ne peut pas inviter
        
        Given: User sans company
        When: POST send-invitation
        Then: 400 Bad Request
        """
        user_no_company = UserFactory()
        self.client.force_authenticate(user=user_no_company)
        
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'brand_id': self.brand.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('User sans company', response.data['error'])
    
    def test_send_invitation_invalid_data_returns_400(self):
        """
        Test données invalides retournent 400
        
        Given: Données invalides (email mal formé)
        When: POST send-invitation
        Then: 400 avec détails erreurs
        """
        response = self.client.post(self.url, {
            'email': 'invalid-email',  # Email mal formé
            'brand_id': self.brand.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Données invalides', response.data['error'])
        self.assertIn('details', response.data)
    
    def test_send_invitation_brand_not_found_returns_404(self):
        """
        Test brand inexistante retourne 404
        
        Given: brand_id inexistant
        When: POST send-invitation
        Then: 404 Brand not found
        """
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'brand_id': 99999  # Brand inexistante
        })
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Brand non trouvée', response.data['error'])
    
    def test_send_invitation_brand_different_company_returns_404(self):
        """
        Test brand d'une autre company retourne 404
        
        Given: Brand d'une autre company
        When: POST send-invitation
        Then: 404
        """
        other_company = CompanyFactory()
        other_brand = BrandFactory(company=other_company)
        
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'brand_id': other_brand.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('onboarding_invitations.services.invitation.send_invitation')
    def test_send_invitation_success_creates_invitation(self, mock_send):
        """
        Test création invitation réussie
        
        Given: Données valides et slots disponibles
        When: POST send-invitation
        Then: 201 avec invitation créée
        """
        # Mock retour service
        invitation = UserInvitationFactory(
            company=self.company,
            invited_brand=self.brand,
            invited_by=self.admin_user,
            email='test@example.com'
        )
        mock_send.return_value = invitation
        
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'brand_id': self.brand.id,
            'user_type': 'brand_member',
            'invitation_message': 'Welcome to the team!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        # Vérifier appel service
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        self.assertEqual(call_args[1]['email'], 'test@example.com')
        self.assertEqual(call_args[1]['user_type'], 'brand_member')
    
    @patch('onboarding_invitations.services.invitation.send_invitation')
    def test_send_invitation_slots_full_returns_error(self, mock_send):
        """
        Test invitation échoue si slots pleins
        
        Given: Company avec slots users pleins
        When: POST send-invitation
        Then: 500 avec erreur slots
        """
        # Mock exception validation slots
        from django.core.exceptions import ValidationError
        mock_send.side_effect = ValidationError("Limite utilisateurs atteinte")
        
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'brand_id': self.brand.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
    
    def test_send_invitation_with_custom_message(self):
        """
        Test invitation avec message personnalisé
        
        Given: Message personnalisé fourni
        When: POST send-invitation
        Then: Message inclus dans invitation
        """
        with patch('onboarding_invitations.services.invitation.send_invitation') as mock_send:
            invitation = UserInvitationFactory(
                invitation_message='Custom welcome message'
            )
            mock_send.return_value = invitation
            
            response = self.client.post(self.url, {
                'email': 'test@example.com',
                'brand_id': self.brand.id,
                'invitation_message': 'Custom welcome message'
            })
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Vérifier message passé au service
            call_args = mock_send.call_args
            self.assertEqual(call_args[1]['message'], 'Custom welcome message')

class OnboardingInvitationsAcceptEndpointTest(APITestCase):
    """Tests de l'endpoint accept-invitation"""
    
    def setUp(self):
        """Setup commun"""
        self.url = reverse('onboarding_invitations:accept_invitation')
        
        # Setup invitation valide
        self.company = CompanyFactory()
        self.brand = BrandFactory(company=self.company)
        self.inviter = UserFactory(company=self.company, user_type='brand_admin')
        
        self.invitation = UserInvitationFactory(
            company=self.company,
            invited_brand=self.brand,
            invited_by=self.inviter,
            email='invitee@example.com',
            status='pending'
        )
        
        # User qui va accepter
        self.accepting_user = UserFactory(email='invitee@example.com')
        
        self.client.force_authenticate(user=self.accepting_user)
    
    def test_accept_invitation_requires_authentication(self):
        """Test authentication requise"""
        self.client.force_authenticate(user=None)
        
        response = self.client.post(self.url, {
            'token': str(self.invitation.token)
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_accept_invitation_invalid_token_returns_400(self):
        """
        Test token invalide retourne 400
        
        Given: Token invalide
        When: POST accept-invitation
        Then: 400 avec erreur
        """
        response = self.client.post(self.url, {
            'token': str(uuid.uuid4())  # Token inexistant
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Token invalide', response.data['error'])
    
    def test_accept_invitation_malformed_token_returns_400(self):
        """
        Test token mal formé retourne 400
        
        Given: Token pas un UUID
        When: POST accept-invitation
        Then: 400
        """
        response = self.client.post(self.url, {
            'token': 'not-a-uuid'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('onboarding_invitations.services.invitation.accept_invitation')
    def test_accept_invitation_success_joins_company(self, mock_accept):
        """
        Test acceptation réussie joint la company
        
        Given: Invitation valide et user éligible
        When: POST accept-invitation
        Then: 200 avec infos company/brand
        """
        # Mock retour service
        mock_accept.return_value = self.invitation
        
        # Simuler mise à jour user après acceptation
        self.accepting_user.company = self.company
        self.accepting_user.user_type = 'brand_member'
        self.accepting_user.save()
        
        response = self.client.post(self.url, {
            'token': str(self.invitation.token)
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertEqual(data['company_id'], self.company.id)
        self.assertEqual(data['brand_id'], self.brand.id)
        self.assertEqual(data['user_type'], 'brand_member')
        
        # Vérifier appel service
        mock_accept.assert_called_once_with(
            token=self.invitation.token,
            user=self.accepting_user
        )
    
    @patch('onboarding_invitations.services.invitation.accept_invitation')
    def test_accept_invitation_expired_returns_400(self, mock_accept):
        """
        Test invitation expirée retourne 400
        
        Given: Invitation expirée
        When: POST accept-invitation
        Then: 400 avec erreur
        """
        # Mock exception expiration
        from django.core.exceptions import ValidationError
        mock_accept.side_effect = ValidationError("Invitation expirée ou déjà utilisée")
        
        response = self.client.post(self.url, {
            'token': str(self.invitation.token)
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('onboarding_invitations.services.invitation.accept_invitation')
    def test_accept_invitation_user_already_has_company_fails(self, mock_accept):
        """
        Test user avec company existante ne peut pas accepter
        
        Given: User déjà assigné à une company
        When: POST accept-invitation
        Then: 400 avec erreur
        """
        # Mock exception company existante
        from django.core.exceptions import ValidationError
        mock_accept.side_effect = ValidationError("User déjà assigné à company")
        
        response = self.client.post(self.url, {
            'token': str(self.invitation.token)
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_accept_invitation_email_mismatch_fails(self):
        """
        Test email user != email invitation échoue
        
        Given: User avec email différent de l'invitation
        When: POST accept-invitation
        Then: 400 avec erreur
        """
        wrong_user = UserFactory(email='different@example.com')
        self.client.force_authenticate(user=wrong_user)
        
        with patch('onboarding_invitations.services.invitation.accept_invitation') as mock_accept:
            from django.core.exceptions import ValidationError
            mock_accept.side_effect = ValidationError("Email user ne correspond pas")
            
            response = self.client.post(self.url, {
                'token': str(self.invitation.token)
            })
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class OnboardingInvitationsStatusEndpointTest(APITestCase):
    """Tests de l'endpoint invitation-status (public)"""
    
    def setUp(self):
        """Setup commun"""
        self.company = CompanyFactory()
        self.brand = BrandFactory(company=self.company)
        self.inviter = UserFactory(company=self.company)
        
        self.invitation = UserInvitationFactory(
            company=self.company,
            invited_brand=self.brand,
            invited_by=self.inviter,
            email='test@example.com'
        )
        
        self.url = reverse('onboarding_invitations:invitation_status', 
                          kwargs={'token': self.invitation.token})
    
    def test_invitation_status_no_auth_required(self):
        """
        Test endpoint public (pas d'auth requise)
        
        Given: Aucune authentication
        When: GET invitation-status
        Then: 200 OK
        """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_invitation_status_valid_token_returns_details(self):
        """
        Test token valide retourne détails invitation
        
        Given: Token d'invitation valide
        When: GET invitation-status
        Then: 200 avec détails invitation
        """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        self.assertTrue(data['found'])
        invitation_data = data['invitation']
        self.assertEqual(invitation_data['email'], 'test@example.com')
        self.assertEqual(invitation_data['company_name'], self.company.name)
        self.assertEqual(invitation_data['brand_name'], self.brand.name)
        self.assertTrue(invitation_data['is_valid'])
    
    def test_invitation_status_invalid_token_returns_not_found(self):
        """
        Test token invalide retourne not found
        
        Given: Token inexistant
        When: GET invitation-status
        Then: 200 avec found=False
        """
        invalid_url = reverse('onboarding_invitations:invitation_status',
                             kwargs={'token': uuid.uuid4()})
        
        response = self.client.get(invalid_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        self.assertFalse(data['found'])
        self.assertIn('error', data)
    
    def test_invitation_status_expired_invitation_shows_invalid(self):
        """
        Test invitation expirée montre invalid
        
        Given: Invitation expirée
        When: GET invitation-status
        Then: is_valid = False
        """
        # Rendre invitation expirée
        self.invitation.expires_at = timezone.now() - timedelta(days=1)
        self.invitation.save()
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        self.assertTrue(data['found'])
        self.assertFalse(data['invitation']['is_valid'])

class OnboardingInvitationsListEndpointTest(APITestCase):
    """Tests de l'endpoint list-invitations"""
    
    def setUp(self):
        """Setup commun"""
        self.url = reverse('onboarding_invitations:list_invitations')
        
        self.company = CompanyFactory()
        self.admin_user = UserFactory(
            company=self.company,
            user_type='agency_admin'
        )
        self.brand = BrandFactory(company=self.company)
        self.brand.users.add(self.admin_user)
        
        # Créer plusieurs invitations
        self.invitations = [
            UserInvitationFactory(
                company=self.company,
                invited_brand=self.brand,
                invited_by=self.admin_user,
                email=f'user{i}@example.com'
            )
            for i in range(3)
        ]
        
        self.client.force_authenticate(user=self.admin_user)
    
    def test_list_invitations_requires_authentication(self):
        """Test authentication requise"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_invitations_user_without_company_returns_400(self):
        """Test user sans company"""
        user_no_company = UserFactory()
        self.client.force_authenticate(user=user_no_company)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_invitations_returns_company_invitations(self):
        """
        Test retourne invitations de la company
        
        Given: Company avec plusieurs invitations
        When: GET list-invitations
        Then: Liste complète des invitations
        """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        self.assertEqual(data['total'], 3)
        self.assertEqual(len(data['invitations']), 3)
        
        # Vérifier structure invitation
        invitation_data = data['invitations'][0]
        expected_fields = [
            'id', 'email', 'status', 'user_type',
            'company_name', 'brand_name', 'invited_by_name',
            'expires_at', 'is_valid'
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, invitation_data)
    
    def test_list_invitations_filters_by_status(self):
        """
        Test filtrage par status
        
        Given: Invitations avec différents status
        When: GET list-invitations?status=pending
        Then: Seules invitations pending retournées
        """
        # Marquer une invitation comme acceptée
        self.invitations[0].status = 'accepted'
        self.invitations[0].save()
        
        response = self.client.get(self.url, {'status': 'pending'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Seulement 2 pending
        self.assertEqual(len(data['invitations']), 2)
        for invitation in data['invitations']:
            self.assertEqual(invitation['status'], 'pending')
    
    def test_list_invitations_excludes_other_companies(self):
        """
        Test exclut invitations autres companies
        
        Given: Invitations d'autres companies
        When: GET list-invitations
        Then: Seules invitations de ma company
        """
        # Créer invitation autre company
        other_company = CompanyFactory()
        other_invitation = UserInvitationFactory(company=other_company)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Seules mes invitations
        self.assertEqual(data['total'], 3)
        for invitation in data['invitations']:
            self.assertEqual(invitation['company_name'], self.company.name)

class OnboardingInvitationsWorkflowIntegrationTest(APITestCase):
    """Tests d'intégration workflow complet invitations"""
    
    def setUp(self):
        """Setup pour tests intégration"""
        # Company admin
        self.company = CompanyFactory()
        self.admin = UserFactory(
            company=self.company,
            user_type='agency_admin'
        )
        self.brand = BrandFactory(company=self.company, brand_admin=self.admin)
        self.brand.users.add(self.admin)
        
        # Slots disponibles
        self.slots = CompanySlotsFactory(
            company=self.company,
            users_slots=5,
            current_users_count=1
        )
    
    @patch('onboarding_invitations.services.invitation.send_invitation')
    @patch('onboarding_invitations.services.invitation.accept_invitation')
    def test_complete_invitation_workflow(self, mock_accept, mock_send):
        """
        Test workflow complet d'invitation
        
        Given: Admin avec brand et slots disponibles
        When: Send invitation → Accept invitation
        Then: Nouveau user joint la company/brand
        """
        # 1. Admin envoie invitation
        self.client.force_authenticate(user=self.admin)
        
        invitation = UserInvitationFactory(
            company=self.company,
            invited_brand=self.brand,
            invited_by=self.admin,
            email='newuser@example.com'
        )
        mock_send.return_value = invitation
        
        send_url = reverse('onboarding_invitations:send_invitation')
        response = self.client.post(send_url, {
            'email': 'newuser@example.com',
            'brand_id': self.brand.id,
            'user_type': 'brand_member'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Nouveau user accepte invitation
        new_user = UserFactory(email='newuser@example.com')
        self.client.force_authenticate(user=new_user)
        
        mock_accept.return_value = invitation
        
        # Simuler acceptation réussie
        new_user.company = self.company
        new_user.user_type = 'brand_member'
        new_user.save()
        self.brand.users.add(new_user)
        
        accept_url = reverse('onboarding_invitations:accept_invitation')
        response = self.client.post(accept_url, {
            'token': str(invitation.token)
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Vérifier status final
        status_url = reverse('onboarding_invitations:invitation_status',
                            kwargs={'token': invitation.token})
        response = self.client.get(status_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Admin vérifie liste invitations
        self.client.force_authenticate(user=self.admin)
        list_url = reverse('onboarding_invitations:list_invitations')
        response = self.client.get(list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

@pytest.mark.django_db
class OnboardingInvitationsValidationTest(APITestCase):
    """Tests de validation spécifiques aux invitations"""
    
    def test_validate_slots_endpoint_success(self):
        """
        Test validation slots disponibles
        
        Given: Company avec slots disponibles
        When: POST validate-slots avec emails
        Then: 200 validation OK
        """
        company = CompanyFactory()
        admin = UserFactory(company=company, user_type='agency_admin')
        slots = CompanySlotsFactory(
            company=company,
            users_slots=5,
            current_users_count=1
        )
        
        self.client.force_authenticate(user=admin)
        
        url = reverse('onboarding_invitations:validate_slots')
        response = self.client.post(url, {
            'emails': ['user1@example.com', 'user2@example.com']
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['emails_count'], 2)
    
    def test_validate_slots_endpoint_slots_full_fails(self):
        """
        Test validation échoue si slots pleins
        
        Given: Company avec slots pleins
        When: POST validate-slots
        Then: 400 validation failed
        """
        company = CompanyFactory()
        admin = UserFactory(company=company, user_type='agency_admin')
        slots = CompanySlotsFactory(
            company=company,
            users_slots=2,
            current_users_count=2  # Pleins
        )
        
        self.client.force_authenticate(user=admin)
        
        url = reverse('onboarding_invitations:validate_slots')
        
        with patch('onboarding_invitations.services.validation.validate_invitation_slots') as mock_validate:
            from django.core.exceptions import ValidationError
            mock_validate.side_effect = ValidationError("Limite atteinte")
            
            response = self.client.post(url, {
                'emails': ['user1@example.com']
            })
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)