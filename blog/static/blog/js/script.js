document.addEventListener("DOMContentLoaded", function () {
    // --- Configuración global ---
    let currentPostId = null;
    let searchTimeout = null;
    
    // --- Utilidades ---
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Mostrar con animación
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Ocultar después de 4 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 4000);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }

    // --- Navegación principal ---
    document.body.classList.add('loaded');
    
    const navDots = document.querySelectorAll('.nav-dot');
    const contentSections = document.querySelectorAll('.content-section');
    const mainContentWrapper = document.querySelector('.main-content-wrapper');
    const footer = document.querySelector('footer');
    const codeTypewriters = document.querySelector('.code-typewriters');

    let currentSectionIndex = 0;
    let isTransitioning = false;

    function showSection(index) {
        if (isTransitioning || index === currentSectionIndex) return;
        isTransitioning = true;

        contentSections[currentSectionIndex].classList.remove('active');
        navDots[currentSectionIndex].classList.remove('active');

        if (index === 0) {
            footer.classList.remove('small');
            if (codeTypewriters) codeTypewriters.classList.add('show-code-typewriters');
        } else {
            footer.classList.add('small');
            if (codeTypewriters) codeTypewriters.classList.remove('show-code-typewriters');
        }

        currentSectionIndex = index;
        contentSections[currentSectionIndex].classList.add('active');
        navDots[currentSectionIndex].classList.add('active');

        setTimeout(() => { isTransitioning = false; }, 800);
    }

    navDots.forEach((dot, index) => {
        dot.addEventListener('click', () => showSection(index));
    });

    // Navegación con scroll y teclado
    let lastScrollTime = 0;
    const scrollThreshold = 700;

    mainContentWrapper.addEventListener('wheel', (event) => {
        const currentTime = new Date().getTime();
        if (currentTime - lastScrollTime < scrollThreshold) return;
        lastScrollTime = currentTime;

        if (event.deltaY > 0 && currentSectionIndex < contentSections.length - 1) {
            showSection(currentSectionIndex + 1);
        } else if (event.deltaY < 0 && currentSectionIndex > 0) {
            showSection(currentSectionIndex - 1);
        }
        event.preventDefault();
    }, { passive: false });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'ArrowDown' || event.key === 'PageDown') {
            if (currentSectionIndex < contentSections.length - 1) {
                showSection(currentSectionIndex + 1);
                event.preventDefault();
            }
        } else if (event.key === 'ArrowUp' || event.key === 'PageUp') {
            if (currentSectionIndex > 0) {
                showSection(currentSectionIndex - 1);
                event.preventDefault();
            }
        }
    });

    showSection(0);

    // --- Carruseles (código simplificado del anterior) ---
    function initCarousel(wrapperSelector, itemSelector, prevBtnId, nextBtnId, dotsSelector) {
        const wrapper = document.querySelector(wrapperSelector);
        const items = document.querySelectorAll(itemSelector);
        const prevBtn = document.getElementById(prevBtnId);
        const nextBtn = document.getElementById(nextBtnId);
        const dots = document.querySelectorAll(dotsSelector);

        if (!wrapper || items.length === 0) return;

        let currentIndex = 0;

        function showSlide(index) {
            if (index < 0) currentIndex = items.length - 1;
            else if (index >= items.length) currentIndex = 0;
            else currentIndex = index;

            const width = items[0].offsetWidth;
            wrapper.style.transform = `translateX(${-currentIndex * width}px)`;

            dots.forEach((dot, idx) => dot.classList.toggle('active', idx === currentIndex));
        }

        if (prevBtn) prevBtn.addEventListener('click', () => showSlide(currentIndex - 1));
        if (nextBtn) nextBtn.addEventListener('click', () => showSlide(currentIndex + 1));
        
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => showSlide(index));
        });

        showSlide(0);
        window.addEventListener('resize', () => showSlide(currentIndex));
    }

    // Inicializar carruseles
    initCarousel('.about-wrapper', '.about-item', 'prevAbout', 'nextAbout', '.about-dot');
    initCarousel('.project-wrapper', '.project-item', 'prevProject', 'nextProject', '.project-dot');

    // --- Logo y modales básicos ---
    const logoLink = document.getElementById('logo-link');
    if (logoLink) {
        logoLink.addEventListener('click', function(event) {
            event.preventDefault();
            showSection(0);
        });
    }

    // Cerrar modales
    const closeButtons = document.querySelectorAll('.close-button');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.modal-backdrop').forEach(modal => {
                modal.classList.remove('show');
            });
            document.body.style.overflow = '';
        });
    });

    // --- Modal de contacto ---
    const googleButton = document.querySelector('.wrapper ul li.google a');
    const contactModal = document.getElementById('contactModal');

    if (googleButton && contactModal) {
        googleButton.addEventListener('click', function(event) {
            event.preventDefault();
            contactModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        });
    }

    // Formulario de contacto
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const formData = new FormData(contactForm);
            const name = formData.get('name');
            const email = formData.get('email');
            const message = formData.get('message');
            
            if (!name || !email || !message) {
                showNotification('Por favor, completa todos los campos.', 'error');
                return;
            }
            
            showNotification(`¡Formulario enviado correctamente! Gracias por tu mensaje, ${name}.`);
            contactModal.classList.remove('show');
            document.body.style.overflow = '';
            contactForm.reset();
        });
    }

    // --- Búsqueda en tiempo real ---
    const searchInput = document.getElementById('blog-search');
    const searchResults = document.getElementById('search-results');

    if (searchInput && searchResults) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                searchResults.innerHTML = '';
                searchResults.classList.remove('show');
                return;
            }
            
            searchTimeout = setTimeout(async () => {
                try {
                    const response = await fetch(`/blog/ajax/search/?q=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    
                    if (data.results && data.results.length > 0) {
                        searchResults.innerHTML = data.results.map(result => `
                            <div class="search-result-item" data-post-id="${result.id}">
                                <h4>${result.title}</h4>
                                <p>${result.excerpt}</p>
                                <div class="result-meta">
                                    <span><i class="fas fa-tags"></i> ${result.categories.join(', ')}</span>
                                    <span><i class="fas fa-eye"></i> ${formatNumber(result.views)}</span>
                                    <span><i class="fas fa-heart"></i> ${formatNumber(result.likes)}</span>
                                </div>
                            </div>
                        `).join('');
                        searchResults.classList.add('show');
                    } else {
                        searchResults.innerHTML = '<div class="no-results">No se encontraron resultados</div>';
                        searchResults.classList.add('show');
                    }
                } catch (error) {
                    console.error('Error en búsqueda:', error);
                }
            }, 300);
        });

        // Cerrar resultados al hacer clic fuera
        document.addEventListener('click', function(event) {
            if (!searchInput.contains(event.target) && !searchResults.contains(event.target)) {
                searchResults.classList.remove('show');
            }
        });
    }

    // --- Filtros del blog ---
    const categoryChips = document.querySelectorAll('.category-chip');
    const blogCards = document.querySelectorAll('.blog-card');

    categoryChips.forEach(chip => {
        chip.addEventListener('click', function(event) {
            event.preventDefault();
            
            categoryChips.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            
            blogCards.forEach(card => {
                const cardCategories = card.dataset.categories || '';
                
                if (filter === 'all' || cardCategories.includes(filter)) {
                    card.classList.remove('hidden');
                    card.style.display = 'block';
                } else {
                    card.classList.add('hidden');
                    setTimeout(() => {
                        if (card.classList.contains('hidden')) {
                            card.style.display = 'none';
                        }
                    }, 300);
                }
            });
        });
    });

    // --- Funciones AJAX ---
    async function loadPostData(postId) {
        try {
            const response = await fetch(`/blog/ajax/post/${postId}/`);
            const data = await response.json();
            
            if (response.ok) return data;
            throw new Error(data.error || 'Error al cargar el post');
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error al cargar los datos del post', 'error');
            return null;
        }
    }

    async function submitComment(postId, author, body, email) {
        try {
            const response = await fetch('/blog/ajax/add-comment/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    post_id: postId,
                    author: author,
                    body: body,
                    email: email
                })
            });

            const data = await response.json();
            
            if (response.ok) return data;
            throw new Error(data.error || 'Error al enviar el comentario');
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error al enviar el comentario: ' + error.message, 'error');
            return null;
        }
    }

    async function likePost(postId, isLike) {
        try {
            const response = await fetch('/blog/ajax/like-post/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    post_id: postId,
                    is_like: isLike
                })
            });

            const data = await response.json();
            
            if (response.ok) return data;
            throw new Error(data.error || 'Error al procesar reacción');
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error al procesar tu reacción', 'error');
            return null;
        }
    }

    // --- Modal de posts con likes/dislikes ---
    const postModal = document.getElementById('postModal');
    const postModalTitle = document.getElementById('modal-post-title');
    const postModalMeta = document.getElementById('modal-post-meta');
    const postModalBody = document.getElementById('modal-post-body');
    const postModalComments = document.getElementById('modal-post-comments');
    const toggleCommentsBtn = document.getElementById('toggle-comments-btn');
    const commentsWrapper = document.getElementById('comments-wrapper');

    // Abrir modal de post
    blogCards.forEach(card => {
        const readMoreBtn = card.querySelector('.blog-card-link');
        if (readMoreBtn) {
            readMoreBtn.addEventListener('click', async function(event) {
                event.preventDefault();
                event.stopPropagation();
                
                const postId = card.dataset.postId;
                currentPostId = postId;
                
                if (postModal) {
                    postModalTitle.textContent = 'Cargando...';
                    postModalBody.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Cargando contenido...</div>';
                    postModal.classList.add('show');
                    document.body.style.overflow = 'hidden';
                }
                
                const postData = await loadPostData(postId);
                
                if (postData) {
                    displayPostData(postData);
                }
            });
        }
        
        card.addEventListener('click', function(event) {
            if (!event.target.closest('.blog-card-link')) {
                const readMoreBtn = card.querySelector('.blog-card-link');
                if (readMoreBtn) readMoreBtn.click();
            }
        });
    });

    function displayPostData(postData) {
        postModalTitle.textContent = postData.title;
        
        // Meta información mejorada
        const categoriesHtml = postData.categories.map(cat => 
            `<span class="category-tag" style="background-color: ${cat.color};">
                <i class="${cat.icon}"></i> ${cat.name}
            </span>`
        ).join('');
        
        postModalMeta.innerHTML = `
            <div class="post-meta-grid">
                <div class="meta-item">
                    <i class="fas fa-calendar"></i> ${postData.date}
                </div>
                <div class="meta-item">
                    <i class="fas fa-clock"></i> ${postData.reading_time} min de lectura
                </div>
                <div class="meta-item">
                    <i class="fas fa-eye"></i> ${formatNumber(postData.views)} visualizaciones
                </div>
                <div class="meta-categories">
                    ${categoriesHtml}
                </div>
            </div>
        `;
        
        // Contenido del post
        let bodyContent = postData.body;
        if (postData.image) {
            bodyContent = `<img src="${postData.image}" alt="${postData.title}" class="post-main-image">` + bodyContent;
        }
        
        // Sistema de likes/dislikes
        const likesSection = `
            <div class="post-engagement">
                <div class="engagement-buttons">
                    <button class="like-btn ${postData.user_reaction === 'like' ? 'active' : ''}" 
                            data-type="like" data-post-id="${postData.id}">
                        <i class="fas fa-thumbs-up"></i>
                        <span class="count">${formatNumber(postData.likes)}</span>
                    </button>
                    <button class="dislike-btn ${postData.user_reaction === 'dislike' ? 'active' : ''}" 
                            data-type="dislike" data-post-id="${postData.id}">
                        <i class="fas fa-thumbs-down"></i>
                        <span class="count">${formatNumber(postData.dislikes)}</span>
                    </button>
                </div>
                <div class="engagement-info">
                    <div class="engagement-bar">
                        <div class="engagement-fill" style="width: ${postData.engagement_ratio}%"></div>
                    </div>
                    <span class="engagement-text">${postData.engagement_ratio}% positivo</span>
                </div>
            </div>
        `;
        
        postModalBody.innerHTML = likesSection + bodyContent.replace(/\n/g, '<br>');
        
        // Event listeners para likes/dislikes
        setupLikeButtons();
        
        updateCommentsDisplay(postData.comments);
    }

    function setupLikeButtons() {
        const likeButtons = document.querySelectorAll('.like-btn, .dislike-btn');
        
        likeButtons.forEach(button => {
            button.addEventListener('click', async function() {
                const isLike = this.classList.contains('like-btn');
                const postId = this.dataset.postId;
                
                // Animación de click
                this.style.transform = 'scale(0.95)';
                setTimeout(() => this.style.transform = 'scale(1)', 150);
                
                const result = await likePost(postId, isLike);
                
                if (result && result.success) {
                    // Actualizar contadores
                    document.querySelector('.like-btn .count').textContent = formatNumber(result.likes);
                    document.querySelector('.dislike-btn .count').textContent = formatNumber(result.dislikes);
                    
                    // Actualizar estados activos
                    document.querySelector('.like-btn').classList.toggle('active', result.user_reaction === 'like');
                    document.querySelector('.dislike-btn').classList.toggle('active', result.user_reaction === 'dislike');
                    
                    // Actualizar barra de engagement
                    const total = result.likes + result.dislikes;
                    const ratio = total > 0 ? (result.likes / total) * 100 : 0;
                    document.querySelector('.engagement-fill').style.width = ratio + '%';
                    document.querySelector('.engagement-text').textContent = ratio.toFixed(1) + '% positivo';
                    
                    // Mostrar notificación
                    const action = result.action === 'removed' ? 'eliminada' : 
                                 result.action === 'changed' ? 'cambiada' : 'agregada';
                    const reaction = isLike ? 'like' : 'dislike';
                    showNotification(`Reacción ${action}: ${reaction}`);
                }
            });
        });
    }

    // Toggle comentarios
    if (toggleCommentsBtn && commentsWrapper) {
        toggleCommentsBtn.addEventListener('click', function() {
            const isVisible = commentsWrapper.classList.contains('visible');
            
            if (isVisible) {
                commentsWrapper.classList.remove('visible');
                this.innerHTML = '<i class="fas fa-comments"></i> Ver Comentarios';
                this.setAttribute('aria-expanded', 'false');
            } else {
                commentsWrapper.classList.add('visible');
                this.innerHTML = '<i class="fas fa-comments"></i> Ocultar Comentarios';
                this.setAttribute('aria-expanded', 'true');
            }
        });
    }

    function updateCommentsDisplay(comments = []) {
        if (!postModalComments) return;
        
        const commentsHtml = `
            <div class="comment-form-container">
                <h3><i class="fas fa-comment-dots"></i> Deja tu comentario:</h3>
                <form class="comment-form" id="server-comment-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Nombre *</label>
                            <input type="text" name="author" required placeholder="Tu nombre" maxlength="60">
                        </div>
                        <div class="form-group">
                            <label>Email (opcional)</label>
                            <input type="email" name="email" placeholder="tu@email.com">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Comentario *</label>
                        <div class="textarea-container">
                            <textarea name="body" rows="4" required placeholder="Escribe tu comentario aquí..." 
                                      maxlength="1000" class="comment-textarea"></textarea>
                            <div class="char-count">
                                <span class="current">0</span> / <span class="max">1000</span>
                            </div>
                        </div>
                    </div>
                    <button type="submit" class="submit-comment-btn">
                        <i class="fas fa-paper-plane"></i> Enviar Comentario
                    </button>
                </form>
            </div>
            <div class="comments-list-container">
                <h3 class="comments-title">
                    <i class="fas fa-comments"></i> 
                    Comentarios (${comments.length})
                </h3>
                <div class="comments-list">
                    ${comments.length > 0 ? 
                        comments.map(comment => `
                            <div class="comment ${comment.is_featured ? 'featured' : ''}">
                                ${comment.is_featured ? '<div class="featured-badge"><i class="fas fa-star"></i> Destacado</div>' : ''}
                                <div class="comment-header">
                                    <div class="comment-author">
                                        <i class="fas fa-user"></i>
                                        <strong>${comment.author}</strong>
                                        ${comment.email ? '<i class="fas fa-envelope verified-email" title="Email verificado"></i>' : ''}
                                    </div>
                                    <span class="comment-date">
                                        <i class="fas fa-clock"></i>
                                        ${comment.date}
                                    </span>
                                </div>
                                <p class="comment-body">${comment.body}</p>
                            </div>
                        `).join('') :
                        `<div class="no-comments">
                            <i class="fas fa-comment-slash"></i>
                            <p>No hay comentarios aún. ¡Sé el primero en comentar!</p>
                        </div>`
                    }
                </div>
            </div>
        `;
        
        postModalComments.innerHTML = commentsHtml;
        
        // Contador de caracteres para comentarios
        const textarea = document.querySelector('.comment-textarea');
        const currentCount = document.querySelector('.char-count .current');
        
        if (textarea && currentCount) {
            textarea.addEventListener('input', function() {
                const length = this.value.length;
                currentCount.textContent = length;
                
                // Cambiar color según límite
                if (length > 900) {
                    currentCount.style.color = '#dc3545';
                } else if (length > 750) {
                    currentCount.style.color = '#ffc107';
                } else {
                    currentCount.style.color = '#28a745';
                }
            });
        }
        
        // Formulario de comentarios
        const serverCommentForm = document.getElementById('server-comment-form');
        if (serverCommentForm) {
            serverCommentForm.addEventListener('submit', async function(event) {
                event.preventDefault();
                
                const formData = new FormData(serverCommentForm);
                const author = formData.get('author').trim();
                const body = formData.get('body').trim();
                const email = formData.get('email').trim();
                
                if (!author || !body) {
                    showNotification('Nombre y comentario son obligatorios', 'error');
                    return;
                }
                
                if (body.length > 1000) {
                    showNotification('El comentario no puede exceder 1000 caracteres', 'error');
                    return;
                }
                
                const submitBtn = serverCommentForm.querySelector('.submit-comment-btn');
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
                submitBtn.disabled = true;
                
                const result = await submitComment(currentPostId, author, body, email);
                
                if (result && result.success) {
                    const updatedPostData = await loadPostData(currentPostId);
                    if (updatedPostData) {
                        updateCommentsDisplay(updatedPostData.comments);
                    }
                    showNotification('¡Comentario agregado exitosamente!');
                }
                
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        }
    }

    // --- Cerrar modales con Escape ---
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelectorAll('.modal-backdrop').forEach(modal => {
                modal.classList.remove('show');
            });
            document.body.style.overflow = '';
        }
    });

    // --- Animaciones de entrada para las tarjetas ---
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.blog-card, .card').forEach(card => {
        observer.observe(card);
    });
});