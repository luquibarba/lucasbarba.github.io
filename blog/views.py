from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator
import json
import re
from blog.models import Post, Comment, Category, PostLike
from blog.forms import CommentForm

def get_client_ip(request):
    """Obtiene la IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def blog_index(request):
    """Vista principal del blog con búsqueda y paginación mejorada"""
    query = request.GET.get('search', '')
    posts = Post.objects.all().select_related().prefetch_related('categories')
    
    # Búsqueda avanzada
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query) |
            Q(categories__name__icontains=query)
        ).distinct()
    
    # Ordenamiento
    order_by = request.GET.get('order', '-created_on')
    if order_by in ['-created_on', '-views', '-likes', 'title']:
        posts = posts.order_by(order_by)
    
    categories = Category.objects.all()
    featured_posts = Post.objects.filter(featured=True)[:3]
    
    context = {
        "posts": posts,
        "categories": categories,
        "featured_posts": featured_posts,
        "search_query": query,
        "total_posts": Post.objects.count(),
        "total_views": sum(p.views for p in Post.objects.all()),
    }
    return render(request, "blog/index.html", context)

def blog_category(request, category):
    """Vista filtrada por categoría"""
    posts = Post.objects.filter(
        categories__name__icontains=category
    ).order_by("-created_on")
    
    categories = Category.objects.all()
    category_obj = Category.objects.filter(name__icontains=category).first()
    
    context = {
        "category": category,
        "category_obj": category_obj,
        "posts": posts,
        "categories": categories,
    }
    return render(request, "blog/index.html", context)

def blog_detail(request, pk):
    """Vista detallada del post con incremento de visualizaciones"""
    post = get_object_or_404(Post, pk=pk)
    
    # Incrementar visualizaciones
    post.increment_views()
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                author=form.cleaned_data["author"],
                body=form.cleaned_data["body"],
                post=post,
                ip_address=get_client_ip(request)
            )
            comment.save()
            return HttpResponseRedirect(request.path_info)
    
    comments = Comment.objects.filter(post=post).order_by('-is_featured', '-created_on')
    categories = Category.objects.all()
    
    # Obtener estado de like/dislike del usuario
    user_ip = get_client_ip(request)
    user_reaction = PostLike.objects.filter(post=post, ip_address=user_ip).first()
    
    context = {
        "post": post,
        "comments": comments,
        "form": CommentForm(),
        "posts": [post],
        "categories": categories,
        "user_reaction": user_reaction,
        "reading_time": post.get_reading_time(),
        "engagement_ratio": post.get_engagement_ratio(),
    }
    
    return render(request, "blog/index.html", context)

@csrf_exempt
@require_POST
def add_comment_ajax(request):
    """Vista AJAX mejorada para agregar comentarios"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        author = data.get('author', '').strip()
        body = data.get('body', '').strip()
        email = data.get('email', '').strip()
        
        # Validaciones
        if not all([post_id, author, body]):
            return JsonResponse({'error': 'Nombre y comentario son obligatorios'}, status=400)
        
        if len(body) > 1000:
            return JsonResponse({'error': 'El comentario no puede exceder 1000 caracteres'}, status=400)
        
        if len(author) > 60:
            return JsonResponse({'error': 'El nombre no puede exceder 60 caracteres'}, status=400)
        
        # Validar email si se proporciona
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return JsonResponse({'error': 'Email inválido'}, status=400)
        
        post = get_object_or_404(Post, pk=post_id)
        
        comment = Comment.objects.create(
            author=author,
            body=body,
            email=email,
            post=post,
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'author': comment.author,
                'body': comment.body,
                'email': comment.email,
                'date': comment.created_on.strftime('%d de %B de %Y a las %H:%M'),
                'is_featured': comment.is_featured
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

@csrf_exempt
@require_POST
def like_post_ajax(request):
    """Vista AJAX para manejar likes/dislikes"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        is_like = data.get('is_like')  # True para like, False para dislike
        
        if post_id is None or is_like is None:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)
        
        post = get_object_or_404(Post, pk=post_id)
        user_ip = get_client_ip(request)
        
        # Verificar si el usuario ya reaccionó
        existing_reaction = PostLike.objects.filter(post=post, ip_address=user_ip).first()
        
        if existing_reaction:
            # Si es la misma reacción, la eliminamos (toggle)
            if existing_reaction.is_like == is_like:
                existing_reaction.delete()
                # Decrementar contador
                if is_like:
                    post.likes = max(0, post.likes - 1)
                else:
                    post.dislikes = max(0, post.dislikes - 1)
                post.save()
                
                return JsonResponse({
                    'success': True,
                    'action': 'removed',
                    'likes': post.likes,
                    'dislikes': post.dislikes,
                    'user_reaction': None
                })
            else:
                # Cambiar reacción
                existing_reaction.is_like = is_like
                existing_reaction.save()
                
                # Ajustar contadores
                if is_like:
                    post.likes += 1
                    post.dislikes = max(0, post.dislikes - 1)
                else:
                    post.dislikes += 1
                    post.likes = max(0, post.likes - 1)
                post.save()
                
                return JsonResponse({
                    'success': True,
                    'action': 'changed',
                    'likes': post.likes,
                    'dislikes': post.dislikes,
                    'user_reaction': 'like' if is_like else 'dislike'
                })
        else:
            # Nueva reacción
            PostLike.objects.create(post=post, ip_address=user_ip, is_like=is_like)
            
            if is_like:
                post.likes += 1
            else:
                post.dislikes += 1
            post.save()
            
            return JsonResponse({
                'success': True,
                'action': 'added',
                'likes': post.likes,
                'dislikes': post.dislikes,
                'user_reaction': 'like' if is_like else 'dislike'
            })
            
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

def get_post_data_ajax(request, pk):
    """Vista AJAX mejorada para obtener datos completos del post"""
    try:
        post = get_object_or_404(Post, pk=pk)
        
        # Incrementar visualizaciones
        post.increment_views()
        
        comments = Comment.objects.filter(post=post).order_by('-is_featured', '-created_on')
        
        comments_data = [{
            'id': comment.id,
            'author': comment.author,
            'body': comment.body,
            'email': comment.email,
            'date': comment.created_on.strftime('%d de %B de %Y a las %H:%M'),
            'is_featured': comment.is_featured
        } for comment in comments]
        
        categories_data = [{
            'name': cat.name,
            'color': cat.color,
            'icon': cat.icon
        } for cat in post.categories.all()]
        
        # Obtener reacción del usuario
        user_ip = get_client_ip(request)
        user_reaction = PostLike.objects.filter(post=post, ip_address=user_ip).first()
        user_reaction_type = None
        if user_reaction:
            user_reaction_type = 'like' if user_reaction.is_like else 'dislike'
        
        return JsonResponse({
            'id': post.id,
            'title': post.title,
            'body': post.body,
            'image': post.image.url if post.image else None,
            'date': post.created_on.strftime('%d de %B de %Y'),
            'categories': categories_data,
            'comments': comments_data,
            'likes': post.likes,
            'dislikes': post.dislikes,
            'views': post.views,
            'reading_time': post.get_reading_time(),
            'engagement_ratio': post.get_engagement_ratio(),
            'user_reaction': user_reaction_type,
            'featured': post.featured
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

@csrf_exempt
def search_posts_ajax(request):
    """Vista AJAX para búsqueda en tiempo real"""
    try:
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query) |
            Q(categories__name__icontains=query)
        ).distinct()[:10]
        
        results = [{
            'id': post.id,
            'title': post.title,
            'excerpt': post.body[:100] + '...' if len(post.body) > 100 else post.body,
            'categories': [cat.name for cat in post.categories.all()],
            'date': post.created_on.strftime('%d/%m/%Y'),
            'views': post.views,
            'likes': post.likes
        } for post in posts]
        
        return JsonResponse({'results': results})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)