from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    Storage for static files on S3.
    """
    location = settings.STATIC_LOCATION if hasattr(settings, 'STATIC_LOCATION') else 'static'
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    """
    Storage for public media files on S3.
    """
    location = settings.PUBLIC_MEDIA_LOCATION if hasattr(settings, 'PUBLIC_MEDIA_LOCATION') else 'media'
    default_acl = 'public-read'
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    """
    Storage for private media files on S3.
    Files are private and require authentication to access.
    """
    location = settings.PRIVATE_MEDIA_LOCATION if hasattr(settings, 'PRIVATE_MEDIA_LOCATION') else 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False