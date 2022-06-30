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
            text='Тестовый текст поста id=55',
            group=Group.objects.get(title='LucyFormTesterGroup_titles'),
            author=User.objects.get(username='LucyTestAuthor'),
            id=55
        )

        cls.form = PostForm()
        cls.all_posts = Post.objects.all()

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
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': 'LucyTesterForm'}
            )
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text='Тестовый текст от LucyTesterForm',
            ).exists()
        )

    def test_edit_post(self):
        """Проверяем, что происходит изменение поста"""
        response = self.post_author.get(
            reverse('posts:post_edit', kwargs={'post_id': 55})
        )
        author_post = response.context['post_selected']
        author_post.text = 'UPDATED Тестовый текст поста id=55'
        upd_form_data = {
            'text': author_post.text,
            'group': author_post.group.id
        }

        # Отправляем POST-запрос
        response = self.post_author.post(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': 55}
            ),
            data=upd_form_data,
            follow=True
        )
        self.assertEqual(
            author_post.text,
            'UPDATED Тестовый текст поста id=55'
        )
