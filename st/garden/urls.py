from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('forum/', views.forum, name='forum'),
    path('forum/<int:pk>/', views.forum_post_detail, name='forum_post_detail'),
    path('ads/', views.ads, name='ads'),
    path('my-ads/', views.my_ads, name='my_ads'),
    path('ads/create/', views.create_advertisement, name='create_advertisement'),
    path('ads/<int:pk>/edit/', views.edit_advertisement, name='edit_advertisement'),
    path('ads/<int:pk>/delete/', views.delete_advertisement, name='delete_advertisement'),
    path('my_community/', views.my_community, name='my_community'),
    # path('community/<slug:slug>/', views.my_community, name='my_community'),
    path('voting/', views.voting_list, name='voting_list'),
    path('voting/<int:voting_id>/', views.voting_detail, name='voting_detail'),


    path('votings/', views.voting_overview, name='voting_overview'),
    path('votings/<int:voting_id>/finish/', views.finish_voting, name='finish_voting'),
    path('votings/create/<int:community_id>/', views.voting_create, name='voting_create'),
    path('voting/<int:voting_id>/edit/', views.voting_edit, name='voting_edit'),
    # path('voting/<int:voting_id>/report/', views.voting_report, name='voting_report'),
    path('voting/overview/', views.voting_overview, name='voting_overview'),
    path('forum/new/', views.forum_post_create, name='forum_post_create'),
    path('appeals/', views.appeal_list, name='appeal_list'),
    path('appeals/new/', views.appeal_create, name='appeal_create'),
    path('appeals/<int:appeal_id>/respond/', views.appeal_detail_and_respond, name='appeal_detail_and_respond'),
    path('appeals/board/', views.all_appeals_list, name='all_appeals_list'),
    path('community/<int:community_id>/documents/', views.documents_list, name='documents_list'),
    path('community/<int:community_id>/documents/add/', views.add_document, name='add_document'),
    path('documents/<int:pk>/delete/', views.delete_document, name='delete_document'),

    path('my-community/contacts/', views.contacts_view, name='community_contacts'),
    path('my-community/contacts/edit/', views.community_contact_edit, name='community_contact_edit'),

    path('my_community/payment/', views.payment_view, name='community_payment'),

    path('payment/', views.payment_view, name='payment_view'),
    path('payment/edit/', views.payment_edit, name='payment_edit'),
    path('payment/delete/', views.payment_delete, name='payment_delete'),

    path('user_ping/', views.user_ping, name='user_ping'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', auth_views.PasswordChangeView.as_view(
        template_name='registration/change_password.html',success_url='/profile/'), name='password_change'),
    path('my-community/', views.my_community_view, name='my_community'),
    path('community/<int:community_id>/news/add/', views.add_news, name='add_news'),
    path('news/<int:pk>/delete/', views.delete_news, name='delete_news'),
    path('news/<int:pk>/edit/', views.edit_news, name='edit_news'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
