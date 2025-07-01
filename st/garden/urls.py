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
    path('ads/create/', views.create_advertisement, name='create_advertisement'),
    path('ads/<int:pk>/edit/', views.edit_advertisement, name='edit_advertisement'),
    path('ads/<int:pk>/delete/', views.delete_advertisement, name='delete_advertisement'),
    path('my_community/', views.my_community, name='my_community'),
    # path('community/<slug:slug>/', views.my_community, name='my_community'),
    path('voting/', views.voting_list, name='voting_list'),
    path('voting/<int:voting_id>/', views.voting_detail, name='voting_detail'),
    # path('voting/<int:voting_id>/report/', views.voting_report, name='voting_report'),
    path('voting/overview/', views.voting_overview, name='voting_overview'),
    path('forum/new/', views.forum_post_create, name='forum_post_create'),
    path('appeals/', views.appeal_list, name='appeal_list'),
    path('appeals/new/', views.appeal_create, name='appeal_create'),
    path('appeals/<int:appeal_id>/respond/', views.appeal_detail_and_respond, name='appeal_detail_and_respond'),
    path('appeals/board/', views.all_appeals_list, name='all_appeals_list'),
    path('community/<int:community_id>/documents/', views.documents_list, name='documents_list'),
    path('community/<int:community_id>/documents/upload/', views.upload_document, name='upload_document'),
    path('my-community/contacts/', views.contacts_view, name='community_contacts'),
    path('my_community/payment/', views.payment_view, name='community_payment'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', auth_views.PasswordChangeView.as_view(
        template_name='registration/change_password.html',success_url='/profile/'), name='password_change'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
