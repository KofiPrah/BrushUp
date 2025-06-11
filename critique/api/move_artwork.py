from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import ArtWork, Folder


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_artwork_to_folder(request):
    """
    Move an artwork to a specific folder or remove it from folders (set to None).
    
    POST /api/artworks/move-to-folder/
    Body: {
        "artwork_id": 123,
        "folder_id": 456  // Optional - omit to remove from folders
    }
    """
    try:
        artwork_id = request.data.get('artwork_id')
        folder_id = request.data.get('folder_id')
        
        if not artwork_id:
            return Response(
                {"error": "artwork_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get artwork and verify ownership
        try:
            artwork = ArtWork.objects.get(id=artwork_id, author=request.user)
        except ArtWork.DoesNotExist:
            return Response(
                {"error": "Artwork not found or you don't have permission to modify it"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Handle folder assignment
        if folder_id:
            try:
                folder = Folder.objects.get(id=folder_id, owner=request.user)
                artwork.folder = folder
            except Folder.DoesNotExist:
                return Response(
                    {"error": "Folder not found or you don't have permission to use it"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Remove from folder (set to None)
            artwork.folder = None
        
        artwork.save()
        
        return Response({
            "success": True,
            "artwork_id": artwork.id,
            "folder_id": artwork.folder.id if artwork.folder else None,
            "folder_name": artwork.folder.name if artwork.folder else None
        })
        
    except Exception as e:
        return Response(
            {"error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )