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
        cls.group = Group.objects.create(
            title='LucyFormTesterGroup_titles',
            slug='LucyFormTesterGroup_slug',
            description='Эта группа создана для тестирования Form'
        )
        cls.form = PostForm()

    @classmethod
    def setUp(cls):
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст от LucyTesterForm',
            'group': 'LucyFormTesterGroup_titles',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        print('self.user.username', self.user.username)
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:profile', self.user.username)
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                group='LucyFormTesterGroup_titles',
                text='Тестовый текст от LucyTesterForm',
            ).exists()
        )
