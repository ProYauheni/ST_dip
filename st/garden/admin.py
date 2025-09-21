from django.contrib import admin
from django.contrib.auth.models import User
from .models import (Community, Profile, News, ForumPost, Advertisement, Vote, Voting, Document, BoardMember, PaymentInfo,
                     DocumentFolder, Appeal, Comment, Ballot)
from adminsortable2.admin import SortableAdminMixin
from django.contrib.admin import SimpleListFilter
from django_summernote.admin import SummernoteModelAdmin





# Регистрируем каждую модель в админке
admin.site.register(Community)
# admin.site.register(Profile)
# admin.site.register(News)
admin.site.register(ForumPost)
# admin.site.register(Advertisement)
# admin.site.register(Voting)
# admin.site.register(Document)
# admin.site.register(DocumentFolder)
# admin.site.register(Ballot)
admin.site.register(Comment)


class BoardMemberAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'full_name', 'role', 'community', 'plot_number', 'phone')
    list_filter = ('community', 'role')
    search_fields = ('full_name', 'plot_number', 'phone', 'user__username')

    def get_username(self, obj):
        return obj.user.username if obj.user else '(не указан)'
    get_username.short_description = 'Пользователь'
    get_username.admin_order_field = 'user__username'

admin.site.register(BoardMember, BoardMemberAdmin)



@admin.register(PaymentInfo)
class PaymentInfoAdmin(admin.ModelAdmin):
    list_display = ('community', 'membership_fee_amount', 'membership_fee_due_date',
                    'additional_fee_amount', 'additional_fee_due_date')
    search_fields = ('community__name',)


"""========================================Объявления====================================================="""
class CommunityFilter(admin.SimpleListFilter): # фильтр по товариществу.
    title = 'Товарищество'
    parameter_name = 'community'

    def lookups(self, request, model_admin):
        communities = Advertisement.objects.values_list('community__id', 'community__name').distinct()
        return [(c[0], c[1]) for c in communities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(community_id=self.value())
        return queryset


class OwnerByCommunityFilter(admin.SimpleListFilter): # фильтр по пользователю
    title = 'Пользователь'
    parameter_name = 'owner'

    def lookups(self, request, model_admin):
        community_id = request.GET.get('community')
        if community_id:
            users = User.objects.filter(profile__community_id=community_id).distinct()
        else:
            users = User.objects.all()
        return [(u.id, u.get_username()) for u in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(owner_id=self.value())
        return queryset


@admin.register(Advertisement) # сортировка объявлений по товариществу и пользователю
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'community', 'owner', 'topic', 'created_at')
    list_filter = (CommunityFilter, OwnerByCommunityFilter)
"""============================================================================================="""


"""========================================Обращения====================================================="""
class CommunityFilterForAppeal(SimpleListFilter):
    title = 'Товарищество'
    parameter_name = 'community'

    def lookups(self, request, model_admin):
        communities = Profile.objects.values_list('community__id', 'community__name').distinct()
        return [(c[0], c[1]) for c in communities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__profile__community_id=self.value())
        return queryset

class UserFilterForAppeal(SimpleListFilter):
    title = 'Пользователь'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        community_id = request.GET.get('community')
        if community_id:
            users = User.objects.filter(profile__community_id=community_id).distinct()
        else:
            users = User.objects.all()
        return [(u.id, u.get_username()) for u in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_id=self.value())
        return queryset

@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ('appeal_type', 'user', 'created_at', 'responder', 'responded_at')
    list_filter = (CommunityFilterForAppeal, UserFilterForAppeal)
    search_fields = ('user__username', 'text', 'response')
"""============================================================================================="""


"""==============================Папки для документов==========================================="""
@admin.register(DocumentFolder) # Используется фильтр CommunityFilter
class DocumentFolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'order')
    list_filter = (CommunityFilter,)
    ordering = ['community__name', 'order']
"""============================================================================================="""



"""==============================Документы======================================================"""
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'community', 'doc_type', 'uploaded_at', 'folder')
    list_filter = (CommunityFilter, 'doc_type')
    ordering = ['community__name', 'title']
"""============================================================================================="""


"""==============================Новости========================================================"""
@admin.register(News)
class NewsAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)  # поле 'content' с редактором
    list_display = ('title', 'community', 'created_at', 'pinned')
    list_filter = ('community', 'pinned')
    ordering = ['community__name', '-pinned', '-created_at']
"""============================================================================================="""


"""==============================Профили========================================================"""
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'community', 'role', 'can_vote', 'last_seen')
    list_filter = (CommunityFilter, 'role', 'can_vote')
    ordering = ['community__name', 'user__username']
"""============================================================================================="""


"""==============================Опрос========================================================"""
class VoteInline(admin.TabularInline):
    model = Vote
    extra = 0
    readonly_fields = ('user', 'choice')
    can_delete = False
    show_change_link = True

    class Media:
        css = {
            'all': ('css/admin_overrides.css',),
        }

@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    list_display = ('question', 'community', 'created_at')
    inlines = [VoteInline]
    list_filter = ('community',)
    ordering = ['community__name', 'created_at']
"""============================================================================================="""
@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
    list_display = ('id', 'community', 'start_date', 'end_date', 'active')
    list_filter = ('community', )  # Фильтр по товариществу
    ordering = ('community', 'start_date')  # Сортировка по товариществу и дате начала
    search_fields = ('community__name', )  # Поиск по имени товарищества (если есть поле name)


"""==================================Голосование================================================"""