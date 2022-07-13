from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='LucyTestName')
        cls.group = Group.objects.create(
            title='Тестовая группа LucyTestName',
            slug='LucyGroupTest',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )
        cls.index = (
            'posts:index',
            'posts/index.html',
            None
        )
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
        cls.ass_urls = (
            cls.index, cls.group_list, cls.profile,
            cls.detail, cls.edit, cls.create
        )

        cls.ass_urls_not_autorized = [
            cls.index, cls.group_list, cls.profile,
            cls.detail
        ]
        cls.ass_urls_autorized = [
            cls.edit, cls.create
        ]
        cls.ass_urls_autorized_author = [
            cls.create
        ]

    def setUp(cls):
        """Создаем неавторизованный клиент, создаем пользователей"""
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post_author = Client()
        cls.post_author.force_login(cls.user)
        cls.client_types_urls = {
            cls.guest_client: cls.ass_urls_not_autorized,
            cls.authorized_client: cls.ass_urls_autorized,
            cls.post_author: cls.ass_urls_autorized_author
        }
        cls.client_common_types_urls = {
            cls.guest_client: cls.ass_urls_not_autorized,
            cls.authorized_client: cls.ass_urls_not_autorized,
            cls.post_author: cls.ass_urls_not_autorized
        }
        cls.client_autorized_urls = {
            cls.authorized_client: cls.ass_urls_autorized,
            cls.post_author: cls.ass_urls_autorized
        }
        cls.client_author_types_urls = {
            cls.post_author: cls.ass_urls_autorized
        }

    def test_unexisting_page(self):
        """Страница unexisting_page вернет ошибку 404"""
        for client, type_autorization in self.client_types_urls.items():
            response = client.get('/unexistint_page/')
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_all(self):
        """Проверяем общедоступные страницы"""
        for client, type_autorization in self.client_common_types_urls.items():
            for route, template, args in type_autorization:
                with self.subTest(route=route):
                    response = client.get(
                        reverse(route, args=args)
                    )
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_autorized(self):
        """Проверяем доступность страниц для авторизованного пользователя"""
        for client, type_autorization in self.client_autorized_urls.items():
            for route, template, args in type_autorization:
                with self.subTest(route=route):
                    response = client.get(
                        reverse(route, args=args)
                    )
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_edit(self):
        """Проверка редактирования поста автором"""
        for client, type_autorization in self.client_author_types_urls.items():
            for route, template, args in type_autorization:
                with self.subTest(route=route):
                    response = client.get(
                        reverse(route, args=args)
                    )
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_all_uses_correct_template_(self):
        """URL-адрес использует соответствующий шаблон."""
        for client, type_autorization in self.client_types_urls.items():
            for route, template, args in type_autorization:
                with self.subTest(route=route):
                    response = client.get(
                        reverse(route, args=args), follow=True
                    )
                    self.assertTemplateUsed(response, template)
