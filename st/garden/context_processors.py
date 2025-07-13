from .models import PageVisit

def total_visits_processor(request):
    counter, created = PageVisit.objects.get_or_create(page_name='main_page')
    return {
        'total_visits': counter.visits
    }
