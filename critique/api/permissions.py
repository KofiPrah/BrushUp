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