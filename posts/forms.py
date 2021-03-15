from django.contrib.auth import get_user_model
from django.forms import ModelForm
from .models import Post

User = get_user_model()


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        # labels = {
        #     'text': 'Текст записи',
        #     'group': 'Группа'
        # }
        # help_texts = {
        #     'text': 'Напишите сюда текст вашей записи.',
        #     'group': 'Группа, к которой отнести запись(необязательно).'
        # }
