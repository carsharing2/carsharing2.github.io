from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.utils import timezone
from .models import Post, Users_base
from chan import utils
from math import ceil
import datetime

def index(request, page=0):

    threads_on_page = 3
    bump_limit = 5
    page = int(page)
    op_posts = Post.objects.filter(parent_thread=None)
    if op_posts.count() <= threads_on_page * page:
        raise Http404('Page does not exist')

    pages_total_count = ceil(op_posts.count() / threads_on_page)
    pages_total = list(range(pages_total_count))
    
    for p in op_posts:
        try:
            s = Post.objects.filter(parent_thread=p.post_id, sage=False)[:bump_limit]
            if s.count() - 1 <= 0:
                p.last_post_id = p.post_id
            else:                  
                s = s[s.count()-1]
                p.last_post_id = s.post_id
        except AttributeError: #No posts in thread, so last post date is date of OP post
            p.last_post_id = p.post_id

    op_posts = sorted(list(op_posts), key=lambda p: p.last_post_id, reverse=True) #Sort threads py last post id

    data = []
    for p in op_posts[page*threads_on_page:page*threads_on_page + threads_on_page]:
        data.append({
            'op': p,
            'related_posts': Post.objects.filter(parent_thread=p.post_id).order_by('-post_id')[:3:-1],
            })

    return render(request, 'chan/index.html', {'posts': data, 'pages': pages_total})
    
def create(request, thread_id=None):
    ip = utils.get_ip(request)
    try: 
        user = Users_base.objects.get(ip=ip)
        new_user = False
    except Users_base.DoesNotExist:
        user = Users_base.objects.create(
            ip = ip,
            last_post_date = timezone.now(),
            ban_reason = None,
            )
        new_user = True

    if user.is_banned():
        allow_post = False
        result_message = 'Ban: {}; expires: {}'.format(user.ban_reason, user.ban_expire.ctime())
    elif (timezone.now() - user.last_post_date < datetime.timedelta(seconds = 5)) and not new_user:
        allow_post = False
        result_message = 'You post too fast'
    else:
        allow_post = True
    
    post_message = request.POST['message']
    sage = True if 'sage' in request.POST else False
    media = request.FILES['file'] if 'file' in request.FILES else None
    if media and 'image' not in media.content_type:
        allow_post = False
        result_message = 'Inappropriate content type (images only)'
    if media and media.size > 2000000:
        allow_post = False
        result_message = 'File is too big (only 2mb allowed)'
    if post_message == '' and not media: #Empty messages are not allowed
        allow_post = False
        result_message = "You can't send an empty message"

    if allow_post:
        new_post = Post(
            message = utils.post_handler(post_message),
            mail = request.POST['mail'],
            date = timezone.now(),
            sage = sage, 
            ip = ip,
            parent_thread = thread_id,
            media = media,
        )
        new_post.save()

        user.last_post_date = timezone.now()
        user.save()

        for num in utils.get_replies_list(post_message):
           p = Post.objects.get(post_id=num)
           p.replies += str(new_post.post_id) + ';'
           p.save()

        result_message = 'Post send'
    
    if thread_id is None and allow_post: #If user created new thread.
        threads = Post.objects.filter(parent_thread=None)
        if threads.count() > 10: #Maximum number of threads on the board.
            last_thread_id = threads.order_by('post_id').first().post_id
            threads.order_by('post_id').first().delete() #delete last thread
            Post.objects.filter(parent_thread=last_thread_id).delete() #delete posts in last thread
        result_message = 'Thread is created'
            
    return JsonResponse({'message': result_message, 'allow_post': allow_post})
    

def thread(request, thread_id, render_posts_only=False):
    op_post = get_object_or_404(Post, post_id=thread_id, parent_thread=None)
    op_post.replies = op_post.replies.split(';')[:-1]

    posts = Post.objects.filter(parent_thread=(thread_id))
    for p in posts:
        p.replies = p.replies.split(';')[:-1]

    if render_posts_only:
        template_name = 'posts'
    else:
        template_name = 'thread'
    return render(request, 'chan/{}.html'.format(template_name), {'op_post': op_post, 'posts': posts})