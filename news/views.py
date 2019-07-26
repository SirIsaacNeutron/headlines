from django.shortcuts import render, redirect
from django import forms

import json

from newsapi import NewsApiClient

from my_secrets import secrets

NEWS_SOURCES = {
    'bbc-news': 'BBC News',
    'the-economist': 'The Economist'
}

CHOICES = sorted(NEWS_SOURCES.items())


class NewsSourceForm(forms.Form):
    sources = forms.MultipleChoiceField(required=True, choices=CHOICES)
    query = forms.CharField(required=True)


def home(request):
    if request.method == 'POST':
        form = NewsSourceForm(request.POST)

        if form.is_valid():
            news_sources = form.cleaned_data['sources']
            client = NewsApiClient(api_key=secrets.NEWS_API_KEY)

            query = form.cleaned_data['query']
            json_response = client.get_top_headlines(q=query,
                                sources=','.join(news_sources))

            total_results = json_response['totalResults']
    else:
        form = NewsSourceForm()
    return render(request, 'news/home.html', {'form': form})
