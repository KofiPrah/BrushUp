"""
Services for the Brush Up application.
Handles business logic for achievements, notifications, and other features.
"""

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from .models import (
    AchievementBadge, UserAchievement, ArtWork, Critique, 
    Reaction, KarmaEvent, Notification
)
import logging

logger = logging.getLogger(__name__)


class AchievementService:
    """
    Service class to handle achievement badge logic.
    Calculates user statistics and awards appropriate badges.
    """
    
    @staticmethod
    def check_and_award_badges(user):
        """
        Check all possible badges for a user and award any they qualify for.
        Returns a list of newly awarded badges.
        """
        newly_awarded = []
        
        # Get all active badges that user hasn't earned yet
        earned_badge_ids = user.achievements.values_list('badge_id', flat=True)
        available_badges = AchievementBadge.objects.filter(
            is_active=True
        ).exclude(id__in=earned_badge_ids)
        
        for badge in available_badges:
            if AchievementService._check_badge_criteria(user, badge):
                # Award the badge
                achievement = UserAchievement.objects.create(
                    user=user,
                    badge=badge,
                    context_data=AchievementService._get_badge_context(user, badge)
                )
                newly_awarded.append(achievement)
                
                # Send notification
                AchievementService._send_badge_notification(user, badge)
                
                logger.info(f"Awarded badge '{badge.name}' to user {user.username}")
        
        return newly_awarded
    
    @staticmethod
    def _check_badge_criteria(user, badge):
        """
        Check if a user meets the criteria for a specific badge.
        """
        criteria_type = badge.criteria_type
        criteria_value = badge.criteria_value
        
        try:
            if criteria_type == 'artwork_count':
                count = user.artworks.filter(is_published=True).count()
                return count >= criteria_value
                
            elif criteria_type == 'published_artwork_count':
                count = user.artworks.filter(is_published=True, visibility='public').count()
                return count >= criteria_value
                
            elif criteria_type == 'critique_count':
                count = user.critiques.filter(is_hidden=False).count()
                return count >= criteria_value
                
            elif criteria_type == 'helpful_reactions':
                count = user.critiques.aggregate(
                    helpful_count=Count('reactions', filter=Q(reactions__reaction_type='HELPFUL'))
                )['helpful_count'] or 0
                return count >= criteria_value
                
            elif criteria_type == 'karma_points':
                return user.profile.karma >= criteria_value
                
            elif criteria_type == 'artwork_likes':
                count = user.artworks.aggregate(
                    total_likes=Count('likes')
                )['total_likes'] or 0
                return count >= criteria_value
                
            elif criteria_type == 'critique_reactions':
                count = user.critiques.aggregate(
                    total_reactions=Count('reactions')
                )['total_reactions'] or 0
                return count >= criteria_value
                
            elif criteria_type == 'days_active':
                if user.date_joined:
                    days_active = (timezone.now().date() - user.date_joined.date()).days
                    return days_active >= criteria_value
                return False
                
            elif criteria_type == 'version_count':
                # Check if user has artworks with multiple versions
                artwork_with_versions = user.artworks.annotate(
                    version_count=Count('versions')
                ).filter(version_count__gte=criteria_value)
                return artwork_with_versions.exists()
                
            elif criteria_type == 'folder_count':
                count = user.folders.filter(visibility='public').count()
                return count >= criteria_value
                
            elif criteria_type == 'seeking_critique_count':
                count = user.artworks.filter(seeking_critique=True, is_published=True).count()
                return count >= criteria_value
                
        except Exception as e:
            logger.error(f"Error checking badge criteria for {badge.name}: {str(e)}")
            return False
        
        return False
    
    @staticmethod
    def _get_badge_context(user, badge):
        """
        Get context data about when/why the badge was earned.
        """
        criteria_type = badge.criteria_type
        
        context = {
            'criteria_type': criteria_type,
            'criteria_value': badge.criteria_value,
            'earned_at': timezone.now().isoformat()
        }
        
        try:
            if criteria_type == 'artwork_count':
                context['current_count'] = user.artworks.filter(is_published=True).count()
            elif criteria_type == 'critique_count':
                context['current_count'] = user.critiques.filter(is_hidden=False).count()
            elif criteria_type == 'karma_points':
                context['current_karma'] = user.profile.karma
            # Add more context as needed
        except Exception as e:
            logger.error(f"Error getting badge context for {badge.name}: {str(e)}")
        
        return context
    
    @staticmethod
    def _send_badge_notification(user, badge):
        """
        Send a notification to the user about earning a new badge.
        """
        try:
            message = f"🏆 Congratulations! You've earned the '{badge.name}' badge!"
            
            Notification.objects.create(
                recipient=user,
                message=message,
                url=f'/profile/{user.username}/'  # Link to user's profile to see badges
            )
            
            # Mark notification as sent in the achievement
            achievement = UserAchievement.objects.get(user=user, badge=badge)
            achievement.notification_sent = True
            achievement.save()
            
        except Exception as e:
            logger.error(f"Error sending badge notification to {user.username}: {str(e)}")
    
    @staticmethod
    def get_user_badge_progress(user):
        """
        Get progress towards earning various badges for a user.
        Returns information about completed and in-progress badges.
        """
        # Get earned badges
        earned_badges = user.achievements.select_related('badge').order_by('-earned_at')
        
        # Get available badges user hasn't earned
        earned_badge_ids = earned_badges.values_list('badge_id', flat=True)
        available_badges = AchievementBadge.objects.filter(
            is_active=True,
            is_hidden=False
        ).exclude(id__in=earned_badge_ids).order_by('category', 'tier', 'sort_order')
        
        # Calculate progress for available badges
        badge_progress = []
        for badge in available_badges:
            current_value = AchievementService._get_current_value(user, badge)
            progress_percentage = min(100, (current_value / badge.criteria_value) * 100) if badge.criteria_value > 0 else 0
            
            badge_progress.append({
                'badge': badge,
                'current_value': current_value,
                'target_value': badge.criteria_value,
                'progress_percentage': progress_percentage,
                'is_completed': progress_percentage >= 100
            })
        
        return {
            'earned_badges': earned_badges,
            'badge_progress': badge_progress
        }
    
    @staticmethod
    def _get_current_value(user, badge):
        """
        Get the current value for a user's progress towards a badge.
        """
        criteria_type = badge.criteria_type
        
        try:
            if criteria_type == 'artwork_count':
                return user.artworks.filter(is_published=True).count()
            elif criteria_type == 'published_artwork_count':
                return user.artworks.filter(is_published=True, visibility='public').count()
            elif criteria_type == 'critique_count':
                return user.critiques.filter(is_hidden=False).count()
            elif criteria_type == 'helpful_reactions':
                return user.critiques.aggregate(
                    helpful_count=Count('reactions', filter=Q(reactions__reaction_type='HELPFUL'))
                )['helpful_count'] or 0
            elif criteria_type == 'karma_points':
                return user.profile.karma
            elif criteria_type == 'artwork_likes':
                return user.artworks.aggregate(
                    total_likes=Count('likes')
                )['total_likes'] or 0
            elif criteria_type == 'critique_reactions':
                return user.critiques.aggregate(
                    total_reactions=Count('reactions')
                )['total_reactions'] or 0
            elif criteria_type == 'days_active':
                if user.date_joined:
                    return (timezone.now().date() - user.date_joined.date()).days
                return 0
            elif criteria_type == 'folder_count':
                return user.folders.filter(visibility='public').count()
            elif criteria_type == 'seeking_critique_count':
                return user.artworks.filter(seeking_critique=True, is_published=True).count()
        except Exception as e:
            logger.error(f"Error getting current value for {badge.name}: {str(e)}")
        
        return 0
    
    @staticmethod
    def trigger_badge_check(user, trigger_type=None):
        """
        Trigger a badge check for a user after specific actions.
        This can be called after artwork uploads, critique submissions, etc.
        """
        logger.info(f"Triggering badge check for {user.username} (trigger: {trigger_type})")
        return AchievementService.check_and_award_badges(user)


def create_default_badges():
    """
    Create default achievement badges for the platform.
    This function can be run to populate the database with initial badges.
    """
    default_badges = [
        # Artwork badges
        {
            'name': 'First Steps',
            'description': 'Upload your first artwork to the platform',
            'category': AchievementBadge.CATEGORY_ARTWORK,
            'tier': AchievementBadge.TIER_BRONZE,
            'icon': 'bi-image',
            'color': 'text-warning',
            'criteria_type': 'artwork_count',
            'criteria_value': 1,
            'sort_order': 1
        },
        {
            'name': 'Prolific Creator',
            'description': 'Upload 10 artworks to showcase your creativity',
            'category': AchievementBadge.CATEGORY_ARTWORK,
            'tier': AchievementBadge.TIER_SILVER,
            'icon': 'bi-collection',
            'color': 'text-info',
            'criteria_type': 'artwork_count',
            'criteria_value': 10,
            'sort_order': 2
        },
        {
            'name': 'Art Master',
            'description': 'Upload 50 artworks to demonstrate mastery',
            'category': AchievementBadge.CATEGORY_ARTWORK,
            'tier': AchievementBadge.TIER_GOLD,
            'icon': 'bi-star-fill',
            'color': 'text-warning',
            'criteria_type': 'artwork_count',
            'criteria_value': 50,
            'sort_order': 3
        },
        
        # Critique badges
        {
            'name': 'Helpful Critic',
            'description': 'Write your first helpful critique',
            'category': AchievementBadge.CATEGORY_CRITIQUE,
            'tier': AchievementBadge.TIER_BRONZE,
            'icon': 'bi-chat-text',
            'color': 'text-success',
            'criteria_type': 'critique_count',
            'criteria_value': 1,
            'sort_order': 1
        },
        {
            'name': 'Feedback Expert',
            'description': 'Write 25 critiques to help fellow artists',
            'category': AchievementBadge.CATEGORY_CRITIQUE,
            'tier': AchievementBadge.TIER_SILVER,
            'icon': 'bi-chat-dots',
            'color': 'text-success',
            'criteria_type': 'critique_count',
            'criteria_value': 25,
            'sort_order': 2
        },
        {
            'name': 'Critique Champion',
            'description': 'Write 100 critiques to become a community mentor',
            'category': AchievementBadge.CATEGORY_CRITIQUE,
            'tier': AchievementBadge.TIER_GOLD,
            'icon': 'bi-award',
            'color': 'text-warning',
            'criteria_type': 'critique_count',
            'criteria_value': 100,
            'sort_order': 3
        },
        
        # Community badges
        {
            'name': 'Well Liked',
            'description': 'Receive 100 likes on your artworks',
            'category': AchievementBadge.CATEGORY_COMMUNITY,
            'tier': AchievementBadge.TIER_SILVER,
            'icon': 'bi-heart-fill',
            'color': 'text-danger',
            'criteria_type': 'artwork_likes',
            'criteria_value': 100,
            'sort_order': 1
        },
        {
            'name': 'Community Favorite',
            'description': 'Receive 500 likes on your artworks',
            'category': AchievementBadge.CATEGORY_COMMUNITY,
            'tier': AchievementBadge.TIER_GOLD,
            'icon': 'bi-heart-pulse',
            'color': 'text-danger',
            'criteria_type': 'artwork_likes',
            'criteria_value': 500,
            'sort_order': 2
        },
        
        # Milestone badges
        {
            'name': 'Karma Rookie',
            'description': 'Earn 100 karma points through positive contributions',
            'category': AchievementBadge.CATEGORY_MILESTONE,
            'tier': AchievementBadge.TIER_BRONZE,
            'icon': 'bi-arrow-up-circle',
            'color': 'text-primary',
            'criteria_type': 'karma_points',
            'criteria_value': 100,
            'sort_order': 1
        },
        {
            'name': 'Karma Master',
            'description': 'Earn 1000 karma points through exceptional contributions',
            'category': AchievementBadge.CATEGORY_MILESTONE,
            'tier': AchievementBadge.TIER_GOLD,
            'icon': 'bi-arrow-up-circle-fill',
            'color': 'text-primary',
            'criteria_type': 'karma_points',
            'criteria_value': 1000,
            'sort_order': 2
        },
        
        # Special badges
        {
            'name': 'Organizer',
            'description': 'Create 5 portfolio folders to organize your work',
            'category': AchievementBadge.CATEGORY_SPECIAL,
            'tier': AchievementBadge.TIER_BRONZE,
            'icon': 'bi-folder-fill',
            'color': 'text-secondary',
            'criteria_type': 'folder_count',
            'criteria_value': 5,
            'sort_order': 1
        },
        {
            'name': 'Feedback Seeker',
            'description': 'Mark 10 artworks as seeking critique',
            'category': AchievementBadge.CATEGORY_SPECIAL,
            'tier': AchievementBadge.TIER_BRONZE,
            'icon': 'bi-question-circle',
            'color': 'text-info',
            'criteria_type': 'seeking_critique_count',
            'criteria_value': 10,
            'sort_order': 2
        }
    ]
    
    created_count = 0
    for badge_data in default_badges:
        badge, created = AchievementBadge.objects.get_or_create(
            name=badge_data['name'],
            defaults=badge_data
        )
        if created:
            created_count += 1
            logger.info(f"Created badge: {badge.name}")
    
    logger.info(f"Created {created_count} new achievement badges")
    return created_count