from django.contrib import admin
from .models import Community, Profile, News, ForumPost, Advertisement, Voting, Document, BoardMember, PaymentInfo

# Регистрируем каждую модель в админке
admin.site.register(Community)
admin.site.register(Profile)
admin.site.register(News)
admin.site.register(ForumPost)
admin.site.register(Advertisement)
admin.site.register(Voting)
admin.site.register(Document)

class BoardMemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'community', 'plot_number', 'phone')
    list_filter = ('community', 'role')
    search_fields = ('full_name', 'plot_number', 'phone')

admin.site.register(BoardMember, BoardMemberAdmin)

@admin.register(PaymentInfo)
class PaymentInfoAdmin(admin.ModelAdmin):
    list_display = ('community', 'membership_fee_amount', 'membership_fee_due_date',
                    'additional_fee_amount', 'additional_fee_due_date')
    search_fields = ('community__name',)
