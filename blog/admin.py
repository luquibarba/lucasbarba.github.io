from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from blog.models import Category, Comment, Post, PostLike

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_preview', 'color_preview', 'post_count')
    search_fields = ('name',)
    
    def icon_preview(self, obj):
        return format_html('<i class="{}" style="font-size: 18px;"></i>', obj.icon)
    icon_preview.short_description = 'Ícono'
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 50%; display: inline-block;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'engagement_display', 'views', 'featured', 'created_on', 'category_list')
    list_filter = ('categories', 'featured', 'created_on', 'last_modified')
    search_fields = ('title', 'body')
    filter_horizontal = ('categories',)
    list_editable = ('featured',)
    actions = ['reset_engagement', 'mark_as_featured', 'unmark_as_featured']
    
    readonly_fields = ('created_on', 'last_modified', 'views', 'engagement_stats')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'body', 'image', 'featured')
        }),
        ('Categorización', {
            'fields': ('categories',)
        }),
        ('Estadísticas', {
            'fields': ('views', 'engagement_stats', 'likes', 'dislikes'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_on', 'last_modified'),
            'classes': ('collapse',)
        }),
    )
    
    def engagement_display(self, obj):
        ratio = obj.get_engagement_ratio()
        color = '#28a745' if ratio >= 70 else '#ffc107' if ratio >= 40 else '#dc3545'
        return format_html(
            '<span style="color: {};">👍 {} 👎 {} ({}%)</span>',
            color, obj.likes, obj.dislikes, ratio
        )
    engagement_display.short_description = 'Engagement'
    
    def engagement_stats(self, obj):
        if not obj.pk:
            return "Guarda el post primero para ver estadísticas"
        
        total_interactions = obj.likes + obj.dislikes
        ratio = obj.get_engagement_ratio()
        reading_time = obj.get_reading_time()
        
        return format_html(
            '''
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <strong>📊 Estadísticas del Post:</strong><br>
                <div style="margin-top: 10px;">
                    📖 Tiempo de lectura: {} min<br>
                    👀 Visualizaciones: {:,}<br>
                    💬 Comentarios: {}<br>
                    👍 Likes: {} | 👎 Dislikes: {}<br>
                    📈 Ratio positivo: {}%<br>
                    🔥 Total interacciones: {}
                </div>
            </div>
            ''',
            reading_time, obj.views, obj.comment_set.count(),
            obj.likes, obj.dislikes, ratio, total_interactions
        )
    engagement_stats.short_description = 'Estadísticas Detalladas'
    
    def category_list(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])
    category_list.short_description = 'Categorías'
    
    def reset_engagement(self, request, queryset):
        """Resetea likes, dislikes y views de posts seleccionados"""
        for post in queryset:
            post.likes = 0
            post.dislikes = 0
            post.views = 0
            post.save()
            # También eliminar registros de PostLike
            PostLike.objects.filter(post=post).delete()
        
        count = queryset.count()
        messages.success(request, f'Se reseteó el engagement de {count} post(s)')
    reset_engagement.short_description = 'Resetear engagement (likes, dislikes, views)'
    
    def mark_as_featured(self, request, queryset):
        queryset.update(featured=True)
        messages.success(request, f'{queryset.count()} post(s) marcado(s) como destacado(s)')
    mark_as_featured.short_description = 'Marcar como destacado'
    
    def unmark_as_featured(self, request, queryset):
        queryset.update(featured=False)
        messages.success(request, f'{queryset.count()} post(s) desmarcado(s) como destacado(s)')
    unmark_as_featured.short_description = 'Desmarcar como destacado'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'is_featured', 'created_on', 'comment_preview', 'has_email')
    list_filter = ('is_featured', 'created_on', 'post')
    search_fields = ('author', 'body', 'post__title', 'email')
    list_editable = ('is_featured',)
    actions = ['mark_as_featured', 'unmark_as_featured']
    
    fieldsets = (
        (None, {
            'fields': ('author', 'email', 'body', 'post', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'created_on'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_on', 'ip_address')
    
    def comment_preview(self, obj):
        return obj.get_short_body()
    comment_preview.short_description = 'Preview'
    
    def has_email(self, obj):
        return '✉️' if obj.email else '❌'
    has_email.short_description = 'Email'
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        messages.success(request, f'{queryset.count()} comentario(s) marcado(s) como destacado(s)')
    mark_as_featured.short_description = 'Marcar como destacado'
    
    def unmark_as_featured(self, request, queryset):
        queryset.update(is_featured=False)
        messages.success(request, f'{queryset.count()} comentario(s) desmarcado(s) como destacado(s)')
    unmark_as_featured.short_description = 'Desmarcar como destacado'

class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'ip_address', 'reaction', 'created_on')
    list_filter = ('is_like', 'created_on')
    search_fields = ('post__title', 'ip_address')
    readonly_fields = ('created_on',)
    
    def reaction(self, obj):
        return '👍 Like' if obj.is_like else '👎 Dislike'
    reaction.short_description = 'Reacción'

# Personalizar el admin site
admin.site.site_header = "Blog Lucas Barba - Admin"
admin.site.site_title = "Blog Admin"
admin.site.index_title = "Panel de Administración"

admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PostLike, PostLikeAdmin)