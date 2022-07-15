from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='LucyTesterForm')
        cls.user_author = User.objects.create_user(username='LucyTestAuthor')
        cls.group = Group.objects.create(
            title='LucyFormTesterGroup_titles',
            slug='LucyFormTesterGroup_slug',
            description='Эта группа создана для тестирования Form'
        )
        cls.post = Post.objects.create(
            text='1 Тестовый текст пост',
            group=cls.group,
            author=cls.user_author
        )
        cls.form = PostForm()
        cls.detail = (
            'posts:post_detail',
            'posts/post_detail.html',
            [cls.post.id]
        )
        cls.edit = (
            'posts:post_edit',
            'posts/create_post.html',
            [cls.post.id]
        )
        cls.create = (
            'posts:post_create',
            'posts/create_post.html',
            None
        )
        cls.ass_urls = (
            cls.detail, cls.edit
        )

    @classmethod
    def setUp(cls):
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post_author = User.objects.get(username='LucyTestAuthor')
        cls.post_author = Client()
        cls.post_author.force_login(cls.user_author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст от LucyTesterForm',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)

    def test_edit_post(self):
        """Проверяем, что происходит изменение поста"""
        app_route, template, args_url = self.edit
        response = self.post_author.get(
            reverse(app_route, args=args_url)
        )
        author_post = response.context['post_selected']
        upd_form_data = {
            'text': 'UPD 1 Тестовый текст пост',
            'group': author_post.group.id,
            'post_author': self.user_author.username
        }
        response = self.post_author.post(
            reverse(app_route, args=args_url),
            data=upd_form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            )
        )

    def test_fields_created_post(self):
        """Тестируем что поля нового поста сохранились"""
        app_route, template, args_url = self.create
        form_data = {
            'text': 'Самый новый тестовый текст от LucyTesterForm',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse(app_route),
            data=form_data,
            follow=True
        )
        last_object = Post.objects.first()
        fields_dict = {
            last_object.author.username: self.user.username,
            last_object.text: form_data['text'],
            last_object.group.id: self.group.id
        }
        for field, expected in fields_dict.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_fields_updates_post(self):
        """Тестируем что поля проапдеченного поста сохранились"""
        app_route, template, args_url = self.edit
        response = self.post_author.get(
            reverse(app_route, args=args_url)
        )
        author_post = response.context['post_selected']
        upd_form_data = {
            'text': 'UPD 1 Тестовый текст пост',
            'group': author_post.group.id,
            'post_author': self.user_author.username
        }
        response = self.post_author.post(
            reverse(app_route, args=args_url),
            data=upd_form_data,
            follow=True
        )
        edited_post = Post.objects.last()
        fields_dict = {
            edited_post.author.username: self.user_author.username,
            edited_post.text: upd_form_data['text'],
            edited_post.group.id: self.group.id
        }
        for field, expected in fields_dict.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)
