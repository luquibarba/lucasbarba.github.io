from django.db import models
import re

class Category(models.Model):
    name = models.CharField(max_length=30)
    icon = models.CharField(max_length=50, default="fas fa-tag", help_text="Ícono de FontAwesome")
    color = models.CharField(max_length=7, default="#3b2342", help_text="Color hexadecimal")

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
    
class Post(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True, help_text="Imagen principal del post")
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField("Category", related_name="posts")
    
    # Nuevos campos para likes/dislikes y funcionalidades
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False, help_text="Post destacado en portada")

    def __str__(self):
        return self.title
    
    def get_reading_time(self):
        """Calcula el tiempo estimado de lectura (promedio 200 palabras por minuto)"""
        word_count = len(re.findall(r'\w+', self.body))
        reading_time = max(1, round(word_count / 200))
        return reading_time
    
    def get_engagement_ratio(self):
        """Calcula el ratio de engagement (likes vs total de interacciones)"""
        total_interactions = self.likes + self.dislikes
        if total_interactions == 0:
            return 0
        return round((self.likes / total_interactions) * 100, 1)
    
    def increment_views(self):
        """Incrementa el contador de visualizaciones"""
        self.views += 1
        self.save(update_fields=['views'])

    class Meta:
        ordering = ['-created_on']
    
class Comment(models.Model):
    author = models.CharField(max_length=60)
    body = models.TextField(max_length=1000, help_text="Máximo 1000 caracteres")
    created_on = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    is_featured = models.BooleanField(default=False, help_text="Comentario destacado")
    
    # Nuevos campos para mejorar comentarios
    email = models.EmailField(blank=True, help_text="Email opcional para respuestas")
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.author} on '{self.post}'"
        
    def get_short_body(self):
        """Devuelve una versión corta del comentario para previews"""
        return self.body[:100] + "..." if len(self.body) > 100 else self.body

    class Meta:
        ordering = ['-is_featured', '-created_on']

class PostLike(models.Model):
    """Modelo para trackear likes/dislikes por IP para evitar spam"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    is_like = models.BooleanField()  # True = like, False = dislike
    created_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'ip_address')
        
    def __str__(self):
        reaction = "Like" if self.is_like else "Dislike"
        return f"{reaction} from {self.ip_address} on {self.post.title}"