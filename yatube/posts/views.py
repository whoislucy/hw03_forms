from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User

POST_LIMIT = 10

POST_LIST_AUTHOR = Post.objects.select_related('author').all()
POST_LIST_GROUP = Post.objects.select_related('group').all()
GROUP_LIST = Group.objects.all()
USER_LIST = User.objects.all()


def paginator(request, posts_category):
    """"Добавляем пагинацию"""
    paginator = Paginator(posts_category, POST_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)   


def index(request):
    """Выводим список последних постов"""
    page_obj = paginator(request, POST_LIST_AUTHOR)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Выводим содержание постов в конкретной группе"""
    group = get_object_or_404(GROUP_LIST, slug=slug)
    posts = POST_LIST_GROUP.filter(group=group)
    page_obj = paginator(request, posts)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Выводим посты конкретного пользователя"""
    is_profile = True
    author = get_object_or_404(USER_LIST, username=username)
    author_posts = POST_LIST_AUTHOR.filter(author=author)
    count_posts = author_posts.count()
    page_obj = paginator(request, author_posts)
    context = {
        'author': author,
        'page_obj': page_obj,
        'count_posts': count_posts,
        'is_profile': is_profile
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Выводим конкретный пост пользователя"""
    post_selected = get_object_or_404(POST_LIST_AUTHOR, id=post_id)
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
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Форма редактирования поста"""
    is_edit = True
    post_selected = get_object_or_404(POST_LIST_AUTHOR, id=post_id)
    if post_selected.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post_selected)
    context = {
        'is_edit': is_edit,
        'form': form,
        'post_selected': post_selected
    }
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:post_detail', post.id)
    return render(request, 'posts/create_post.html', context)
