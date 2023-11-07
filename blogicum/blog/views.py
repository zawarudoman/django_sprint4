from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)

from blog.forms import CommentForm, CreatePostForm, UserForm
from blog.models import Category, Comment, Post, User


PAGINATOR_NUM = 10


def get_request():
    return Post.objects.select_related(
        "category",
        "location",
        "author"
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


class IndexView(ListView):
    """Homepage"""

    model = Post
    paginate_by = PAGINATOR_NUM
    template_name = 'blog/index.html'

    def get_queryset(self):
        """Post"""

        return Post.objects.select_related(
            'location',
            'author',
            'category'
        ).filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).annotate(
            comment_count=Count('comment')
        ).order_by('-pub_date')


def category_posts(request, category_slug):
    """Page output category_posts"""

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post = get_request().filter(category=category)
    paginator = Paginator(post, PAGINATOR_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj, }
    return render(request, "blog/category.html", context)


class PostDetailViews(LoginRequiredMixin, DetailView):
    """Post detail"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Checking for user access to editing a post
         as well as user access to hidden publications"""

        post_object = self.get_object()
        if post_object.author != self.request.user:
            if (
                    not post_object.is_published
                    or not post_object.category.is_published
                    or post_object.pub_date > timezone.now()
            ):
                raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Update context"""

        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (self.object.comment.select_related('author'))
        return context


class PostCreateViews(LoginRequiredMixin, CreateView):
    """Post create"""
    model = Post
    fields = ['title', 'text', 'image', 'pub_date', 'location', 'category']
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        """Update context"""

        context = super().get_context_data(**kwargs)
        context['comment'] = self.object.comment.select_related('author')\
            if self.object \
            else 'avc'
        return context

    def form_valid(self, form):
        """Form validity check"""

        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """User translation after successful post create"""

        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostUpdateViews(LoginRequiredMixin, UpdateView):
    """Post eding"""

    model = Post
    fields = ['title', 'text', 'image', 'pub_date', 'location', 'category']
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Checking for user access to editing a post"""

        if self.get_object().author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        get_object_or_404(
            Post,
            pk=kwargs['post_id'],
            is_published=True,
            author=self.request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """User translation after successful post editing"""

        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteViews(LoginRequiredMixin, DeleteView):
    """Delete post"""

    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Сhecking the user for the authorship of the post"""

        if not request.user.is_authenticated:
            return self.handle_no_permission()
        get_object_or_404(Post, pk=kwargs['post_id'], author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Update context"""

        context = super().get_context_data(**kwargs)
        context['form'] = CreatePostForm(instance=self.object)
        return context


class ProfileListViews(ListView):
    """Profile page"""

    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = PAGINATOR_NUM

    def get_queryset(self):
        """Obtaining user information"""

        user = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        if user == self.request.user:
            return Post.objects.select_related(
                'location',
                'category',
                'author'
            ).filter(
                author=user
            ).order_by(
                '-pub_date'
            ).annotate(comment_count=Count('comment'))
        return Post.objects.select_related(
            'location',
            'category',
            'author'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
            author=user
        ).order_by(
            '-pub_date'
        ).annotate(comment_count=Count('comment'))

    def get_context_data(self, **kwargs):
        """Update context"""

        context = super().get_context_data(**kwargs)
        user = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        context['profile'] = user
        return context


class ProfileUpdateViews(LoginRequiredMixin, UpdateView):
    """Profile update"""

    queryset = Post.objects.select_related()
    form_class = UserForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'username'

    def get_object(self, queryset=None):
        """Getting the username object"""

        slug = self.kwargs['username']
        return get_object_or_404(User, username=slug)

    def get_success_url(self):
        """User translation after successful  create"""

        return reverse_lazy('blog:profile', kwargs={'username': self.request.user})


class CommentCreateViews(LoginRequiredMixin, CreateView):
    """Comment create"""

    posts = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        """Сhecking post availability"""

        self.posts = get_object_or_404(
            Post,
            pk=kwargs['post_id'],
            category__is_published=True,
            is_published=True
        )
        return super().dispatch(request, args, kwargs)

    def form_valid(self, form):
        """Form validity check"""

        form.instance.author = self.request.user
        form.instance.post = self.posts
        return super().form_valid(form)

    def get_success_url(self):
        """User translation after successful comment create"""

        return reverse('blog:post_detail', kwargs={'post_id': self.posts.id})


class CommentUpdateViews(LoginRequiredMixin, UpdateView):
    """Coment update"""

    model = Comment
    fields = ('comment',)
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        """Сhecking the user for the authorship of the comment"""

        comment_obj = get_object_or_404(Comment, id=kwargs['comment_id'])
        if comment_obj.author != self.request.user:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """User translation after successful comment editing"""

        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteViews(LoginRequiredMixin, DeleteView):
    """Comment delete and redirect homepage"""

    model = Comment
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        """Сhecking the user for the authorship of the comment"""

        comment_obj = get_object_or_404(Comment, id=kwargs['comment_id'])
        if comment_obj.author != self.request.user:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)
