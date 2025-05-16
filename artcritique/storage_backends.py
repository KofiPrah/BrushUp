from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    Storage for static files on S3.
    With bucket ownership enforced, we use bucket policies for access control.
    """
    location = settings.STATIC_LOCATION if hasattr(settings, 'STATIC_LOCATION') else 'static'
    default_acl = None  # Don't set ACL with bucket ownership enforced
    querystring_auth = False  # Don't use authentication for URLs
    
    def get_object_parameters(self, name):
        """
        Override to ensure proper parameters with bucket ownership enforced.
        """
        params = super().get_object_parameters(name)
        # With bucket ownership enforced, we should not set ACL
        if 'ACL' in params:
            del params['ACL']
        # Set bucket owner to have full control
        params['ObjectOwnership'] = 'BucketOwnerEnforced'
        return params


class PublicMediaStorage(S3Boto3Storage):
    """
    Storage for public media files on S3.
    With bucket ownership enforced, we use bucket policies for access control.
    """
    location = settings.PUBLIC_MEDIA_LOCATION if hasattr(settings, 'PUBLIC_MEDIA_LOCATION') else 'media'
    default_acl = None  # Don't set ACL with bucket ownership enforced
    file_overwrite = False
    querystring_auth = False  # Don't use authentication for URLs
    
    def get_object_parameters(self, name):
        """
        Override to ensure proper parameters with bucket ownership enforced.
        """
        params = super().get_object_parameters(name)
        # With bucket ownership enforced, we should not set ACL
        if 'ACL' in params:
            del params['ACL']
        # Set bucket owner to have full control
        params['ObjectOwnership'] = 'BucketOwnerEnforced'
        return params
    
    def _save(self, name, content):
        """
        Override _save to work with bucket ownership enforced.
        """
        # Call the parent _save method with our parameters that don't include ACL
        params = self.get_object_parameters(name)
        return super()._save(name, content)


class PrivateMediaStorage(S3Boto3Storage):
    """
    Storage for private media files on S3.
    Files are private and require authentication to access.
    With bucket ownership enforced, we rely on bucket policy instead of ACLs.
    """
    location = settings.PRIVATE_MEDIA_LOCATION if hasattr(settings, 'PRIVATE_MEDIA_LOCATION') else 'private'
    default_acl = None  # Don't set ACL with bucket ownership enforced
    file_overwrite = False
    custom_domain = False
    querystring_auth = True  # Use authentication for URLs
    
    def get_object_parameters(self, name):
        """
        Override to ensure proper parameters without ACL.
        """
        params = super().get_object_parameters(name)
        # Remove ACL parameter if it exists
        if 'ACL' in params:
            del params['ACL']
        # Set bucket owner to have full control
        params['ObjectOwnership'] = 'BucketOwnerEnforced'
        return params