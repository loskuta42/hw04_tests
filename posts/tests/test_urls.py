from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='test_author'
        )
        cls.authorized_author_client = Client()
        cls.authorized_author_client.force_login(cls.author)
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
            id=1,
            text='test_post',
            group=cls.group,
            author=cls.author
        )
        cls.templates_url_names = {
            '/': 'index.html',
            '/group/test-slug/': 'group.html',
            '/new/': 'new.html',
            '/test_author/1/edit/': 'new.html',
            '/test_author/': 'profile.html',
            '/test_author/1/': 'post.html'
        }

    def test_index(self):
        """Страница / доступна любому пользователю."""
        response = PostURLTests.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        """Страница /<username>/ доступна любому пользователю."""
        response = PostURLTests.guest_client.get('/test_author/')
        self.assertEqual(response.status_code, 200)

    def test_profile_post(self):
        """Страница /<username>/<post_id>/ доступна любому пользователю."""
        response = PostURLTests.guest_client.get('/test_author/1/')
        self.assertEqual(response.status_code, 200)

    def test_profile_post_edit_not_auth(self):
        """Страница /<username>/<post_id>/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = PostURLTests.guest_client.get(
            '/test_author/1/edit/',
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/test_author/1/edit/')

    def test_profile_post_edit_auth_not_author(self):
        """Страница /<username>/<post_id>/edit/ перенаправит
         авторизированного пользователя(не автора поста) на страницу поста.
        """
        response = PostURLTests.authorized_not_author_client.get(
            '/test_author/1/edit/',
            follow=True
        )
        self.assertRedirects(
            response, '/test_author/1/')

    def test_profile_post_edit_auth_author(self):
        """Страница /<username>/<post_id>/edit/ доступна
         автору поста.
        """
        response = PostURLTests.authorized_author_client.get(
            '/test_author/1/edit/'
        )
        self.assertEqual(response.status_code, 200)

    def test_group_slug(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = PostURLTests.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_new(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = PostURLTests.authorized_author_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_about_author(self):
        """Страница /about/author/ доступна любому пользователю."""
        response = PostURLTests.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech(self):
        """Страница /about/author/ доступна любому пользователю."""
        response = PostURLTests.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in PostURLTests.templates_url_names.items():
            with self.subTest(url=url):
                response = PostURLTests.authorized_author_client.get(url)
                self.assertTemplateUsed(response, template)


