from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube import settings

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_list = group.posts.all()
    paginator = Paginator(group_list, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm(request.POST)
        return render(
            request,
            'posts/new.html',
            {
                'form': form,
                'title': 'Новая запись',
                'button': "Создать новую запись"
            })
    form = PostForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            'posts/new.html',
            {
                'form': form,
                'title': 'Новая запись',
                'button': 'Создать новую запись'
            })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    count = author_posts.count()
    paginator = Paginator(author_posts, settings.PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {'page': page, 'count': count, 'author': author}
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author_posts = post.author.posts.all()
    count = author_posts.count()
    return render(
        request,
        'post.html',
        {'author': post.author, 'post': post, 'count': count}
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author != request.user:
        return redirect(
            'post',
            post_id=post.id,
            username=post.author.username
        )
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(
            'post',
            post_id=post.id,
            username=post.author.username
        )
    return render(
        request,
        'posts/new.html',
        {
            'form': form,
            'title': 'Редактировать запись',
            'button': 'Сохранить запись',
            'post': post
        }
    )
