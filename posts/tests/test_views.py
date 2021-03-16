from django.test import TestCase, Client
from posts.models import Post, Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='test_author'
        )
        cls.auth_author_client = Client()
        cls.auth_author_client.force_login(cls.author)
        cls.not_author = User.objects.create_user(
            username='test_not_author'
        )
        cls.authorized_not_author_client = Client()
        cls.authorized_not_author_client.force_login(cls.not_author)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author
        )
        cls.templ_names = {
            reverse('index'): 'index.html',
            reverse(
                'group_posts',
                args=[cls.group.slug]
            ): 'group.html',
            reverse('new_post'): 'new.html',
            reverse('post_edit',
                    kwargs={
                        'username': cls.author.username,
                        'post_id': cls.post.pk
                    }
                    ): 'new.html',
            reverse('profile',
                    args=[cls.author.username]
                    ): 'profile.html',
            reverse('post',
                    kwargs={
                        'username': cls.author.username,
                        'post_id': cls.post.pk
                    }
                    ): 'post.html',
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for reverse_name, template in PostPagesTest.templ_names.items():
            with self.subTest(template=template):
                response = PostPagesTest.auth_author_client.get(
                    reverse_name
                )
                self.assertTemplateUsed(response, template)

    def test_new_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = PostPagesTest.auth_author_client.get(
            reverse('new_post')
        )
        response_title = response.context.get('title')
        response_button = response.context.get('button')
        for value, expected in PostPagesTest.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response_title, 'Новая запись')
        self.assertEqual(response_button, 'Создать новую запись')

    def test_index_page_list_is_1(self):
        """На страницу index передаётся ожидаемое количество объектов."""
        response = PostPagesTest.auth_author_client.get(reverse('index'))
        self.assertEqual(len(response.context.get(
            'page'
        ).object_list), 1)

    def test_group_page_list_is_1(self):
        """На страницу group передаётся ожидаемое количество объектов."""
        response = PostPagesTest.auth_author_client.get(
            reverse('group_posts', args=[PostPagesTest.group.slug])
        )
        correct_post = response.context.get(
            'page'
        ).object_list[0]
        self.assertEqual(len(response.context.get('page').object_list), 1)
        self.assertEqual(correct_post, PostPagesTest.post)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = PostPagesTest.guest_client.get(reverse('index'))
        post = PostPagesTest.post
        response_post = response.context.get('page').object_list[0]
        self.assertEqual(post, response_post)

    def test_index_show_correct_profile(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = PostPagesTest.guest_client.get(
            reverse('profile', args=[PostPagesTest.author.username])
        )
        post = PostPagesTest.post
        author = PostPagesTest.author
        response_post = response.context.get('page').object_list[0]
        response_author = response.context.get('author')
        response_count = response.context.get('count')
        self.assertEqual(post, response_post)
        self.assertEqual(author, response_author)
        self.assertEqual(1, response_count)

    def test_index_show_correct_post_view(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = PostPagesTest.guest_client.get(
            reverse(
                'post',
                kwargs={
                    'username': PostPagesTest.author.username,
                    'post_id': PostPagesTest.post.pk
                }
            )
        )
        post = PostPagesTest.post
        author = PostPagesTest.author
        response_post = response.context.get('post')
        response_author = response.context.get('author')
        response_count = response.context.get('count')
        self.assertEqual(post, response_post)
        self.assertEqual(author, response_author)
        self.assertEqual(1, response_count)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = PostPagesTest.auth_author_client.get(
            reverse('post_edit',
                    kwargs={
                        'username': PostPagesTest.author.username,
                        'post_id': PostPagesTest.post.pk
                    }
                    )
        )
        response_title = response.context.get('title')
        response_button = response.context.get('button')
        for value, expected in PostPagesTest.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response_title, 'Редактировать запись')
        self.assertEqual(response_button, 'Сохранить запись')

    def test_group_slug_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = PostPagesTest.auth_author_client.get(
            reverse('group_posts', args=[PostPagesTest.group.slug])
        )
        post = PostPagesTest.post
        response_post = response.context.get('page').object_list[0]
        self.assertEqual(post, response_post)

    def test_about_author_use_correct_view(self):
        """Шаблон author использует корректный view."""
        response = PostPagesTest.guest_client.get(
            reverse('about:author')
        )
        response_author = response.context.get('author')
        response_github = response.context.get('github')
        self.assertEqual(
            response_author,
            'Автор проекта - Алексей Лобарев.'
        )
        self.assertEqual(
            response_github,
            '<a href="https://github.com/loskuta42/">'
            'Ссылка на github</a>'
        )

    def test_about_tech_use_correct_view(self):
        """Шаблон tech использует корректный view."""
        response = PostPagesTest.guest_client.get(
            reverse('about:tech')
        )
        response_pycharm = response.context.get('pycharm')
        response_tech = response.context.get('tech')
        self.assertEqual(
            response_pycharm,
            'Сайт написан при использовании Pycharm.'
        )
        self.assertEqual(
            response_tech,
            'А так же модели, формы, декораторы и многое другое'
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text=f'test_post{i}',
                group=cls.group,
                author=cls.author
            )

        cls.templates = {
            1: reverse('index'),
            2: reverse('group_posts', args=[cls.group.slug]),
            3: reverse('profile', args=[cls.author.username])
        }

    def test_first_page_contains_ten_records(self):
        """Paginator предоставляет ожидаемое количество постов
         на первую страницую"""
        for i in PaginatorViewsTest.templates.keys():
            with self.subTest(i=i):
                response = self.client.get(self.templates[i])
                self.assertEqual(len(response.context.get(
                    'page'
                ).object_list), 10)

    def test_second_page_contains_three_records(self):
        """Paginator предоставляет ожидаемое количество постов
         на вторую страницую"""
        for i in PaginatorViewsTest.templates.keys():
            with self.subTest(i=i):
                response = self.client.get(self.templates[i] + '?page=2')
                self.assertEqual(len(response.context.get(
                    'page'
                ).object_list), 3)
