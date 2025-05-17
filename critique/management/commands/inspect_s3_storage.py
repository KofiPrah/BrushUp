import json
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from critique.models import ArtWork
from artcritique.storage_backends import PublicMediaStorage, PrivateMediaStorage


class Command(BaseCommand):
    help = 'Inspect the S3 storage configuration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n========== Django S3 Storage Inspection =========="))
        
        # Display Django settings
        self.inspect_django_settings()
        
        # Analyze storage backend
        self.analyze_storage_backend()
        
        # Test storage operations
        self.test_storage_operations()
        
        # Inspect existing artwork images
        self.inspect_artwork_images()
        
        # Check access to existing files
        self.check_file_access()
        
        self.stdout.write(self.style.SUCCESS("\n========== Inspection Complete ==========\n"))

    def inspect_django_settings(self):
        """Display relevant Django settings for S3 storage"""
        self.stdout.write(self.style.NOTICE("\n=== Django S3 Storage Settings ==="))
        
        # Check if S3 is enabled
        self.stdout.write(f"S3 enabled: {settings.USE_S3}")
        
        if settings.USE_S3:
            # Display S3 settings
            self.stdout.write(f"Default file storage: {settings.DEFAULT_FILE_STORAGE}")
            self.stdout.write(f"Media URL: {settings.MEDIA_URL}")
            self.stdout.write(f"S3 bucket name: {settings.AWS_STORAGE_BUCKET_NAME}")
            self.stdout.write(f"S3 region: {settings.AWS_S3_REGION_NAME}")
            self.stdout.write(f"Public media location: {settings.PUBLIC_MEDIA_LOCATION}")
            
            # Show ACL settings
            self.stdout.write(f"AWS default ACL: {settings.AWS_DEFAULT_ACL}")
            self.stdout.write(f"Query string auth: {settings.AWS_QUERYSTRING_AUTH}")
            
            # Check for custom domain
            if hasattr(settings, 'AWS_S3_CUSTOM_DOMAIN'):
                self.stdout.write(f"S3 custom domain: {settings.AWS_S3_CUSTOM_DOMAIN}")

    def analyze_storage_backend(self):
        """Analyze the storage backend classes"""
        self.stdout.write(self.style.NOTICE("\n=== Storage Backend Analysis ==="))
        
        # Analyze public media storage
        public_storage = PublicMediaStorage()
        self.stdout.write("Public Storage (DEFAULT_FILE_STORAGE):")
        self.stdout.write(f"  Location: {public_storage.location}")
        self.stdout.write(f"  Base URL: {public_storage.url('')}")
        self.stdout.write(f"  Default ACL: {public_storage.default_acl}")
        
        # Check how it builds paths and URLs
        test_path = "test_image.jpg"
        s3_path = public_storage._normalize_name(test_path)
        self.stdout.write(f"  Test file path: {test_path}")
        self.stdout.write(f"  S3 normalized path: {s3_path}")
        
        # Print key attributes of the class
        self.stdout.write("\nPublic Storage Key Attributes:")
        key_attrs = ['bucket_name', 'location', 'access_key', 'secret_key', 'file_overwrite', 
                     'object_parameters', 'region_name', 'custom_domain', 'secure_urls']
        for attr in key_attrs:
            if hasattr(public_storage, attr):
                try:
                    value = getattr(public_storage, attr)
                    # Don't print secret key content
                    if attr == 'secret_key' and value:
                        value = "<SECRET_KEY_PRESENT>"
                    self.stdout.write(f"  {attr}: {value}")
                except Exception as e:
                    self.stdout.write(f"  {attr}: <Error: {e}>")

    def test_storage_operations(self):
        """Test basic storage operations"""
        self.stdout.write(self.style.NOTICE("\n=== Storage Operations Testing ==="))
        
        # Create a test file
        test_content = b"This is a test file for S3 storage."
        test_path = "storage_test/test_file.txt"
        
        try:
            # Save the test file
            path = default_storage.save(test_path, ContentFile(test_content))
            self.stdout.write(f"File saved at: {path}")
            
            # Get the URL
            url = default_storage.url(path)
            self.stdout.write(f"File URL: {url}")
            
            # Analyze URL components
            url_parts = url.split("/")
            self.stdout.write(f"URL structure: {'/'.join(url_parts[:-1])}/{url_parts[-1]}")
            
            # Check if the file exists
            exists = default_storage.exists(path)
            self.stdout.write(f"File exists: {exists}")
            
            # Display generated paths
            storage = default_storage
            full_path = storage._normalize_name(path)
            self.stdout.write(f"Normalized path: {full_path}")
            
            # Get object parameters that would be sent to S3
            if hasattr(storage, 'get_object_parameters'):
                try:
                    params = storage.get_object_parameters(path)
                    self.stdout.write(f"Object parameters: {json.dumps(params, indent=2)}")
                except Exception as e:
                    self.stdout.write(f"Could not get object parameters: {e}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error testing storage operations: {e}"))

    def inspect_artwork_images(self):
        """Inspect existing artwork images"""
        self.stdout.write(self.style.NOTICE("\n=== Existing Artwork Images ==="))
        
        # Get all artworks with images
        artworks = ArtWork.objects.exclude(image='').order_by('-created_at')[:5]
        
        if not artworks:
            self.stdout.write("No artworks with images found.")
            return
        
        for artwork in artworks:
            self.stdout.write(self.style.SUCCESS(f"\nArtwork: {artwork.title}"))
            self.stdout.write(f"  Image field value: {artwork.image}")
            self.stdout.write(f"  Image URL: {artwork.image.url}")
            
            # Get storage info for this image
            storage = artwork.image.storage
            storage_class = storage.__class__.__name__
            self.stdout.write(f"  Storage class: {storage_class}")
            
            # Check if the file exists in storage
            exists = storage.exists(artwork.image.name)
            self.stdout.write(f"  File exists in storage: {exists}")
            
            # Analyze custom URL generation if any
            if hasattr(storage, '_normalize_name'):
                normalized = storage._normalize_name(artwork.image.name)
                self.stdout.write(f"  Normalized name: {normalized}")

    def check_file_access(self):
        """Check if files are publicly accessible"""
        self.stdout.write(self.style.NOTICE("\n=== File Access Check ==="))
        
        # Get sample files to test
        test_files = []
        
        # Add a direct upload file
        test_files.append({
            'name': 'Direct Upload',
            'url': f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/direct_uploads/test_image_20250517015003.jpg"
        })
        
        # Add a recent Django-uploaded file
        artworks = ArtWork.objects.exclude(image='').order_by('-created_at')[:1]
        if artworks:
            test_files.append({
                'name': f'Django Upload - {artworks[0].title}',
                'url': artworks[0].image.url
            })
        
        # Test each file
        for file in test_files:
            self.stdout.write(f"\nFile: {file['name']}")
            self.stdout.write(f"  URL: {file['url']}")
            
            try:
                response = requests.head(file['url'], timeout=5)
                status = f"✅ ACCESSIBLE (Status: {response.status_code})" if response.status_code == 200 else f"❌ NOT ACCESSIBLE (Status: {response.status_code})"
                self.stdout.write(f"  Access: {status}")
                
                # If not accessible, try a GET request which might provide more details
                if response.status_code != 200:
                    try:
                        get_response = requests.get(file['url'], timeout=5)
                        self.stdout.write(f"  GET response: {get_response.status_code}")
                        if len(get_response.content) < 1000:  # Only show if it's a small response
                            self.stdout.write(f"  Error message: {get_response.text[:500]}")
                    except Exception as e:
                        self.stdout.write(f"  GET request error: {e}")
            except Exception as e:
                self.stdout.write(f"  Error checking file: {e}")