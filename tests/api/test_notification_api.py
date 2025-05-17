"""
Test script for the notification API endpoints.

This script tests the notification API endpoints to verify their functionality:
1. Getting all notifications for a user
2. Getting unread notification count
3. Marking a single notification as read
4. Marking all notifications as read
5. Marking multiple notifications as read

Run this script to verify that the notification API endpoints are working correctly.
"""
import os
import sys
import requests
import json
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth import get_user_model
from critique.models import Notification, ArtWork, Critique
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

# API endpoint for testing (adjust as needed)
BASE_URL = 'http://127.0.0.1:5000/api'  # Using the correct port for our application
HEADERS = {'Content-Type': 'application/json'}
AUTH_COOKIES = {}  # Will store authentication cookies after login

def login(username, password):
    """Log in and get authentication cookies."""
    global AUTH_COOKIES
    
    # Get CSRF token first
    csrf_response = requests.get(f"{BASE_URL}/auth/csrf/", headers=HEADERS)
    csrf_token = csrf_response.json().get('csrf_token')
    
    # Set up cookies and headers for login
    csrf_cookie = csrf_response.cookies.get_dict()
    login_headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    }
    
    # Login request
    login_data = {
        'username': username,
        'password': password
    }
    login_response = requests.post(
        f"{BASE_URL}/auth/login/",
        headers=login_headers,
        cookies=csrf_cookie,
        json=login_data
    )
    
    if login_response.status_code == 200:
        AUTH_COOKIES = login_response.cookies.get_dict()
        print(f"Successfully logged in as {username}")
        return True
    else:
        print(f"Failed to log in: {login_response.text}")
        return False

def create_test_data():
    """Create test users and notifications for testing."""
    # Create test users if they don't exist
    user1 = User.objects.get_or_create(
        username='notification_tester',
        email='notification.tester@example.com',
    )[0]
    user1.set_password('testpassword')
    user1.save()
    
    user2 = User.objects.get_or_create(
        username='notification_sender',
        email='notification.sender@example.com',
    )[0]
    user2.set_password('testpassword')
    user2.save()
    
    # Create test artwork and critique for notifications
    artwork = ArtWork.objects.get_or_create(
        title='Notification Test Artwork',
        author=user1,
        description='An artwork for testing notifications',
        medium='Digital',
    )[0]
    
    critique = Critique.objects.get_or_create(
        artwork=artwork,
        author=user2,
        text='This is a test critique for notifications',
        composition_score=4,
        technique_score=5,
        originality_score=4,
    )[0]
    
    # Get content types for creating generic relations
    artwork_content_type = ContentType.objects.get_for_model(ArtWork)
    critique_content_type = ContentType.objects.get_for_model(Critique)
    
    # Create test notifications for user1
    notifications = []
    for i in range(5):
        notification = Notification.objects.create(
            recipient=user1,
            message=f"Test notification {i+1}",
            target_content_type=critique_content_type if i % 2 == 0 else artwork_content_type,
            target_object_id=critique.id if i % 2 == 0 else artwork.id,
            is_read=False
        )
        notifications.append(notification)
    
    print(f"Created {len(notifications)} test notifications for {user1.username}")
    return user1, notifications

def test_get_notifications():
    """Test getting all notifications for the current user."""
    response = requests.get(
        f"{BASE_URL}/notifications/",
        cookies=AUTH_COOKIES,
        headers=HEADERS
    )
    
    if response.status_code == 200:
        notifications = response.json()
        print(f"✓ Successfully retrieved {len(notifications)} notifications")
        return notifications
    else:
        print(f"✗ Failed to get notifications: {response.text}")
        return []

def test_get_unread_count():
    """Test getting the count of unread notifications."""
    response = requests.get(
        f"{BASE_URL}/notifications/unread/",
        cookies=AUTH_COOKIES,
        headers=HEADERS
    )
    
    if response.status_code == 200:
        unread_count = response.json().get('unread_count', 0)
        print(f"✓ Successfully retrieved unread count: {unread_count}")
        return unread_count
    else:
        print(f"✗ Failed to get unread count: {response.text}")
        return 0

def test_mark_notification_read(notification_id):
    """Test marking a single notification as read."""
    response = requests.post(
        f"{BASE_URL}/notifications/{notification_id}/mark_read/",
        cookies=AUTH_COOKIES,
        headers=HEADERS
    )
    
    if response.status_code == 200:
        print(f"✓ Successfully marked notification {notification_id} as read")
        return True
    else:
        print(f"✗ Failed to mark notification as read: {response.text}")
        return False

def test_mark_multiple_read(notification_ids):
    """Test marking multiple notifications as read."""
    data = {"notification_ids": notification_ids}
    
    # Update headers to include CSRF token
    headers = HEADERS.copy()
    headers['X-CSRFToken'] = AUTH_COOKIES.get('csrftoken', '')
    
    response = requests.post(
        f"{BASE_URL}/notifications/mark_multiple_read/",
        cookies=AUTH_COOKIES,
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ {result.get('message')}")
        return True
    else:
        print(f"✗ Failed to mark multiple notifications as read: {response.text}")
        return False

def test_mark_all_read():
    """Test marking all notifications as read."""
    # Update headers to include CSRF token
    headers = HEADERS.copy()
    headers['X-CSRFToken'] = AUTH_COOKIES.get('csrftoken', '')
    
    response = requests.post(
        f"{BASE_URL}/notifications/mark_all_read/",
        cookies=AUTH_COOKIES,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✓ Successfully marked all notifications as read")
        return True
    else:
        print(f"✗ Failed to mark all notifications as read: {response.text}")
        return False

def main():
    """Run the notification API test."""
    print("Starting notification API endpoint test...\n")
    
    # Create test data
    user, notifications = create_test_data()
    
    # Log in as the test user
    if not login('notification_tester', 'testpassword'):
        print("Cannot continue test without login")
        return
    
    # Test getting all notifications
    all_notifications = test_get_notifications()
    
    # Test getting unread notification count
    unread_before = test_get_unread_count()
    
    if all_notifications:
        # Test marking a single notification as read
        first_notification_id = all_notifications[0]['id']
        test_mark_notification_read(first_notification_id)
        
        # Verify unread count changed
        unread_after_single = test_get_unread_count()
        print(f"Unread count changed from {unread_before} to {unread_after_single}")
        
        # Test marking multiple notifications as read (if we have enough)
        if len(all_notifications) >= 3:
            notification_ids = [n['id'] for n in all_notifications[1:3]]
            test_mark_multiple_read(notification_ids)
            
            # Verify unread count changed
            unread_after_multiple = test_get_unread_count()
            print(f"Unread count changed from {unread_after_single} to {unread_after_multiple}")
        
        # Test marking all notifications as read
        test_mark_all_read()
        
        # Verify all are marked as read
        final_unread = test_get_unread_count()
        print(f"Final unread count: {final_unread}")
    
    print("\nNotification API test completed!")

if __name__ == "__main__":
    main()