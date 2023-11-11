from django.shortcuts import redirect

from blog.models import Comment


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
