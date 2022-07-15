from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

User = get_user_model()


class PostsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='LucyTestContext')
        cls.user_second = User.objects.create_user(username='MikeTestContex')
        cls.group = Group.objects.create(
            title='LucyTestGroupContext',
            slug='TestovayaGroupContext',
            description='Эта группа создана для тестирования context'
        )
        cls.group_other = Group.objects.create(
            title='MikeTestGroupContext',
            slug='MikeTestovayaGroupContext',
            description='Эта группа Mike создана для тестирования context'
        )
        cls.post = Post.objects.create(
            text='1 Тестовый текст пост',
            group=cls.group,
            author=cls.user
        )
        cls.index = (
            'posts:index',
            'posts/index.html',
            None)
        cls.group_list = (
            'posts:grouppa',
            'posts/group_list.html',
            [cls.group.slug]
        )
        cls.group_list_other = (
            'posts:grouppa',
            'posts/group_list.html',
            [cls.group_other.slug]
        )
        cls.profile = (
            'posts:profile',
            'posts/profile.html',
            [cls.user.username]
        )
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
        cls.page_obj = Post.objects.all()
        cls.ass_urls = (
            cls.index, cls.group_list, cls.profile,
            cls.detail, cls.edit, cls.create
        )

    @classmethod
    def setUp(cls):
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_second = Client()
        cls.authorized_client_second.force_login(cls.user_second)
        cls.post_author = Client()
        cls.post_author.force_login(cls.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for route, template, args in self.ass_urls:
            with self.subTest(route=route):
                response = self.post_author.get(
                    reverse(route, args=args)
                )
                self.assertTemplateUsed(response, template)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильными типами полей."""
        """Форма создания поста"""
        app_route, template, args_url = self.create
        response = self.authorized_client.get(
            reverse(app_route)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(
                    value
                )
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон edit_post сформирован с правильными типами полей."""
        """Форма редактирования поста"""
        app_route, template, args_url = self.edit
        response = self.post_author.get(
            reverse(app_route, args=args_url)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(
                    value
                )
                self.assertIsInstance(form_field, expected)
        self.assertEqual(
            response.context.get('post_selected').text,
            self.post.text
        )
        self.assertEqual(
            response.context.get('post_selected').group.title,
            self.group.title
        )

    def check_context(self, id, text, author, group, group_slug):
        self.assertEqual(id, self.post.id,)
        self.assertEqual(text, self.post.text,)
        self.assertEqual(author, self.post.author.username,)
        self.assertEqual(group, self.post.group.id)
        self.assertEqual(group_slug, self.post.group.slug)

    def index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        """Список постов с сортировкой от новых к старым"""
        app_route, template, args_url = self.index
        response = self.authorized_client.get(
            reverse(app_route)
        )
        first_post = len(self.page_obj) - 1
        first_object = response.context['page_obj'][first_post]
        self.check_context(
            first_object.id,
            first_object.text,
            first_object.author.username,
            first_object.group.id,
            first_object.group.slug
        )

    def test_group_posts_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        """Список постов Группы"""
        app_route, template, args_url = self.group_list
        response = self.authorized_client.get(
            reverse(app_route, args=args_url)
        )
        self.assertEqual(
            response.context.get('group').title,
            self.group.title
        )
        self.assertEqual(
            response.context.get('group').slug,
            self.group.slug
        )
        self.assertEqual(
            response.context.get('group').description,
            self.group.description
        )

    def test_profile_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        """Список постов пользователя"""
        app_route, template, args_url = self.profile
        response = self.authorized_client.get(
            reverse(app_route, args=args_url)
        )
        first_post = len(self.page_obj) - 1
        first_object = response.context['page_obj'][first_post]
        self.assertEqual(
            response.context.get('author').username,
            self.post.author.username
        )
        self.assertTrue(
            response.context.get('is_profile')
        )
        self.check_context(
            first_object.id,
            first_object.text,
            first_object.author.username,
            first_object.group.id,
            first_object.group.slug
        )

    def test_post_exist_index(self):
        """Проверяем что пост появился на странице постов"""
        app_route, template, args_url = self.index
        response = self.authorized_client.get(
            reverse(app_route)
        )
        all_posts = response.context['page_obj']
        first_post = len(all_posts.object_list) - 1
        self.check_context(
            all_posts.object_list[first_post].id,
            all_posts.object_list[first_post].text,
            all_posts.object_list[first_post].author.username,
            all_posts.object_list[first_post].group.id,
            all_posts.object_list[first_post].group.slug
        )

    def test_post_exist_group_page(self):
        """Проверяем, что пост появился на странице группы"""
        app_route, template, args_url = self.group_list
        response = self.authorized_client.get(
            reverse(app_route, args=args_url)
        )
        all_posts = response.context['posts']
        first_post = len(all_posts) - 1
        new_dict = {}
        new_dict['text'] = all_posts[first_post].text
        new_dict['group'] = all_posts[first_post].group.slug
        new_dict['author'] = all_posts[first_post].author.username
        self.assertEqual(
            new_dict['text'],
            self.page_obj.latest('-pub_date').text
        )
        self.assertEqual(
            new_dict['group'],
            self.page_obj.latest('-pub_date').group.slug
        )
        self.assertEqual(
            new_dict['author'],
            self.page_obj.latest('-pub_date').author.username
        )

    def test_post_exist_profile_page(self):
        """Проверяем что пост появился в профайле пользователя"""
        app_route, template, args_url = self.profile
        response = self.authorized_client.get(
            reverse(app_route, args=args_url)
        )
        all_posts = response.context['page_obj']
        self.assertIn(self.post, all_posts)
        self.assertEqual(
            response.context['author'].username,
            self.post.author.username
        )

    def test_post_not_exist_in_different_group_page(self):
        """Проверяем, что пост НЕ появился на странице не своей группы"""
        app_route, template, args_url = self.group_list_other
        response = self.authorized_client.get(
            reverse(app_route, args=args_url)
        )
        self.assertNotIn(self.post, response.context['posts'])
