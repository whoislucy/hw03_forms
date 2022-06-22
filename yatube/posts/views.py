from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User

POST_LIMIT = 10

post_list = Post.objects.prefetch_related('author').all()


def paginator(request):
    """"Добавляем пагинацию"""
    paginator = Paginator(post_list, POST_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Выводим список последних постов"""
    page_obj = paginator(request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Выводим содержание постов в конкретной группе"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator(request)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Выводим посты конкретного пользователя"""
    is_profile = True
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    count_posts = author_posts.count()
    paginator = Paginator(author_posts, POST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'posts': author_posts,
        'page_obj': page_obj,
        'count_posts': count_posts,
        'is_profile': is_profile
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Выводим конкретный пост пользователя"""
    post_selected = get_object_or_404(Post, id=post_id)
    author = post_selected.author
    author_posts = author.posts.all()
    count_author_posts = author_posts.count()
    context = {
        'post_selected': post_selected,
        'count_posts': count_author_posts
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Форма для публикации поста"""
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', post.author)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Форма редактирования поста"""
    is_edit = True
    post_selected = get_object_or_404(Post, id=post_id)
    if post_selected.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post_selected)
    context = {
        'is_edit': is_edit,
        'form': form,
        'post_selected': post_selected
    }
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:post_detail', post.id)
        return render(request, 'posts/create_post.html', context)
    return render(request, 'posts/create_post.html', context)
