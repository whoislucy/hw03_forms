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
            None,
            '/',
            None)
        cls.group_list = (
            'posts:grouppa',
            'posts/group_list.html',
            [cls.group.slug],
            f'/group/{cls.group.slug}/',
            None
        )
        cls.profile = (
            'posts:profile',
            'posts/profile.html',
            [cls.user.username],
            f'/profile/{cls.post.author}/',
            None
        )
        cls.detail = (
            'posts:post_detail',
            'posts/post_detail.html',
            [cls.post.id],
            f'/posts/{cls.post.id}/',
            None
        )
        cls.edit = (
            'posts:post_edit',
            'posts/create_post.html',
            [cls.post.id],
            f'/posts/{cls.post.id}/edit/',
            'author_user'
        )
        cls.create = (
            'posts:post_create',
            'posts/create_post.html',
            None,
            f'/posts/{cls.post.id}/edit/',
            'autorized'
        )
        cls.ass_urls = (
            cls.index, cls.group_list, cls.profile,
            cls.detail, cls.edit, cls.create
        )

    def setUp(self):
        """Создаем неавторизованный клиент, создаем пользователей"""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_author = User.objects.get(username='LucyTestName')
        self.post_author = Client()
        self.post_author.force_login(self.user)

    def test_unexisting_page(self):
        """Страница unexisting_page вернет ошибку 404"""
        response = self.guest_client.get('/unexistint_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_all(self):
        """Проверяем общедоступные страницы"""
        for route, template, args, address, autorized in self.ass_urls:
            with self.subTest(address=address):
                if autorized is None:
                    response = self.guest_client.get(address)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_autorized(self):
        """Проверяем доступность страниц для авторизованного пользователя"""
        create_data = {
            'route': self.create[0]
        }
        response = self.authorized_client.get(
            reverse(create_data['route'])
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_edit(self):
        """Проверка редактирования поста автором"""
        edit_data = {
            'route': self.edit[0],
            'args': self.edit[2]
        }
        response = self.post_author.get(
            reverse(edit_data['route'], args=edit_data['args'])
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_all_uses_correct_template_(self):
        """URL-адрес использует соответствующий шаблон."""
        for route, template, args, address, autorized in self.ass_urls:
            with self.subTest(address=address):
                if autorized == "author_user" and route == "posts:post_edit":
                    response = self.post_author.get(
                        address,
                        follow=True
                    )
                    self.assertTemplateUsed(response, template)
                elif autorized == 'autorized' and route != 'posts:post_edit':
                    response = self.authorized_client.get(
                        address,
                        follow=True
                    )
                    self.assertTemplateUsed(response, template)
                elif autorized is None:
                    response = self.guest_client.get(
                        address,
                        follow=True
                    )
                    self.assertTemplateUsed(response, template)
