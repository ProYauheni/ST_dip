from django.shortcuts import redirect
from django.urls import reverse

class CommunityActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        # Проверяем, что пользователь аутентифицирован и есть профиль с сообществом
        if user.is_authenticated:
            profile = getattr(user, 'profile', None)
            if profile and not profile.community.is_active:
                # Исключаем страницы выхода и страницы отключения, чтобы избежать цикла
                if request.path not in [reverse('community_disabled'), reverse('logout')]:
                    return redirect('community_disabled')
        response = self.get_response(request)
        return response
