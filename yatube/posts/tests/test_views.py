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
        cls.group2 = Group.objects.create(
            title='MikeTestGroupContext',
            slug='MikeTestovayaGroupContext',
            description='Эта группа Mike создана для тестирования context'
        )
        i = 0
        for i in range(3):
            i += 1
            Post.objects.create(
                text=str(i) + ' Тестовый текст пост',
                group=cls.group,
                author=cls.user
            )
        cls.post = Post.objects.get(id=1)
        cls.index = (
            'posts:index',
            'posts/index.html',
            None)
        cls.group_list = (
            'posts:grouppa',
            'posts/group_list.html',
            [cls.group.slug]
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
        cls.authorized_client.force_login(cls.user_second)
        cls.post_author = User.objects.get(username='LucyTestContext')
        cls.post_author = Client()
        cls.post_author.force_login(cls.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url in self.ass_urls:
            app_route = url[0]
            template = url[1]
            args_url = url[2]
            with self.subTest(app_route=app_route):
                response = self.post_author.get(
                    reverse(app_route, args=args_url)
                )
                self.assertTemplateUsed(response, template)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильными типами полей."""
        """Форма создания поста"""
        for url in self.ass_urls:
            app_route = url[0]
            if app_route == 'posts:post_create':
                response = self.authorized_client.get(reverse(app_route))
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
        for url in self.ass_urls:
            app_route = url[0]
            args_url = url[2]
            if app_route == 'posts:post_edit':
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

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        """Список постов с сортировкой от новых к старым"""
        for url in self.ass_urls:
            app_route = url[0]
            if app_route == 'posts:index':
                response = self.authorized_client.get(reverse(app_route))
                first_post = len(self.page_obj) - 1
                first_object = response.context['page_obj'][first_post]
                task_text_0 = first_object.text
                task_author_0 = first_object.author.username
                self.assertEqual(task_text_0, self.post.text)
                self.assertEqual(task_author_0, self.post.author.username)

    def test_group_posts_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        """Список постов Группы"""
        for url in self.ass_urls:
            app_route = url[0]
            args_url = url[2]
            if app_route == 'posts:grouppa':
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
        for url in self.ass_urls:
            app_route = url[0]
            args_url = url[2]
            if app_route == 'posts:profile':
                response = self.authorized_client.get(
                    reverse(app_route, args=args_url)
                )
                self.assertEqual(
                    response.context.get('author').username,
                    self.post.author.username
                )
                self.assertTrue(
                    response.context.get('is_profile')
                )

    def test_post_exist_index(self):
        """Проверяем что пост появился на странице постов"""
        for url in self.ass_urls:
            app_route = url[0]
            if app_route == 'posts:index':
                response = self.authorized_client.get(reverse(app_route))
                all_posts = response.context['page_obj']
                new_dict = {}
                for new_post in all_posts:
                    if new_post.id == 1:
                        new_dict['text'] = new_post.text
                        new_dict['group'] = new_post.group.slug
                        new_dict['author'] = new_post.author.username
                self.assertEqual(
                    new_dict['text'],
                    self.post.text
                )
                self.assertEqual(new_dict['group'], self.group.slug)
                self.assertEqual(new_dict['author'], self.post.author.username)

    def test_post_exist_group_page(self):
        """Проверяем, что пост появился на странице группы"""
        for url in self.ass_urls:
            app_route = url[0]
            args_url = url[2]
            if app_route == 'posts:grouppa':
                response = self.authorized_client.get(
                    reverse(app_route, args=args_url)
                )
                all_posts = response.context['page_obj']
                new_dict = {}
                for post in all_posts:
                    if post.id == 1:
                        new_dict['text'] = post.text
                        new_dict['group'] = post.group.slug
                        new_dict['author'] = post.author.username
                self.assertEqual(
                    new_dict['text'],
                    self.post.text
                )
                self.assertEqual(new_dict['group'], self.group.slug)
                self.assertEqual(new_dict['author'], self.post.author.username)

    def test_post_exist_profile_page(self):
        """Проверяем что пост появился в профайле пользователя"""
        for url in self.ass_urls:
            app_route = url[0]
            args_url = url[2]
            if app_route == 'posts:profile':
                response = self.authorized_client.get(
                    reverse(app_route, args=args_url)
                )
                all_posts = response.context['page_obj']
                for post in all_posts:
                    if post.id == 1:
                        mine_post = post
                        self.assertIn(mine_post, all_posts)

    def test_post_not_exist_in_different_group_page(self):
        """Проверяем, что пост НЕ появился на странице не своей группы"""
        for url in self.ass_urls:
            app_route = url[0]
            args_url = url[2]
            if app_route == 'posts:profile':
                response = self.authorized_client_second.get(
                    reverse(app_route, args=args_url)
                )
                all_posts = response.context['page_obj']
                for post in all_posts:
                    if post.id != 1:
                        mine_post = False
                        self.assertNotIn(mine_post, all_posts)
