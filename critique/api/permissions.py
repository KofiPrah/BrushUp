from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the author of an artwork to edit or delete it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the author or admin
        return obj.author == request.user or request.user.is_staff

class IsModeratorOrAdmin(permissions.BasePermission):
    """
    Permission that allows access only to users with MODERATOR or ADMIN role.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated and has appropriate role
        if not request.user or not request.user.is_authenticated:
            return False
        
        # First check Profile.role if available
        try:
            profile = request.user.profile
            if hasattr(profile, 'role'):
                return profile.role in ['MODERATOR', 'ADMIN']
            elif hasattr(profile, 'is_moderator_or_admin'):
                return profile.is_moderator_or_admin()
        except (AttributeError, Exception):
            pass
            
        # Fall back to checking is_staff if profile check fails
        return request.user.is_staff or request.user.is_superuser
            
class IsAdminOnly(permissions.BasePermission):
    """
    Permission that allows access only to users with ADMIN role.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated and has the ADMIN role
        if not request.user or not request.user.is_authenticated:
            return False
        
        # First check Profile.role if available
        try:
            profile = request.user.profile
            if hasattr(profile, 'role'):
                return profile.role == 'ADMIN'
            elif hasattr(profile, 'is_admin'):
                return profile.is_admin()
        except (AttributeError, Exception):
            pass
            
        # Fall back to checking is_superuser if profile check fails
        return request.user.is_superuser
            
class IsModeratorOrOwner(permissions.BasePermission):
    """
    Permission that allows read access to everyone, but write access only to:
    1. The owner (author/user) of the object
    2. Users with MODERATOR or ADMIN role
    """
    
    def has_permission(self, request, view):
        # Anyone can access read methods
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Otherwise, must be authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Must be authenticated for write operations
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Check if user is a moderator or admin
        is_moderator = False
        try:
            profile = request.user.profile
            if hasattr(profile, 'role'):
                is_moderator = profile.role in ['MODERATOR', 'ADMIN']
            elif hasattr(profile, 'is_moderator_or_admin'):
                is_moderator = profile.is_moderator_or_admin()
        except (AttributeError, Exception):
            is_moderator = request.user.is_staff or request.user.is_superuser
                
        # If user is moderator, allow access
        if is_moderator:
            return True
            
        # Otherwise, check if user is the owner
        is_owner = False
        if hasattr(obj, 'author'):
            is_owner = obj.author == request.user
        elif hasattr(obj, 'user'):
            is_owner = obj.user == request.user
        elif hasattr(obj, 'owner'):
            is_owner = obj.owner == request.user
            
        return is_owner
        
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    More generic version of the permission that works with any model that has
    either a 'user', 'author', or 'owner' attribute.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Figure out the owner field
        if hasattr(obj, 'author'):
            return obj.author == request.user or request.user.is_staff
        elif hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user or request.user.is_staff
            
        # If we can't figure out the owner, deny permission
        return False