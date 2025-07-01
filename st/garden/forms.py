from django import forms
from .models import Appeal, Document, Comment, Advertisement

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
    class Meta:
        model = Document
        fields = ['doc_type', 'title', 'file']



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
            'contact': 'Контакт для связи',  # можно явно указать метку, но если есть verbose_name, Django подставит его автоматически
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'contact': forms.TextInput(attrs={'placeholder': 'Телефон, email или другой контакт'}),
        }

