from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=100)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        "Текст поста",
        help_text="Напишите текст вашей записи."
    )
    pub_date = models.DateTimeField(
        "date published",
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    group = models.ForeignKey(
        Group,
        verbose_name="Группа",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="posts",
        help_text="Группа, к которой относится запись."
    )

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[:15]
