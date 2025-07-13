from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Community(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    legal_address = models.TextField("Юридический адрес", blank=True, null=True)
    postal_address = models.TextField("Почтовый адрес", blank=True, null=True)
    bank_details = models.TextField("Банковские реквизиты", blank=True, null=True)
    additional_info = models.TextField("Дополнительная информация", blank=True, null=True)


    def __str__(self):
        return self.name


class Profile(models.Model):
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('chairman', 'Председатель'),
        ('board_member', 'Член правления'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return str(self.user)


def is_chairman_or_board_member(user, community):
    return Profile.objects.filter(
        user=user,
        community=community,
        role__in=['chairman', 'board_member']
    ).exists()


class News(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='news')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Описание новости')
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # Поле мягкого удаления

    def __str__(self):
        return self.title


class ForumPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Комментарий от {self.user.username} к {self.post.title}"


# class Advertisement(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
class Advertisement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    photo = models.ImageField(upload_to='ads_photos/', blank=True, null=True)
    contact = models.CharField(max_length=100, verbose_name='Контакт для связи')  # новое обязательное поле
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='advertisements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Voting(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class Vote(models.Model):
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.BooleanField()

    def __str__(self):
        return str(self.choice)


class PageVisit(models.Model):
    page_name = models.CharField(max_length=100, unique=True)
    visits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.page_name}: {self.visits} посещений"


class Appeal(models.Model):
    APPEAL_TYPES = [
        ('complaint', 'Жалоба'),
        ('proposal', 'Предложение'),
        ('question', 'Вопрос'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appeals')
    appeal_type = models.CharField(max_length=20, choices=APPEAL_TYPES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    response = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    responder = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='responses',
        limit_choices_to={'groups__name__in': ['Председатель', 'Правление']}
    )

    def __str__(self):
        return f"{self.get_appeal_type_display()} от {self.user.username} ({self.created_at.date()})"




class DocumentFolder(models.Model):
    name = models.CharField(max_length=255)
    community = models.ForeignKey('Community', on_delete=models.CASCADE, related_name='folders')

    def __str__(self):
        return self.name

class Document(models.Model):
    DOC_TYPE_CHOICES = [
        ('charter', 'Уставные документы'),
        ('meeting_minutes', 'Протоколы собраний'),
        ('report', 'Отчёты'),
        ('internal_rules', 'Правила внутреннего распорядка'),
        ('other', 'Другая нормативная документация'),
    ]

    community = models.ForeignKey('Community', on_delete=models.CASCADE, related_name='documents')
    folder = models.ForeignKey(DocumentFolder, on_delete=models.PROTECT, related_name='documents', null=True, blank=True)
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, verbose_name='тип документа')
    title = models.CharField(max_length=255, verbose_name='Название документа')
    file = models.FileField(upload_to='community_documents/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # Мягкое удаление

    def delete(self, *args, **kwargs):
        # Вместо физического удаления — помечаем как удалённый
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"[{self.folder.name}] {self.get_doc_type_display()} - {self.title}"


class BoardMember(models.Model):
    ROLE_CHOICES = [
        ('chairman', 'Председатель правления'),
        ('treasurer', 'Казначей'),
        ('board_member', 'Член правления'),
        ('electricity_manager', 'Ответственный за электрохозяйство'),
        ('water_manager', 'Ответственный за водохозяйство'),
    ]

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='board_members')
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=255)
    plot_number = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.get_role_display()} — {self.full_name}"


class PaymentInfo(models.Model):
    community = models.OneToOneField(Community, on_delete=models.CASCADE, related_name='payment_info')

    membership_fee_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Размер членских взносов", null=True, blank=True)
    membership_fee_due_date = models.DateField(
        verbose_name="Срок оплаты членских взносов", null=True, blank=True)
    membership_fee_instruction = models.TextField(
        verbose_name="Инструкция по оплате взносов", blank=True)

    additional_fee_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Размер дополнительных взносов", null=True, blank=True)
    additional_fee_due_date = models.DateField(
        verbose_name="Срок оплаты дополнительных взносов", null=True, blank=True)

    def __str__(self):
        return f"Оплата для {self.community.name}"
