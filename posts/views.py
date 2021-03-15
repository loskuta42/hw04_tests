from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User
from .forms import PostForm
from django.core.paginator import Paginator


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_list = group.posts.all()
    paginator = Paginator(group_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    if request.method != "POST":
        form = PostForm(request.POST)
        return render(
            request,
            "new.html",
            {
                "form": form,
                "title": "Новая запись",
                "button": "Создать новую запись"
            })
    form = PostForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "new.html",
            {
                "form": form,
                "title": "Новая запись",
                "button": "Создать новую запись"
            })
    post = form.save(commit=False)
    username = request.user.username
    post.author = User.objects.get(username=username)
    post.save()
    return redirect("index")


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    count = author_posts.count()
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {"page": page, "count": count, "author":author})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    author_posts = author.posts.all()
    count = author_posts.count()
    return render(request, "post.html", {"author": author, "post": post, "count": count})


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    if request.method != "POST":
        if post.author != request.user:
            return redirect("post", post_id=post.id, username=author.username)
        form = PostForm(instance=post)
        return render(
            request,
            "new.html",
            {
                "form": form,
                "title": "Редактировать запись",
                "button": "Сохранить запись",
                "post": post,
                "author": author
            })
    form = PostForm(request.POST, instance=post)
    if not form.is_valid():
        return render(
            request,
            "new.html",
            {
                "form": form,
                "title": "Редактировать запись",
                "button": "Сохранить запись",
                "post": post
            })
    form.save()
    return redirect("profile")
    # тут тело функции. Не забудьте проверить,
    # что текущий пользователь — это автор записи.
    # В качестве шаблона страницы редактирования укажите шаблон создания новой записи
    # который вы создали раньше (вы могли назвать шаблон иначе)
