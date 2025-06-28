from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from allauth.socialaccount.models import SocialAccount
import json

from ..forms import SetPasswordForOAuthUserForm, ProfileUpdateForm, RemovePasswordForm


@login_required
def profile_password_management(request):
    """
    View for managing passwords on user profile.
    Allows OAuth users to set/change/remove passwords.
    """
    user = request.user
    
    # Check if user has a social account (OAuth user)
    has_google_account = SocialAccount.objects.filter(user=user, provider='google').exists()
    
    # Check if user has a password set
    has_password = user.has_usable_password()
    
    context = {
        'user': user,
        'has_google_account': has_google_account,
        'has_password': has_password,
        'profile_form': ProfileUpdateForm(instance=user),
    }
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'set_password':
            return handle_set_password(request, user, context)
        elif action == 'change_password':
            return handle_change_password(request, user, context)
        elif action == 'remove_password':
            return handle_remove_password(request, user, context)
        elif action == 'update_profile':
            return handle_update_profile(request, user, context)
    
    # Add appropriate form based on user's current state
    if has_password:
        # User has password - show change password form
        from django.contrib.auth.forms import PasswordChangeForm
        context['password_form'] = PasswordChangeForm(user=user)
        context['remove_password_form'] = RemovePasswordForm()
    else:
        # User doesn't have password - show set password form
        context['password_form'] = SetPasswordForOAuthUserForm(user=user)
    
    return render(request, 'critique/profile_password_management.html', context)


def handle_set_password(request, user, context):
    """Handle setting password for OAuth users."""
    form = SetPasswordForOAuthUserForm(user=user, data=request.POST)
    
    if form.is_valid():
        form.save()
        messages.success(request, 
            'Password set successfully! You can now log in using your email and password alongside your Google account.')
        return redirect('profile_password_management')
    else:
        context['password_form'] = form
        messages.error(request, 'Please correct the errors below.')
        return render(request, 'critique/profile_password_management.html', context)


def handle_change_password(request, user, context):
    """Handle changing password for users who already have one."""
    from django.contrib.auth.forms import PasswordChangeForm
    
    form = PasswordChangeForm(user=user, data=request.POST)
    
    if form.is_valid():
        form.save()
        # Re-authenticate user after password change
        login(request, user)
        messages.success(request, 'Password changed successfully!')
        return redirect('profile_password_management')
    else:
        context['password_form'] = form
        messages.error(request, 'Please correct the errors below.')
        return render(request, 'critique/profile_password_management.html', context)


def handle_remove_password(request, user, context):
    """Handle removing password for OAuth users."""
    form = RemovePasswordForm(data=request.POST)
    
    if form.is_valid():
        # Only allow removing password if user has a social account
        has_google_account = SocialAccount.objects.filter(user=user, provider='google').exists()
        
        if has_google_account:
            user.set_unusable_password()
            user.save()
            messages.success(request, 
                'Password removed successfully! You can now only log in using your Google account.')
        else:
            messages.error(request, 
                'Cannot remove password: You need at least one login method available.')
        
        return redirect('profile_password_management')
    else:
        context['remove_password_form'] = form
        messages.error(request, 'Please confirm that you understand the implications.')
        return render(request, 'critique/profile_password_management.html', context)


def handle_update_profile(request, user, context):
    """Handle updating user profile information."""
    form = ProfileUpdateForm(data=request.POST, instance=user)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile_password_management')
    else:
        context['profile_form'] = form
        messages.error(request, 'Please correct the errors in your profile.')
        return render(request, 'critique/profile_password_management.html', context)


@require_POST
@csrf_protect
def send_password_reset_to_oauth_user(request):
    """
    Send password reset email to OAuth users who want to set up password login.
    This is an alternative way for OAuth users to set up passwords.
    """
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email:
            return JsonResponse({'success': False, 'error': 'Email is required'})
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            return JsonResponse({
                'success': True, 
                'message': 'If this email is associated with an account, you will receive password reset instructions.'
            })
        
        # Check if user has a Google account
        has_google_account = SocialAccount.objects.filter(user=user, provider='google').exists()
        
        if not has_google_account:
            return JsonResponse({
                'success': True, 
                'message': 'If this email is associated with an account, you will receive password reset instructions.'
            })
        
        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Create password reset URL
        reset_url = request.build_absolute_uri(
            f'/accounts/password/reset/key/{uid}/{token}/'
        )
        
        # Prepare email content
        subject = 'Set up password for your Brush Up account'
        
        # Render email template
        email_context = {
            'user': user,
            'reset_url': reset_url,
            'domain': request.get_host(),
            'site_name': 'Brush Up',
            'has_google_account': True,
        }
        
        html_message = render_to_string('critique/emails/oauth_password_setup.html', email_context)
        text_message = render_to_string('critique/emails/oauth_password_setup.txt', email_context)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Password setup instructions have been sent to your email address.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request format'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred while sending the email'})


def get_user_auth_status(request):
    """
    API endpoint to get current user's authentication status.
    Useful for frontend to determine what options to show.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'authenticated': False,
            'has_password': False,
            'has_google_account': False,
        })
    
    user = request.user
    has_google_account = SocialAccount.objects.filter(user=user, provider='google').exists()
    has_password = user.has_usable_password()
    
    return JsonResponse({
        'authenticated': True,
        'has_password': has_password,
        'has_google_account': has_google_account,
        'email': user.email,
        'username': user.username,
        'full_name': user.get_full_name(),
    })