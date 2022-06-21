from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .forms import PostForm
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
    posts = group.posts.all()

    paginator = Paginator(posts, POST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Выводим посты конкретного пользователя"""
    is_profile = True
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
        'count_posts': count_posts,
        'is_profile': is_profile
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


@login_required
def post_create(request):
    """Форма для публикации поста"""
    if request.method == 'POST':
        form = PostForm(request.POST or None)
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
    post_id_selected = get_object_or_404(Post, id=post_id)
    if post_id_selected.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post_id_selected)
    context = {
        'is_edit': is_edit,
        'form': form,
        'post_id_selected': post_id_selected
    }
    if request.method == 'POST':
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.group = post_id_selected.group
            post.id = post_id_selected.id
            post.pub_date = post_id_selected.pub_date
            form.save()
            return redirect('posts:post_detail', post.id)
        return render(request, 'posts/create_post.html', context)
    return render(request, 'posts/create_post.html', context)
