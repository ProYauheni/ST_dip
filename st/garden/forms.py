from django import forms
from .models import Appeal, Document, Comment, Advertisement, News, DocumentFolder, Voting, PaymentInfo, Community

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
        labels = {'content': '',}  # убираем метку
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ваш комментарий...'}),
        }




class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'description', 'photo', 'contact']  # добавлено поле contact
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'photo': 'Фото',
            'contact': 'Контакт для связи',
        }
        widgets = {
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
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
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
        ]
        widgets = {
            'membership_fee_due_date': forms.DateInput(attrs={'type': 'date'}),
            'additional_fee_due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CommunityPaymentInfoForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['legal_address', 'postal_address', 'bank_details', 'additional_info']
        widgets = {
            'legal_address': forms.Textarea(attrs={'rows': 1, 'style': 'width: 700px;'}),
            'postal_address': forms.Textarea(attrs={'rows': 1, 'style': 'width: 730px;'}),
            'bank_details': forms.Textarea(attrs={'rows': 2, 'style': 'width: 684px;'}),
            'additional_info': forms.Textarea(attrs={'rows': 3, 'style': 'width: 630px;'}),
        }