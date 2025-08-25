from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone
from .models import PageVisit, Profile
from datetime import timedelta
# from .utils import get_nbrb_rates

def total_visits_processor(request):
    counter, created = PageVisit.objects.get_or_create(page_name='main_page')
    return {
        'total_visits': counter.visits
    }

# def online_users_processor(request):
#     sessions = Session.objects.filter(expire_date__gte=timezone.now())
#     user_ids = []
#     for session in sessions:
#         data = session.get_decoded()
#         uid = data.get('_auth_user_id')
#         if uid:
#             user_ids.append(uid)
#     online_count = User.objects.filter(id__in=user_ids).count()
#     return {
#         'online_users': online_count
#     }





def online_users_processor(request):
    now = timezone.now()
    active_threshold = now - timedelta(seconds=40)  # считаем активными за последние 40 секунд
    online_count = Profile.objects.filter(last_seen__gte=active_threshold).count()
    return {'online_users': online_count}







# def nbrb_currency_rates(request):
#     rates = get_nbrb_rates()
#     return {'nbrb_rates': rates}
