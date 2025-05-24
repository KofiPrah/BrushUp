from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import ArtWork, Profile, Comment

# Custom User admin with profile inline
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend the User admin
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')

# Re-register the User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register other models
@admin.register(ArtWork)
class ArtWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'total_likes')
    search_fields = ('title', 'description', 'author__username', 'tags')
    list_filter = ('created_at', 'medium')
    readonly_fields = ('created_at', 'updated_at', 'total_likes')
    filter_horizontal = ('likes',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'description', 'image')
        }),
        ('Artwork Details', {
            'fields': ('medium', 'dimensions', 'tags')
        }),
        ('Engagement', {
            'fields': ('likes', 'total_likes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize query by prefetching related objects"""
        return super().get_queryset(request).select_related('author')
    
    def total_likes(self, obj):
        """Display the number of likes for the artwork"""
        return obj.likes.count()
    total_likes.short_description = 'Likes Count'



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'birth_date')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    list_filter = ('location', 'birth_date')
    readonly_fields = ('user',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('bio', 'location', 'birth_date')
        }),
        ('Web Presence', {
            'fields': ('profile_picture', 'website')
        }),
    )
    
    def get_inline_instances(self, request, obj=None):
        """No inlines on the profile page as it's accessed via User"""
        return []

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('artwork', 'author', 'parent', 'created_at')
    search_fields = ('content', 'author__username', 'artwork__title')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('artwork', 'author', 'parent')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize query by prefetching related objects"""
        return super().get_queryset(request).select_related('artwork', 'author', 'parent')
