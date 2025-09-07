"""
Test script for role-based permissions in the Brush Up application

This script tests the role-based permissions by:
1. Creating users with different roles (USER, MODERATOR, ADMIN)
2. Attempting operations that should be allowed or denied based on roles
3. Printing the results to verify permissions are working

Usage:
    python scripts/utility/test_permissions.py
"""

import os
import sys
import django

# Ensure project root is on the Python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Import models and permissions after setup
from django.contrib.auth.models import User
from critique.models import Profile, ArtWork, Critique
from critique.api.permissions import (
    IsAuthorOrReadOnly, IsOwnerOrReadOnly, IsModeratorOrOwner,
    IsModeratorOrAdmin, IsAdminOnly
)
from rest_framework.test import APIRequestFactory
from django.test import RequestFactory


def create_test_users():
    """Create test users with different roles for permission testing"""
    print("Creating test users with different roles...")
    
    # Create or get regular user
    regular_user, created = User.objects.get_or_create(
        username='regular_user',
        email='regular@example.com'
    )
    if created:
        regular_user.set_password('password123')
        regular_user.save()
        regular_profile = Profile.objects.get(user=regular_user)
        regular_profile.role = Profile.ROLE_USER
        regular_profile.save()
    
    # Create or get moderator
    moderator, created = User.objects.get_or_create(
        username='moderator',
        email='moderator@example.com'
    )
    if created:
        moderator.set_password('password123')
        moderator.save()
        moderator_profile = Profile.objects.get(user=moderator)
        moderator_profile.role = Profile.ROLE_MODERATOR
        moderator_profile.save()
    
    # Create or get admin
    admin, created = User.objects.get_or_create(
        username='admin',
        email='admin@example.com'
    )
    if created:
        admin.set_password('password123')
        admin.save()
        admin_profile = Profile.objects.get(user=admin)
        admin_profile.role = Profile.ROLE_ADMIN
        admin_profile.save()
    
    return regular_user, moderator, admin


def test_permissions():
    """Test the role-based permission classes"""
    regular_user, moderator, admin = create_test_users()
    
    # Create test artwork
    artwork, created = ArtWork.objects.get_or_create(
        title='Test Artwork',
        description='Artwork for testing permissions',
        author=regular_user
    )
    
    # Create test critique
    critique, created = Critique.objects.get_or_create(
        artwork=artwork,
        text='Test critique for permission testing',
        author=moderator,
        composition_score=4,
        technique_score=3,
        originality_score=5
    )
    
    print("\nTesting permission classes...\n")
    
    # Test IsModeratorOrAdmin permission
    factory = RequestFactory()
    
    # Test with regular user
    request = factory.get('/')
    request.user = regular_user
    moderator_admin_perm = IsModeratorOrAdmin()
    has_permission = moderator_admin_perm.has_permission(request, None)
    print(f"IsModeratorOrAdmin - Regular user permission: {has_permission} (should be False)")
    
    # Test with moderator
    request.user = moderator
    has_permission = moderator_admin_perm.has_permission(request, None)
    print(f"IsModeratorOrAdmin - Moderator permission: {has_permission} (should be True)")
    
    # Test with admin
    request.user = admin
    has_permission = moderator_admin_perm.has_permission(request, None)
    print(f"IsModeratorOrAdmin - Admin permission: {has_permission} (should be True)")
    
    # Test IsModeratorOrOwner permission
    moderator_owner_perm = IsModeratorOrOwner()
    
    # Create a POST request for write operations
    post_request = factory.post('/')
    
    # Test with regular user (not the owner)
    another_user, _ = User.objects.get_or_create(username='another_user')
    post_request.user = another_user
    has_permission = moderator_owner_perm.has_object_permission(post_request, None, critique)
    print(f"IsModeratorOrOwner - Non-owner regular user: {has_permission} (should be False)")
    
    # Test with owner (regular user)
    post_request.user = regular_user
    has_permission = moderator_owner_perm.has_object_permission(post_request, None, artwork)
    print(f"IsModeratorOrOwner - Owner (regular user): {has_permission} (should be True)")
    
    # Test with moderator (not the owner)
    post_request.user = moderator
    has_permission = moderator_owner_perm.has_object_permission(post_request, None, artwork)
    print(f"IsModeratorOrOwner - Moderator (not owner): {has_permission} (should be True)")
    
    # Test with admin (not the owner)
    post_request.user = admin
    has_permission = moderator_owner_perm.has_object_permission(post_request, None, artwork)
    print(f"IsModeratorOrOwner - Admin (not owner): {has_permission} (should be True)")
    
    # Test IsAdminOnly permission
    admin_only_perm = IsAdminOnly()
    
    # Test with regular user
    request.user = regular_user
    has_permission = admin_only_perm.has_permission(request, None)
    print(f"IsAdminOnly - Regular user: {has_permission} (should be False)")
    
    # Test with moderator
    request.user = moderator
    has_permission = admin_only_perm.has_permission(request, None)
    print(f"IsAdminOnly - Moderator: {has_permission} (should be False)")
    
    # Test with admin
    request.user = admin
    has_permission = admin_only_perm.has_permission(request, None)
    print(f"IsAdminOnly - Admin: {has_permission} (should be True)")


if __name__ == "__main__":
    test_permissions()