from django.contrib import admin
from .models import Community, Profile, News, ForumPost, Advertisement, Voting, Document, BoardMember, PaymentInfo, DocumentFolder
from adminsortable2.admin import SortableAdminMixin

# Регистрируем каждую модель в админке
admin.site.register(Community)
admin.site.register(Profile)
admin.site.register(News)
admin.site.register(ForumPost)
admin.site.register(Advertisement)
admin.site.register(Voting)
admin.site.register(Document)
admin.site.register(DocumentFolder)


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





