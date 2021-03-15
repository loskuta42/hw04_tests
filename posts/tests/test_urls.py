from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='testuser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        cls.templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test-slug/',
            'new.html': '/new/'
        }

    def test_homepage(self):
        """Страница / доступна любому пользователю."""
        response = PostURLTests.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_slug(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = PostURLTests.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_new(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = PostURLTests.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, url in PostURLTests.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)


