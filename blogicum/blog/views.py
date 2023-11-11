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
from blog.utils import get_request


PAGINATOR_NUM = 10


class CommentFormMixin:
    """Comment Mixin for delete and update view"""

    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        """Сhecking the user for the authorship of the comment"""
        if self.get_object().author != self.request.user:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)


class IndexView(ListView):
    """Homepage"""

    model = Post
    paginate_by = PAGINATOR_NUM
    template_name = 'blog/index.html'

    def get_queryset(self):
        """Post"""
        return get_request().annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')


def category_posts(request, category_slug):
    """Page output category_posts"""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post = get_request().filter(category=category).annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(post, PAGINATOR_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj, }
    return render(request, "blog/category.html", context)


class PostDetailViews(DetailView):
    """Post detail"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        """Checking for user access to editing a post"""
        post_object = super(PostDetailViews, self).get_object(
            queryset=queryset
        )
        if post_object.author != self.request.user:
            if (
                not post_object.is_published
                or not post_object.category.is_published
                or post_object.pub_date > timezone.now()
            ):
                raise Http404
        return post_object

    def get_context_data(self, **kwargs):
        """Update context"""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostCreateViews(LoginRequiredMixin, CreateView):
    """Post create"""

    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Form validity check"""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """User translation after successful post create"""
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostUpdateViews(LoginRequiredMixin, UpdateView):
    """Post eding"""

    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Checking for user access to editing a post"""
        if self.get_object().author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
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
        if not request.user.is_anonymous:
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
            ).annotate(comment_count=Count('comments'))
        return get_request().filter(
            author=user
        ).order_by(
            '-pub_date'
        ).annotate(comment_count=Count('comments'))

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

    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        """Getting the username object"""
        return self.request.user

    def get_success_url(self):
        """User translation after successful  create"""
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class CommentCreateViews(LoginRequiredMixin, CreateView):
    """Comment create"""

    posts = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        """Form validity check"""
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id'],
            category__is_published=True,
            is_published=True
        )
        return super().form_valid(form)

    def get_success_url(self):
        """User translation after successful comment create"""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateViews(LoginRequiredMixin, CommentFormMixin, UpdateView):
    """Coment update"""

    form_class = CommentForm

    def get_success_url(self):
        """User translation after successful comment editing"""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteViews(LoginRequiredMixin, CommentFormMixin, DeleteView):
    """Comment delete and redirect homepage"""

    success_url = reverse_lazy('blog:index')
