from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from djangoblogv2.settings import EMAIL
from taggit.models import Tag
from django.db.models import Count, Q
# Create your views here.

def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    search=False
    tag=None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    search_form = SearchForm()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            searched_posts = Post.published.filter(Q(title__icontains=data['search_field']) and Q(body__icontains=data['search_field']))
            if searched_posts.count() > 0:
                search = True
        return render(request, 'blog/post/list.html', {'page': page,
                                                       'tag': tag,
                                                       'search_form': search_form,
                                                       'search': search,
                                                       'searched_posts': searched_posts})
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'page': page,
                                                   'posts': posts,
                                                   'tag': tag,
                                                   'search_form': search_form,
                                                   'search': search,})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similiar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similiar_posts = similiar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post':post,
                                                     'comments': comments,
                                                     'comment_form': comment_form,
                                                     'similiar_posts': similiar_posts})

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{}({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post_url)
            message = 'Read "{}" at {} by {} \n comments: {}'.format(post.title, post_url, post.author, cd['comments'])
            send_mail(subject, message, EMAIL, [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post':post, 'form': form, 'sent': sent})