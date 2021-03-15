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
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.user
        )
        cls.templates_page_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts', args=[cls.group.slug]),
            'new.html': reverse('new_post')
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for template, reverse_name in PostPagesTest.templates_page_names.items():
            with self.subTest(template=template):
                response = PostPagesTest.authorized_client.get(
                    reverse_name
                )
                self.assertTemplateUsed(response, template)

    def test_new_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = PostPagesTest.authorized_client.get(
            reverse('new_post')
        )
        for value, expected in PostPagesTest.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_index_page_list_is_1(self):
        """На страницу с постами передаётся ожидаемое количество объектов."""
        response = PostPagesTest.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get(
            'page'
        ).object_list), 1)

    def test_group_page_list_is_1(self):
        """На страницу с постами передаётся ожидаемое количество объектов."""
        response = PostPagesTest.authorized_client.get(
            reverse('group_posts', args=[PostPagesTest.group.slug])
        )
        correct_group = response.context.get(
            'page'
        ).object_list[0].group.title
        self.assertEqual(len(response.context.get('page').object_list), 1)
        self.assertEqual(correct_group, 'test_group')

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = PostPagesTest.authorized_client.get(reverse('index'))

        post = PostPagesTest.post
        response_post = response.context.get('page').object_list[0]
        self.assertEqual(post, response_post)


    def test_group_slug_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = PostPagesTest.authorized_client.get(
            reverse('group_posts', args=[PostPagesTest.group.slug])
        )
        post = PostPagesTest.post
        response_post = response.context.get('page').object_list[0]
        self.assertEqual(post, response_post)



class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text=f'test_post{i}',
                group=cls.group,
                author=cls.user
            )

        cls.list1 = {
            1: reverse('index'),
            2: reverse('group_posts', args=[cls.group.slug])
        }

    def test_first_page_containse_ten_records(self):
        for i in PaginatorViewsTest.list1.keys():
            with self.subTest(i=i):
                response = self.client.get(self.list1[i])
                self.assertEqual(len(response.context.get(
                    'page'
                ).object_list), 10)

    def test_second_page_containse_three_records(self):
        for i in PaginatorViewsTest.list1.keys():
            with self.subTest(i=i):
                response = self.client.get(self.list1[i] + '?page=2')
                self.assertEqual(len(response.context.get(
                    'page'
                ).object_list), 3)
