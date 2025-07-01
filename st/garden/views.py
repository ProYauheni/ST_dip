from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Profile, ForumPost, Advertisement, News, Voting, Vote, PageVisit, Appeal, Community, Document, \
    Comment
from .forms import AppealForm, AppealResponseForm, DocumentForm, CommentForm, AdvertisementForm
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden

from django.urls import reverse
from django.db.models import Count, Q


def main_page(request):
    # visits_count = request.session.get('visits_num', 0)
    counter, created = PageVisit.objects.get_or_create(page_name='main_page')
    # Увеличиваем счётчик посещений
    counter.visits += 1
    counter.save()
    # Передаём количество посещений в шаблон
    return render(request, 'main_page.html', {'total_visits': counter.visits})
    # request.session['visits_num'] = visits_count + 1
    # return render(request, 'main_page.html', {'visits_num':visits_count})


@login_required
def forum(request):
    posts = ForumPost.objects.all().order_by('-created_at')
    return render(request, 'forum.html', {'posts': posts})


@login_required
def forum_post_detail(request, pk):
    post = get_object_or_404(ForumPost, pk=pk)
    # Получаем только корневые комментарии (без родителя)
    comments = post.comments.filter(parent__isnull=True).prefetch_related('replies', 'user')

    # Получаем, на какой комментарий хотят ответить
    reply_to = request.GET.get('reply_to')
    try:
        reply_to = int(reply_to)
    except (TypeError, ValueError):
        reply_to = None

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = form.cleaned_data.get('parent_id')
            parent_comment = None
            if parent_id:
                # Проверяем, что родительский комментарий действительно принадлежит этому посту
                parent_comment = Comment.objects.filter(id=parent_id, post=post).first()
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.parent = parent_comment
            comment.save()
            # После отправки формы редиректим на тот же пост, чтобы избежать повторной отправки
            # и сбрасываем reply_to (можно прокрутить к новому комментарию по желанию)
            return redirect(f'{post.get_absolute_url()}#comment-{comment.id}')
    else:
        # Если пользователь нажал "Ответить", подставляем parent_id в форму
        initial = {}
        if reply_to:
            initial['parent_id'] = reply_to
        form = CommentForm(initial=initial)

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'reply_to': reply_to,
    }
    return render(request, 'forum_post_detail.html', context)


def ads(request):
    ads = Advertisement.objects.all().order_by('-created_at')
    return render(request, 'ads.html', {'ads': ads})


@login_required
def create_advertisement(request):
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.owner = request.user
            ad.save()
            return redirect('ads')  # замените на нужный URL после создания
    else:
        form = AdvertisementForm()
    return render(request, 'create_ads.html', {'form': form})


@login_required
def edit_advertisement(request, pk):
    ad = get_object_or_404(Advertisement, pk=pk)

    # Проверяем, что текущий пользователь — владелец объявления
    if ad.owner != request.user:
        return HttpResponseForbidden("Вы не можете редактировать это объявление.")

    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ads')  # или на страницу просмотра объявления
    else:
        form = AdvertisementForm(instance=ad)

    return render(request, 'edit_advertisement.html', {'form': form, 'ad': ad})


@login_required
def delete_advertisement(request, pk):
    ad = get_object_or_404(Advertisement, pk=pk)

    # Проверяем, что текущий пользователь — владелец объявления
    if ad.owner != request.user:
        return HttpResponseForbidden("Вы не можете удалить это объявление.")

    if request.method == 'POST':
        ad.delete()
        return redirect('ads')

    return render(request, 'delete_advertisement.html', {'ad': ad})


@login_required
def voting_list(request):
    community = getattr(request.user.profile, 'community', None)
    if not community:
        return render(request, 'no_profile.html')  # или сообщение об ошибке

    votings = Voting.objects.filter(community=community, active=True).order_by('-created_at')
    return render(request, 'voting_list.html', {'votings': votings})


@login_required
def my_community(request):
    profile = get_object_or_404(Profile, user=request.user)
    news = News.objects.filter(community=profile.community)
    votings = Voting.objects.filter(community=profile.community, active=True)
    return render(request, 'my_community.html', {
        'community': profile.community,
        'news': news,
        'votings': votings
    })


@login_required
def voting_detail(request, voting_id):
    voting = get_object_or_404(Voting, id=voting_id, community=request.user.profile.community)

    # Получаем существующий голос пользователя, если есть
    user_vote = Vote.objects.filter(voting=voting, user=request.user).first()

    if not voting.active:
        messages.info(request, 'Голосование завершено. Вы не можете изменить свой голос.')
        return render(request, 'voting_detail.html', {'voting': voting, 'user_vote': user_vote, 'voting_closed': True})

    if request.method == 'POST':
        choice = request.POST.get('choice')
        if choice not in ['True', 'False']:
            messages.error(request, 'Пожалуйста, выберите вариант для голосования.')
        else:
            choice_bool = (choice == 'True')
            if user_vote:
                # Обновляем существующий голос
                user_vote.choice = choice_bool
                user_vote.save()
                messages.success(request, 'Ваш голос обновлён.')
            else:
                # Создаём новый голос
                Vote.objects.create(voting=voting, user=request.user, choice=choice_bool)
                messages.success(request, 'Ваш голос учтён.')
            return redirect(reverse('voting_detail', args=[voting.id]))

    return render(request, 'voting_detail.html', {
        'voting': voting,
        'user_vote': user_vote,
        'voting_closed': False,
    })


@login_required
def forum_post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            ForumPost.objects.create(user=request.user, title=title, content=content)
            return redirect('forum')
        else:
            error = "Пожалуйста, заполните все поля."
            return render(request, 'forum_post_create.html', {'error': error})
    return render(request, 'forum_post_create.html')


@login_required
def appeal_create(request):
    if request.method == 'POST':
        form = AppealForm(request.POST)
        if form.is_valid():
            appeal = form.save(commit=False)
            appeal.user = request.user
            appeal.save()
            messages.success(request, 'Обращение успешно отправлено.')
            return redirect('appeal_list')
    else:
        form = AppealForm()
    return render(request, 'appeal_create.html', {'form': form})


@login_required
def appeal_list(request):
    appeals = Appeal.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'appeal_list.html', {'appeals': appeals})


def is_board_member(user):
    return user.groups.filter(name__in=['Председатель', 'Правление']).exists()


@login_required
@user_passes_test(is_board_member)
def appeal_detail_and_respond(request, appeal_id):
    appeal = get_object_or_404(Appeal, id=appeal_id)

    if request.method == 'POST':
        form = AppealResponseForm(request.POST, instance=appeal)
        if form.is_valid():
            appeal = form.save(commit=False)
            appeal.responded_at = timezone.now()
            appeal.responder = request.user
            appeal.save()
            messages.success(request, 'Ответ успешно сохранён.')
            return redirect('appeal_detail_and_respond', appeal_id=appeal.id)
    else:
        form = AppealResponseForm(instance=appeal)

    context = {
        'appeal': appeal,
        'form': form,
    }
    return render(request, 'appeal_detail_and_respond.html', context)


@login_required
@user_passes_test(is_board_member)
def all_appeals_list(request):
    appeals = Appeal.objects.all().order_by('-created_at')
    return render(request, 'all_appeals_list.html', {'appeals': appeals})


# @login_required
# @user_passes_test(is_board_member)
# def voting_report(request, voting_id):
#     voting = get_object_or_404(Voting, id=voting_id)
#
#     votes = voting.vote_set.aggregate(
#         total=Count('id'),
#         votes_for=Count('id', filter=Q(choice=True)),
#         votes_against=Count('id', filter=Q(choice=False))
#     )
#
#     context = {
#         'voting': voting,
#         'total_votes': votes['total'],
#         'votes_for': votes['votes_for'],
#         'votes_against': votes['votes_against'],
#     }
#     return render(request, 'voting_report.html', context)

@login_required
def voting_overview(request):
    # Если пользователь администратор — показываем всё
    if request.user.is_superuser or request.user.is_staff:
        votings = Voting.objects.annotate(
            total_votes=Count('vote'),
            votes_for=Count('vote', filter=Q(vote__choice=True)),
            votes_against=Count('vote', filter=Q(vote__choice=False))
        ).order_by('-created_at')
    else:
        # Обычная логика — показывать только свои товарищества, если не админ
        communities = Profile.objects.filter(
            user=request.user,
            role__in=['chairman', 'board_member']
        ).values_list('community', flat=True)
        votings = Voting.objects.filter(community__in=communities).annotate(
            total_votes=Count('vote'),
            votes_for=Count('vote', filter=Q(vote__choice=True)),
            votes_against=Count('vote', filter=Q(vote__choice=False))
        ).order_by('-created_at')

    context = {
        'votings': votings,
    }
    return render(request, 'voting_overview.html', context)


@login_required
def documents_list(request, community_id):
    community = get_object_or_404(Community, id=community_id)

    # Проверка прав доступа: пользователь должен принадлежать к этому сообществу или быть админом
    if not (request.user.is_superuser or request.user.is_staff or request.user.profile.community == community):
        return HttpResponseForbidden("Доступ запрещён")

    documents = community.documents.all().order_by('-uploaded_at')
    return render(request, 'documents_list.html', {'community': community, 'documents': documents})


@login_required
def upload_document(request, community_id):
    community = get_object_or_404(Community, id=community_id)

    # Проверка прав доступа (например, только председатель и члены правления)
    if not (request.user.is_superuser or request.user.is_staff or
            (request.user.profile.community == community and request.user.profile.role in ['chairman',
                                                                                           'board_member'])):
        return HttpResponseForbidden("Доступ запрещён")

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.community = community
            document.save()
            return redirect('documents_list', community_id=community.id)
    else:
        form = DocumentForm()

    return render(request, 'upload_document.html', {'form': form, 'community': community})


@login_required
def contacts_view(request):
    community = request.user.profile.community  # или другой способ получить сообщество пользователя

    contacts = {
        'chairman': community.board_members.filter(role='chairman').first(),
        'treasurer': community.board_members.filter(role='treasurer').first(),
        'board_members': community.board_members.filter(role='board_member'),
        'electricity_manager': community.board_members.filter(role='electricity_manager').first(),
        'water_manager': community.board_members.filter(role='water_manager').first(),
    }

    return render(request, 'contacts.html', {
        'community': community,
        'contacts': contacts,
    })


@login_required
def payment_view(request):
    community = request.user.profile.community
    payment_info = getattr(community, 'payment_info', None)
    return render(request, 'payment.html', {
        'community': community,
        'payment_info': payment_info,
    })


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
def profile_view(request):
    user = request.user
    appeals = user.appeals.order_by('-created_at')

    # Проверяем, состоит ли пользователь в нужных группах
    allowed_groups = ['Председатель', 'Правление']  # или ['Председатель', 'Правление']
    is_chairman_or_board = user.groups.filter(name__in=allowed_groups).exists()

    return render(request, 'profile.html', {
        'appeals': appeals,
        'is_chairman_or_board': is_chairman_or_board,
    })
