from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Profile, ForumPost, Advertisement, News, Voting, Vote, Voting, PageVisit, Appeal, Community, Document, \
    Comment, DocumentFolder, PaymentInfo
from .forms import AppealForm, AppealResponseForm, DocumentForm, CommentForm, AdvertisementForm, NewsForm, VotingForm, \
    PaymentInfoForm, CommunityPaymentInfoForm, VotingEditForm
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden

from django.urls import reverse
from django.db.models import Count, Q, Prefetch

from django.views.decorators.http import require_POST


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
    posts = ForumPost.objects.filter(active=True).order_by('-created_at')
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
            return redirect('ads')
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


# @login_required
# def voting_create(request, community_id):
#     if not user_can_manage_votes(request.user):
#         messages.error(request, "У вас нет прав создавать голосования.")
#         return redirect('voting_overview')
#
#     # Проверяем, что пользователь связан с этим сообществом
#     community = get_object_or_404(Community, pk=community_id)
#     profile = getattr(request.user, 'profile', None)
#     if not profile or profile.community_id != community.id:
#         messages.error(request, "Вы не принадлежите этому сообществу.")
#         return redirect('voting_overview')
#
#     if request.method == 'POST':
#         form = VotingForm(request.POST)
#         if form.is_valid():
#             voting = form.save(commit=False)
#             voting.community = community  # фиксируем сообщество
#             voting.save()
#             messages.success(request, "Голосование успешно создано.")
#             return redirect('voting_overview')
#     else:
#         form = VotingForm(initial={'community': community})
#
#     return render(request, 'voting_create.html', {'form': form, 'community': community})
@login_required
def voting_create(request, community_id):
    if not user_can_manage_votes(request.user):
        messages.error(request, "У вас нет прав создавать голосования.")
        return redirect('voting_overview')

    # Проверяем, что пользователь связан с этим сообществом
    community = get_object_or_404(Community, pk=community_id)
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.community_id != community.id:
        messages.error(request, "Вы не принадлежите этому сообществу.")
        return redirect('voting_overview')

    if request.method == 'POST':
        form = VotingForm(request.POST)
        if form.is_valid():
            voting = form.save(commit=False)
            voting.community = community  # фиксируем сообщество
            voting.save()
            messages.success(request, "Голосование успешно создано.")
            return redirect('voting_overview')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        # При инициализации поля community передаём id, так как в форме HiddenInput
        form = VotingForm(initial={'community': community.id})

    return render(request, 'voting_create.html', {'form': form, 'community': community})


@login_required
def voting_edit(request, voting_id):
    voting = get_object_or_404(Voting, id=voting_id)

    if not user_can_manage_votes(request.user):
        messages.error(request, "У вас нет прав на редактирование этого голосования.")
        return redirect('voting_overview')

    if not voting.active:
        messages.warning(request, "Редактирование завершённого голосования невозможно.")
        return redirect('voting_overview')

    if request.method == 'POST':
        form = VotingEditForm(request.POST, instance=voting)
        if form.is_valid():
            form.save()
            messages.success(request, "Голосование успешно обновлено.")
            return redirect('voting_overview')
    else:
        form = VotingEditForm(instance=voting)

    return render(request, 'voting_edit.html', {'form': form, 'voting': voting})



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





def user_can_manage_votes(user):
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role in ['chairman', 'board_member']


@login_required
def voting_detail(request, voting_id):
    voting = get_object_or_404(Voting, id=voting_id)
    user_vote = Vote.objects.filter(voting=voting, user=request.user).first()
    voting_closed = not voting.active

    if not voting_closed and request.method == 'POST':
        choice = request.POST.get('choice')
        if choice not in ['for', 'against', 'abstained']:
            error = "Пожалуйста, выберите ваш вариант."
        else:
            if user_vote:
                user_vote.choice = choice
                user_vote.save()
            else:
                Vote.objects.create(voting=voting, user=request.user, choice=choice)
            return redirect('voting_detail', voting_id=voting_id)
    else:
        error = None

    return render(request, 'voting_detail.html', {
        'voting': voting,
        'user_vote': user_vote,
        'voting_closed': voting_closed,
        'error': error,
    })



@login_required
def voting_overview(request):
    can_manage = user_can_manage_votes(request.user)

    if request.user.is_superuser or request.user.is_staff:
        votings = Voting.objects.annotate(
            total_votes=Count('votes'),
            votes_for=Count('votes', filter=Q(votes__choice='for')),
            votes_against=Count('votes', filter=Q(votes__choice='against')),
            votes_abstained=Count('votes', filter=Q(votes__choice='abstained')),
        ).order_by('-created_at')
        community = None
    else:
        communities = Profile.objects.filter(
            user=request.user,
            role__in=['chairman', 'board_member']
        ).values_list('community', flat=True)

        votings = Voting.objects.filter(community__in=communities).annotate(
            total_votes=Count('votes'),
            votes_for=Count('votes', filter=Q(votes__choice='for')),
            votes_against=Count('votes', filter=Q(votes__choice='against')),
            votes_abstained=Count('votes', filter=Q(votes__choice='abstained')),
        ).order_by('-created_at')

        community = None
        if communities:
            community = Community.objects.filter(id__in=communities).first()

    context = {
        'votings': votings,
        'can_manage': can_manage,
        'community': community,
    }
    return render(request, 'voting_overview.html', context)


@login_required
@require_POST
def finish_voting(request, voting_id):
    voting = get_object_or_404(Voting, id=voting_id)

    if not user_can_manage_votes(request.user):
        messages.error(request, "У вас нет прав завершать голосования.")
        return redirect('voting_overview')

    if not voting.active:
        messages.info(request, "Голосование уже завершено.")
        return redirect('voting_overview')

    voting.active = False
    voting.save()
    messages.success(request, f"Голосование «{voting.question}» успешно завершено.")
    return redirect('voting_overview')





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

def user_is_board_member(user):
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role in ['chairman', 'board_member']


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


@login_required
@user_passes_test(user_is_board_member)
def appeal_detail_and_respond(request, appeal_id):
    appeal = get_object_or_404(Appeal, id=appeal_id)
    profile = get_object_or_404(Profile, user=request.user)

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
        'community': profile.community,
    }
    return render(request, 'appeal_detail_and_respond.html', context)


@login_required
@user_passes_test(user_is_board_member)
def all_appeals_list(request):
    profile = get_object_or_404(Profile, user=request.user)
    community = profile.community

    # Фильтруем обращения только по сообществу пользователя
    appeals = Appeal.objects.filter(user__profile__community=community).order_by('-created_at')

    return render(request, 'all_appeals_list.html', {
        'appeals': appeals,
        'community': community,
    })


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


def user_can_manage_documents(user):
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role in ['chairman', 'board_member']

@login_required
def documents_list(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    folders = community.folders.prefetch_related(
        models.Prefetch(
            'documents',
            queryset=Document.objects.filter(is_deleted=False)
        )
    )
    is_chairman_or_board = user_can_manage_documents(request.user)
    context = {
        'community': community,
        'folders': folders,
        'is_chairman_or_board': is_chairman_or_board,
    }
    return render(request, 'documents_list.html', context)

@login_required
def add_document(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    if not user_can_manage_documents(request.user):
        messages.error(request, "У вас нет прав для добавления документов.")
        return redirect('documents_list', community_id=community.id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, community=community)
        if form.is_valid():
            document = form.save(commit=False)
            document.community = community
            document.save()
            messages.success(request, "Документ успешно добавлен.")
            return redirect('documents_list', community_id=community.id)
    else:
        form = DocumentForm(community=community)

    return render(request, 'add_document.html', {'form': form, 'community': community})

@login_required
def delete_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not user_can_manage_documents(request.user):
        messages.error(request, "У вас нет прав для удаления документов.")
        return redirect('documents_list', community_id=document.community.id)

    if request.method == 'POST':
        # Мягкое удаление
        document.delete()
        messages.success(request, "Документ успешно удалён.")
        return redirect('documents_list', community_id=document.community.id)

    return render(request, 'confirm_delete_document.html', {'document': document})



def user_can_manage_contacts(user):
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role in ['chairman', 'board_member']

@login_required
def contacts_view(request):
    community = request.user.profile.community

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
def community_contact_edit(request):
    community = request.user.profile.community

    if not user_can_manage_contacts(request.user):
        messages.error(request, "У вас нет прав редактировать контактную информацию.")
        return redirect('community_contacts')

    if request.method == 'POST':
        form = CommunityPaymentInfoForm(request.POST, instance=community)
        if form.is_valid():
            form.save()
            messages.success(request, "Информация успешно обновлена.")
            return redirect('community_contacts')
    else:
        form = CommunityPaymentInfoForm(instance=community)

    return render(request, 'community_contact_edit.html', {'form': form, 'community': community})


@login_required
def payment_view(request):
    community = request.user.profile.community
    payment_info = getattr(community, 'payment_info', None)
    return render(request, 'payment.html', {
        'community': community,
        'payment_info': payment_info,
    })

def user_can_manage_payments(user):
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role in ['chairman', 'board_member']

@login_required
def payment_edit(request):
    community = request.user.profile.community
    if not user_can_manage_payments(request.user):
        messages.error(request, "У вас нет прав редактировать информацию по оплате.")
        return redirect('payment_view')

    payment_info, created = PaymentInfo.objects.get_or_create(community=community)

    if request.method == 'POST':
        form = PaymentInfoForm(request.POST, instance=payment_info)
        if form.is_valid():
            form.save()
            messages.success(request, "Информация по оплате успешно сохранена.")
            return redirect('payment_view')
    else:
        form = PaymentInfoForm(instance=payment_info)

    return render(request, 'payment_edit.html', {'form': form, 'community': community})

@login_required
def payment_delete(request):
    community = request.user.profile.community
    if not user_can_manage_payments(request.user):
        messages.error(request, "У вас нет прав удалять информацию по оплате.")
        return redirect('payment_view')

    payment_info = getattr(community, 'payment_info', None)
    if not payment_info:
        messages.error(request, "Информация по оплате не найдена.")
        return redirect('payment_view')

    if request.method == 'POST':
        payment_info.delete()
        messages.success(request, "Информация по оплате удалена.")
        return redirect('payment_view')

    return render(request, 'payment_confirm_delete.html', {'payment_info': payment_info})





def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
def profile_view(request):
    user = request.user
    appeals = user.appeals.order_by('-created_at')

    profile = getattr(user, 'profile', None)
    user_role = getattr(profile, 'role', 'member') if profile else 'member'

    context = {
        'appeals': appeals,
        'user_role': user_role,
    }
    return render(request, 'profile.html', context)





def user_can_manage_news(user):
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role in ['chairman', 'board_member']

@login_required
def my_community_view(request):
    # Получаем сообщество пользователя (замените на вашу логику)
    community = getattr(request.user.profile, 'community', None)
    if not community:
        messages.error(request, "Сообщество для пользователя не найдено.")
        return redirect('profile')  # или другая страница

    news = community.news.filter(is_deleted=False).order_by('-created_at')
    is_chairman_or_board = user_can_manage_news(request.user)

    context = {
        'community': community,
        'news': news,
        'is_chairman_or_board': is_chairman_or_board,
    }
    return render(request, 'my_community.html', context)

@login_required
def add_news(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    if not user_can_manage_news(request.user):
        messages.error(request, "У вас нет прав для добавления новостей.")
        return redirect('my_community')

    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.community = community
            news.save()
            messages.success(request, "Новость успешно добавлена.")
            return redirect('my_community')
    else:
        form = NewsForm()

    return render(request, 'add_news.html', {'form': form, 'community': community})

@login_required
def delete_news(request, pk):
    news = get_object_or_404(News, pk=pk)
    if not user_can_manage_news(request.user):
        messages.error(request, "У вас нет прав для удаления новостей.")
        return redirect('my_community')

    if request.method == 'POST':
        news.is_deleted = True
        news.save()
        messages.success(request, "Новость успешно удалена.")
        return redirect('my_community')

    return render(request, 'confirm_delete_news.html', {'news': news})


@login_required
def edit_news(request, pk):
    news = get_object_or_404(News, pk=pk)
    if not user_can_manage_news(request.user):
        messages.error(request, "У вас нет прав для редактирования новостей.")
        return redirect('my_community')

    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, "Новость успешно обновлена.")
            return redirect('my_community')
    else:
        form = NewsForm(instance=news)

    return render(request, 'edit_news.html', {'form': form, 'news': news})
