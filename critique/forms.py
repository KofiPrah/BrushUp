from django import forms
from .models import Comment, ArtWork, Profile

class CommentForm(forms.ModelForm):
    """
    Form for creating and editing comments.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-dark text-white',
            'rows': 3,
            'placeholder': 'Write a comment...'
        }),
        required=True
    )
    
    class Meta:
        model = Comment
        fields = ['content']
        
class ReplyForm(forms.ModelForm):
    """
    Form for replying to comments.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-dark text-white',
            'rows': 2,
            'placeholder': 'Write a reply...'
        }),
        required=True
    )
    
    class Meta:
        model = Comment
        fields = ['content']