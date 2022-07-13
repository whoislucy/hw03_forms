from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

User = get_user_model()


class PaginatorViewsTest(TestCase):
    """Тестируем Паджинатор"""
    @classmethod
    def setUpClass(cls):
        """Здесь создаются базовые записи в БД"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='LucyTestPaginator')
        cls.group = Group.objects.create(
            title='LucyTestGroup',
            slug='Testovaya',
            description='Эта группа создана для тестирования'
        )
        cls.index = 'posts:index'
        for i in range(15):
            Post.objects.create(
                text=f'Тестовый текст поста_{str(i)}',
                group=Group.objects.get(title='LucyTestGroup'),
                author=cls.user
            )
        cls.page_obj = Post.objects.all()
        cls.limit_1_page = 10
        cls.limit_2_page = 5
        cls.page_num = 2

    @classmethod
    def setUp(cls):
        """Здесь создаются фикстуры: клиент и 15 тестовых записей."""
        cls.authorized_client = Client()

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        response = self.client.get(reverse(self.index))
        self.assertEqual(len(response.context['page_obj']), self.limit_1_page)

    def test_second_page_contains_five_records(self):
        """Проверка: на второй странице должно быть 5 постов."""
        response = self.client.get(
            f"{reverse('posts:index')}?page={self.page_num}"
        )
        self.assertEqual(len(response.context['page_obj']), self.limit_2_page)
