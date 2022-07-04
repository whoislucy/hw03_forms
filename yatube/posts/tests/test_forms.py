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
        i = 0
        for i in range(3):
            Post.objects.create(
                text=str(i) + ' Тестовый текст пост',
                group=cls.group,
                author=cls.user_author
            )
        cls.post = Post.objects.get(id=1)
        cls.form = PostForm()
        cls.all_posts = Post.objects.all()
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
        cls.page_obj = Post.objects.all()

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
        self.assertEqual(self.all_posts.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text='Тестовый текст от LucyTesterForm',
            ).exists()
        )
        last_object = self.all_posts.first()
        fields_dict = {
            last_object.author.username: self.user.username,
            last_object.text: form_data['text'],
            last_object.group.id: self.group.id
        }
        for field, expected in fields_dict.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_edit_post(self):
        """Проверяем, что происходит изменение поста"""
        for url in self.ass_urls:
            app_route = url[0]
            args_url = url[2]
            if app_route == 'posts:post_edit':
                response = self.post_author.get(
                    reverse(app_route, args=args_url)
                )
                author_post = response.context['post_selected']
                author_post.text = 'UPD 1 Тестовый текст пост'
                upd_form_data = {
                    'text': author_post.text,
                    'group': author_post.group.id
                }
                response = self.post_author.post(
                    reverse(app_route, args=args_url),
                    data=upd_form_data,
                    follow=True
                )
                self.assertEqual(
                    author_post.text,
                    self.all_posts.last().text
                )
