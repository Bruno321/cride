"""invitation test"""
# Django
from django.test import TestCase

# Model
from cride.circles.models.memebership import Membership
from cride.circles.models import Invitation, Circle
from cride.users.models import User, Profile
from rest_framework.authtoken.models import Token

# Django REST framework
from rest_framework.test import APITestCase
from rest_framework import status


class InvitationsManagerTestCase(TestCase):
    """invitations manager test case"""

    def setUp(self):
        """Test case setup"""
        self.user = User.objects.create(
            first_name='Pablo',
            last_name='Trinidad',
            email='pablotrinidad@ciencias.unam.mx',
            username='pablotrinidad',
            password='admin123'
        )
        self.circle = Circle.objects.create(
            name='Facultad de ciencias',
            slug_name='fciencias',
            about='Grupo oficial de ciencias',
            verified=True
        )

    def test_code_generation(self):
        """random codes should be generated automatically"""
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle
        )
        self.assertIsNotNone(invitation.code)

    def test_code_usage(self):
        """if a code is given, theres no need to create a new one"""
        code = 'holamundo'
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )
        self.assertEqual(invitation.code,code)

    def test_code_generation_if_duplicated(self):
        """if given code is not unique new one must be generated"""
        code = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
        ).code

        # create another ivnitation with the past code
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )

        self.assertNotEqual(code,invitation.code)


class MemberInvitationsAPITestCase(APITestCase):
    """Member invitation API test case."""

    def setUp(self):
        """Test case setup."""
        self.user = User.objects.create(
            first_name='Pablo',
            last_name='Trinidad',
            email='pablotrinidad@ciencias.unam.mx',
            username='pablotrinidad',
            password='admin123'
        )
        self.profile = Profile.objects.create(user=self.user)
        self.circle = Circle.objects.create(
            name='Facultad de Ciencias',
            slug_name='fciencias',
            about='Grupo oficial de la Facultad de Ciencias de la UNAM',
            verified=True
        )
        self.membership = Membership.objects.create(
            user=self.user,
            profile=self.profile,
            circle=self.circle,
            remaining_invitations=10
        )

        # Auth
        self.token = Token.objects.create(user=self.user).key
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.token))

        # URL
        self.url = '/circles/{}/members/{}/invitations/'.format(
            self.circle.slug_name,
            self.user.username
        )

    def test_response_success(self):
        """Verify request succeed."""
        request = self.client.get(self.url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_invitation_creation(self):
        """Verify invitation are generated if none exist previously."""
        # Invitations in DB must be 0
        self.assertEqual(Invitation.objects.count(), 0)

        # Call member invitations URL
        request = self.client.get(self.url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        # Verify new invitations were created
        invitations = Invitation.objects.filter(issued_by=self.user)
        self.assertEqual(invitations.count(), self.membership.remaining_invitations)
        for invitation in invitations:
            self.assertIn(invitation.code, request.data['invitations'])