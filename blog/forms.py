from django import forms

class CommentForm(forms.Form):
    author = forms.CharField(
        max_length=60,
        widget=forms.TextInput(
            attrs={
                "class": "form-control", 
                "placeholder": "Tu nombre",
                "required": True
            }
        ),
        label="Nombre"
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control", 
                "placeholder": "tu@email.com (opcional)"
            }
        ),
        label="Email (opcional)",
        help_text="Para recibir notificaciones de respuestas"
    )
    
    body = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(
            attrs={
                "class": "form-control comment-textarea", 
                "placeholder": "Escribe tu comentario aquí... (máximo 1000 caracteres)",
                "rows": 4,
                "maxlength": 1000,
                "data-max-length": 1000
            }
        ),
        label="Comentario"
    )
    
    def clean_body(self):
        body = self.cleaned_data.get('body')
        if body and len(body) > 1000:
            raise forms.ValidationError('El comentario no puede exceder 1000 caracteres.')
        return body
    
    def clean_author(self):
        author = self.cleaned_data.get('author')
        if author and len(author.strip()) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        return author.strip() if author else author