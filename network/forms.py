from django.forms import ModelForm, Textarea
from .models import Post


class AddPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["body"]
        widgets = {
            "body": Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Write what's on your mind here...",
                    "rows": 4,
                }
            ),
        }
