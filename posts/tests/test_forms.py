from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='testuser')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.group_old = Group.objects.create(
            title='test_group_old',
            slug='test-slug-old',
            description='test_description'
        )
        cls.group_new = Group.objects.create(
            title='test_group_new',
            slug='test-slug-new',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group_old,
            author=cls.author
        )

    def test_create_post(self):
        """Проверка формы создания нового поста."""
        posts_count = Post.objects.count()
        group_field = PostFormTests.group_old.id
        form_data = {
            'text': 'test_new_post',
            'group': group_field,
        }
        response = PostFormTests.author_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group_old.id,
                text='test_new_post'
            ).exists()
        )

    def test_edit_post(self):
        """Проверка формы редактирования поста и изменение
        его в базе данных."""
        group_field_new = PostFormTests.group_new.id
        form_data = {
            'text': 'test_edit_post',
            'group': group_field_new,
        }
        response = PostFormTests.author_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': PostFormTests.author.username,
                    'post_id': PostFormTests.post.pk
                }

            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'post',
                kwargs={
                    'username': PostFormTests.author.username,
                    'post_id': PostFormTests.post.pk
                }
            )
        )
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group_new.id,
                text='test_edit_post'
            ).exists()
        )
        self.assertFalse(
            Post.objects.filter(
                group=PostFormTests.group_old.id,
                text='test_post'
            ).exists()
        )
