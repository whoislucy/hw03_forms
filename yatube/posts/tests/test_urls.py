from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

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

    def setUp(self):
        """Создаем неавторизованный клиент, создаем пользователей"""
        self.guest_client = Client()
        # Создаем пользователя
        # self.user = User.objects.create_user(username='LucyTestName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
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
        post = PostURLTests.post
        group = PostURLTests.group
        urls_not_autorized = (
            '/',
            f'/group/{group.slug}/',
            f'/profile/{post.author}/',
            f'/posts/{post.id}/',
        )
        for url in urls_not_autorized:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_autorized(self):
        """Проверяем доступность страниц для авторизованного пользователя"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_edit(self):
        """Проверка редактирования поста автором"""
        post = PostURLTests.post
        response = self.post_author.get(f'/posts/{post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_all_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post = PostURLTests.post
        group = PostURLTests.group
        templates_urls_not_autorized_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{group.slug}/',
            'posts/profile.html': f'/profile/{post.author}/',
            'posts/post_detail.html': f'/posts/{post.id}/',
        }
        for template, address in templates_urls_not_autorized_names.items():
            print('template', template)
            print('address', address)
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertTemplateUsed(response, template)

    def test_urls_autorized_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post = PostURLTests.post
        templates_urls_all_autorized_names = {
            'posts/create_post.html': f'/posts/{post.id}/edit/',
        }

        for template, address in templates_urls_all_autorized_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertTemplateUsed(response, template)
