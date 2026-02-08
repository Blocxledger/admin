from django import forms

from theme.models import Theme
from set.models import SetInfo


class ItemSearchForm(forms.Form):
    code = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by set code...',
            'autocomplete': 'off',
            'class': 'search-input',
        })
    )


class BrowseFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Theme.objects.none(),
        required=False,
        empty_label='All Themes',
        widget=forms.Select(attrs={'class': 'w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brick-500 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100'}),
    )
    min_price = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'w-full rounded-lg px-3 py-2 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100'}))
    max_price = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'w-full rounded-lg px-3 py-2 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100'}))
    sort_by = forms.ChoiceField(
        choices=[
            ('-view_count', 'Most Viewed'),
            ('year', 'Year: Oldest'),
            ('-year', 'Year: Newest'),
            ('lego_price', 'Price: Low to High'),
            ('-lego_price', 'Price: High to Low'),
        ],
        required=False,
        initial='-view_count',
        widget=forms.Select(attrs={'class': 'w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brick-500 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Theme.objects.filter(parent__isnull=True)
