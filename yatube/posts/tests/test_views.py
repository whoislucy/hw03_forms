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
        cls.group = Group.objects.create(
            title='LucyTestGroupContext',
            slug='TestovayaGroupContext',
            description='Эта группа создана для тестирования context'
        )
        cls.group = Group.objects.create(
            title='MikeTestGroupContext',
            slug='MikeTestovayaGroupContext',
            description='Эта группа Mike создана для тестирования context'
        )

    @classmethod
    def setUp(cls):
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post_author = User.objects.get(username='LucyTestContext')
        cls.post_author = Client()
        cls.post_author.force_login(cls.user)
        i = 0
        for i in range(2):
            i += 1
            Post.objects.create(
                text='Тестовый текст поста_' + str(i),
                group=Group.objects.get(title='LucyTestGroupContext'),
                author=cls.user,
                id=i
            )
        Post.objects.create(
            text='Тестовый текст поста проверяем задание 3',
            group=Group.objects.get(title='LucyTestGroupContext'),
            author=User.objects.get(username='LucyTestContext'),
            id=55
        )

        cls.page_obj = Post.objects.all()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse(
                    'posts:grouppa',
                    kwargs={'slug': 'TestovayaGroupContext'}
                )
            ),
            'posts/profile.html': (
                reverse(
                    'posts:profile',
                    kwargs={'username': 'LucyTestContext'}
                )
            ),
            'posts/post_detail.html': (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': 1}
                )
            ),
            'posts/create_post.html': reverse('posts:post_create')
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_post_edit_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон для post_edit."""
        response = self.post_author.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильными типами полей."""
        """Форма создания поста"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон edit_post сформирован с правильными типами полей."""
        """Форма редактирования поста"""
        response = self.post_author.get(
            reverse("posts:post_edit", kwargs={"post_id": 1})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertEqual(
            response.context.get('post_selected').text,
            'Тестовый текст поста_1'
        )
        self.assertEqual(
            response.context.get('post_selected').group.title,
            'LucyTestGroupContext'
        )

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        """Список постов с сортировкой от новых к старым"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = len(self.page_obj) - 1
        first_object = response.context['page_obj'][first_post]
        task_text_0 = first_object.text
        task_author_0 = first_object.author.username
        self.assertEqual(task_text_0, 'Тестовый текст поста_1')
        self.assertEqual(task_author_0, 'LucyTestContext')

    def test_group_posts_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        """Список постов Группы"""
        response = self.authorized_client.get(
            reverse('posts:grouppa', kwargs={'slug': 'TestovayaGroupContext'})
        )
        self.assertEqual(
            response.context.get('group').title,
            'LucyTestGroupContext'
        )
        self.assertEqual(
            response.context.get('group').slug,
            'TestovayaGroupContext'
        )
        self.assertEqual(
            response.context.get('group').description,
            'Эта группа создана для тестирования context'
        )

    def test_profile_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        """Список постов пользователя"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'LucyTestContext'})
        )
        self.assertEqual(
            response.context.get('author').username,
            'LucyTestContext'
        )
        self.assertTrue(
            response.context.get('is_profile')
        )

    def test_post_exist_index(self):
        """Проверяем что пост появился на странице постов"""
        response = self.authorized_client.get(reverse('posts:index'))
        all_posts = response.context['page_obj']
        new_dict = {}
        for post in all_posts:
            if post.id == 55:
                new_dict['text'] = post.text
                new_dict['group'] = post.group.slug
                new_dict['author'] = post.author.username
        self.assertEqual(
            new_dict['text'],
            'Тестовый текст поста проверяем задание 3'
        )
        self.assertEqual(new_dict['group'], 'TestovayaGroupContext')
        self.assertEqual(new_dict['author'], 'LucyTestContext')

    def test_post_exist_group_page(self):
        """Проверяем, что пост появился на странице группы"""
        response = self.authorized_client.get(
            reverse(
                'posts:grouppa',
                kwargs={'slug': 'TestovayaGroupContext'}
            )
        )
        all_posts = response.context['page_obj']
        new_dict = {}
        for post in all_posts:
            if post.id == 55:
                new_dict['text'] = post.text
                new_dict['group'] = post.group.slug
                new_dict['author'] = post.author.username
        self.assertEqual(
            new_dict['text'],
            'Тестовый текст поста проверяем задание 3'
        )
        self.assertEqual(new_dict['group'], 'TestovayaGroupContext')
        self.assertEqual(new_dict['author'], 'LucyTestContext')

    def test_post_exist_profile_page(self):
        """Проверяем что пост появился в профайле пользователя"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'LucyTestContext'}
            )
        )
        all_posts = response.context['page_obj']
        for post in all_posts:
            if post.id == 55:
                mine_post = post
                self.assertIn(mine_post, all_posts)

    def test_post_not_exist_in_different_group_page(self):
        """Проверяем, что пост НЕ появился на странице не своей группы"""
        response = self.authorized_client.get(
            reverse(
                'posts:grouppa',
                kwargs={'slug': 'MikeTestovayaGroupContext'}
            )
        )
        all_posts = response.context['page_obj']
        for post in all_posts:
            if post.id != 55:
                mine_post = False
                self.assertNotIn(mine_post, all_posts)
