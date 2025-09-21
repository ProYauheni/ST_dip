from django import forms
from .models import Appeal, Document, Comment, Advertisement, News, DocumentFolder, Voting, PaymentInfo, Community, \
                    BoardMember, BallotVote, Ballot, BallotQuestion
from django.forms import modelformset_factory
from django_summernote.widgets import SummernoteWidget
from django.forms import inlineformset_factory


class AppealForm(forms.ModelForm):
    class Meta:
        model = Appeal
        fields = ['appeal_type', 'text']
        widgets = {
            'appeal_type': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class AppealResponseForm(forms.ModelForm):
    class Meta:
        model = Appeal
        fields = ['response']
        widgets = {
            'response': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        labels = {
            'response': 'Ответ на обращение',
        }



class DocumentForm(forms.ModelForm):
    folder = forms.ModelChoiceField(
        queryset=DocumentFolder.objects.none(),
        required=True,
        label='Папка'
    )

    class Meta:
        model = Document
        fields = ['folder', 'doc_type', 'title', 'file']

    def __init__(self, *args, **kwargs):
        community = kwargs.pop('community', None)
        super().__init__(*args, **kwargs)
        if community:
            self.fields['folder'].queryset = DocumentFolder.objects.filter(community=community)
        else:
            self.fields['folder'].queryset = DocumentFolder.objects.none()

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file and file.size > 3 * 1024 * 1024:  # 3 МБ
            raise forms.ValidationError("Файл превышает максимальный размер 3 МБ.")
        return file


class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Comment
        fields = ['content', 'parent_id']
        labels = {'content': '',}
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ваш комментарий...',
                'class': 'form-control',
            }),
        }



# class AdvertisementForm(forms.ModelForm): #форма для объявлений
#     class Meta:
#         model = Advertisement
#         fields = ['title', 'description', 'photo', 'contact']  # добавлено поле contact
#         labels = {
#             'title': 'Заголовок',
#             'description': 'Описание',
#             'photo': 'Фото',
#             'contact': 'Контакт для связи',
#         }
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 4}),
#             'contact': forms.TextInput(attrs={'placeholder': 'Телефон, email или другой контакт'}),
#         }
#
#     def clean_contact(self):
#         contact = self.cleaned_data.get('contact')
#         if not contact or contact.strip() == '':
#             raise forms.ValidationError('Поле "Контакт для связи" обязательно для заполнения.')
#         return contact
class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['topic', 'title', 'description', 'photo', 'contact']
        labels = {
            'topic': 'Тема объявления',
            'title': 'Заголовок',
            'description': 'Описание',
            'photo': 'Фото',
            'contact': 'Контакт для связи',
        }
        widgets = {
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'contact': forms.TextInput(attrs={'placeholder': 'Телефон, email или другой контакт'}),
        }

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if not contact or contact.strip() == '':
            raise forms.ValidationError('Поле "Контакт для связи" обязательно для заполнения.')
        return contact



class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content']
        labels = {
            'title': 'Заголовок',
            'content': 'Описание новости (Фото и видео прикрепить нельзя) :',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': SummernoteWidget(attrs={
                'summernote': {
                    'width': '1000px',   # желаемая ширина
                    'height': '250px',  # желаемая высота
                }
            }),
        }




class VotingForm(forms.ModelForm):
    class Meta:
        model = Voting
        fields = ['community', 'question', 'start_date', 'end_date']
        labels = {
            'question': 'Вопрос',
            'start_date': 'Дата начала голосования',
            'end_date': 'Дата окончания голосования',
        }
        widgets = {
            'community': forms.HiddenInput(),  # Сообщество фиксируем в коде view
            'question': forms.Textarea(attrs={
                'style': 'width: 600px; min-height: 100px;',
            }),
            'start_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'style': 'width: 250px;',
            }),
            'end_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'style': 'width: 250px;',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError("Дата окончания должна быть позже даты начала.")
        return cleaned_data


class VotingEditForm(forms.ModelForm):
    class Meta:
        model = Voting
        fields = ['question', 'start_date', 'end_date']  # добавили start_date
        labels = {
            'question': 'Вопрос',
            'start_date': 'Дата начала голосования',
            'end_date': 'Дата окончания голосования',
        }
        widgets = {
            'question': forms.Textarea(attrs={
                'style': 'width: 600px; min-height: 100px;',
            }),
            'start_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'style': 'width: 250px;',
            }),
            'end_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'style': 'width: 250px;',
            }),
        }



class PaymentInfoForm(forms.ModelForm):
    class Meta:
        model = PaymentInfo
        fields = [
            'membership_fee_amount',
            'membership_fee_due_date',
            'membership_fee_instruction',
            'additional_fee_amount',
            'additional_fee_due_date',
            'additional_fee_instruction',
        ]
        widgets = {
            'membership_fee_due_date': forms.DateInput(attrs={'type': 'date'}),
            'additional_fee_due_date': forms.DateInput(attrs={'type': 'date'}),
            'membership_fee_instruction': forms.Textarea(attrs={'rows': 3}),  # можно добавить удобный виджет
            'additional_fee_instruction': forms.Textarea(attrs={'rows': 3}),  # тоже textarea для инструкции
        }


class CommunityPaymentInfoForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['legal_address', 'postal_address', 'bank_details', 'additional_info']
        widgets = {
            'legal_address': forms.Textarea(attrs={'rows': 1, 'style': 'width: 700px;'}),
            'postal_address': forms.Textarea(attrs={'rows': 1, 'style': 'width: 730px;'}),
            'bank_details': forms.Textarea(attrs={'rows': 2, 'style': 'width: 684px;'}),
            'additional_info': forms.Textarea(attrs={'rows': 3, 'style': 'width: 60px;'}),
        }





class BoardMemberForm(forms.ModelForm):
    full_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='ФИО'
    )
    plot_number = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Номер участка'
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Телефон'
    )

    class Meta:
        model = BoardMember
        fields = ['full_name', 'plot_number', 'phone']

    def clean_plot_number(self):
        data = self.cleaned_data.get('plot_number')
        if data in ['', None]:
            return None
        return data


BoardMemberFormSet = modelformset_factory(
    BoardMember,
    form=BoardMemberForm,
    extra=1,
    can_delete=True,
)


class CommunityInfoForm(forms.ModelForm):
    legal_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Юридический адрес'
    )
    postal_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Почтовый адрес'
    )
    bank_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Банковские реквизиты'
    )
    additional_info = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Дополнительная информация'
    )

    messenger_group_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
        label='Ссылка на группу в мессенджере'
    )

    class Meta:
        model = Community
        fields = ['legal_address', 'postal_address', 'bank_details', 'additional_info', 'messenger_group_link']




class EmailUpdateForm(forms.Form):
    email = forms.EmailField(label='Email для восстановления пароля',
                             max_length=100,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))


"""=============================Голосовалка по 155 указу=================================="""
class BallotForm(forms.ModelForm):
    agenda = forms.CharField(
        widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '300px'}}),
        label='Повестка дня общего собрания'
    )
    instructions = forms.CharField(
        required=False,
        widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '200px'}}),
        label='Порядок заполнения бюллетеня'
    )
    submission_place = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Место представления заполненных бюллетеней'
    )
    start_date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        label='Дата и время начала голосования',
        input_formats=['%Y-%m-%dT%H:%M']
    )
    end_date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        label='Дата и время окончания голосования',
        input_formats=['%Y-%m-%dT%H:%M']
    )
    counting_commission_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        label='Дата заседания счетной комиссии',
        input_formats=['%Y-%m-%d']
    )
    documents = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='Документы и материалы'
    )
    active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Активно'
    )

    class Meta:
        model = Ballot
        fields = [
            'agenda', 'instructions', 'submission_place', 'start_date', 'end_date',
            'counting_commission_date', 'documents', 'active'
        ]


class BallotQuestionForm(forms.ModelForm):
    text = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Формулировка вопроса'
    )
    decision_project = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Формулировка проекта решения'
    )

    class Meta:
        model = BallotQuestion
        fields = ['text', 'decision_project']

BallotQuestionFormSet = inlineformset_factory(
    Ballot, BallotQuestion,
    form=forms.modelform_factory(BallotQuestion, fields=('text',), widgets={
        'text': forms.TextInput(attrs={'class': 'form-control'})
    }),
    extra=1,
    can_delete=True
)

class BallotVoteForm(forms.ModelForm):
    choice = forms.ChoiceField(
        choices=[('for', 'За'), ('against', 'Против'), ('abstained', 'Воздержался')],
        widget=forms.RadioSelect,
        required=True,
    )

    class Meta:
        model = BallotVote
        fields = ['choice']


"""======================================================================================="""