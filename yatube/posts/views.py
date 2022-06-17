from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Group, Post, User

POST_LIMIT = 10


def index(request):
    """Выводим список последних постов"""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Выводим содержание постов в конкретной группе"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:POST_LIMIT]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Выводим посты конкретного пользователя"""
    user_profile = get_object_or_404(User, username=username)
    author_post = Post.objects.filter(author=user_profile)
    count_posts = len(author_post)
    paginator = Paginator(author_post, POST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': user_profile,
        'posts': author_post,
        'page_obj': page_obj,
        'count_posts': count_posts
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Выводим конкретный пост пользователя"""
    post_id_selected = get_object_or_404(Post, id=post_id)
    author = post_id_selected.author
    author_post = Post.objects.filter(author=author)
    count_author_post = len(author_post)
    context = {
        'post_id_selected': post_id_selected,
        'count_posts': count_author_post
    }
    return render(request, 'posts/post_detail.html', context)
