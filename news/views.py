from django.shortcuts import render, redirect
from django import forms
from django.http import Http404

import os

from newsapi import NewsApiClient

NEWS_SOURCES = {
    'bbc-news': 'BBC News',
    'the-economist': 'The Economist',
    'business-insider': 'Business Insider',
    'cnn': 'CNN',
    'daily-mail': 'Daily Mail',
    'cnbc': 'CNBC',
    'nbc-news': 'NBC',
    'reddit-r-all': '/r/all',
    'reuters': 'Reuters',
    'the-hill': 'The Hill',
    'the-new-york-times': 'The New York Times',
    'the-wall-street-journal': 'The Wall Street Journal',
    'the-washington-post': 'The Washington Post',
    'the-huffington-post': 'The Huffington Post',
    'the-telegraph': 'The Telegraph',
    'usa-today': 'USA Today',
    'vice-news': 'Vice News',
    'time': 'Time Magazine',
    'the-verge': 'The Verge',
    'the-times-of-india': 'The Times of India',
    'politico': 'Politico',
    'techcrunch': 'TechCrunch',
    'spiegel-online': 'Spiegel Online',
    'national-geographic': 'National Geographic',
    'msnbc': 'MSNBC',
    'national-review': 'National Review',
    'hacker-news': 'Hacker News',
    'le-monde': 'Le Monde',
    'fortune': 'Fortune Magazine',
    'cbs-news': 'CBS News',
    'buzzfeed': 'Buzzfeed',
    'bloomberg': 'Bloomberg',
    'associated-press': 'Associated Press',
    'abc-news': 'ABC News',
    'abc-news-au': 'ABC News (AU)',
    'ars-technica': 'Ars Technica',
    'axios': 'Axios',
    'the-washington-times': 'The Washington Times',
    'new-york-magazine': 'New York Magazine',
    'newsweek': 'Newsweek',
}

CHOICES = sorted(NEWS_SOURCES.items())


class NewsSourceForm(forms.Form):
    sources = forms.MultipleChoiceField(required=True, choices=CHOICES)
    query = forms.CharField(required=True)


class Article:
    def __init__(self, title, description, url, source_name, published_at):
        self.title = title
        self.description = description
        self.url = url
        self.source_name = source_name
        self.published_at = published_at


def get_context_dict(context, json_response):
    for result in json_response['articles']:
        source_name = result['source']['name']
        title = result['title']
        description = result['description']
        url = result['url']
        published_at = result['publishedAt'].split('T')[0]

        context['articles'].append(Article(title, description, url,
                                    source_name, published_at))

    return context


def category(request, category: str):
    client = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY'))

    try:
        json_response = client.get_top_headlines(category=category,
                                                country='us')
    # If category is invalid
    except ValueError:
        raise Http404('Invalid category')

    context = {
        'total_results': json_response['totalResults'],
        'category': category.title(),
        'articles': []
    }

    context = get_context_dict(context, json_response)

    return render(request, 'news/results.html', context)

def results(request):
    try:
        json_response = request.session['json_response']
        del request.session['json_response']
    except KeyError:
        return redirect('news-home')

    context = {
        'total_results': json_response['totalResults'],
        'articles': []
    }

    context = get_context_dict(context, json_response)

    return render(request, 'news/results.html', context)

def home(request):
    if request.method == 'POST':
        form = NewsSourceForm(request.POST)

        if form.is_valid():
            news_sources = form.cleaned_data['sources']
            client = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY'))

            query = form.cleaned_data['query']
            json_response = client.get_everything(q=query,
                                sources=','.join(news_sources),
                                page_size=100)

            request.session['json_response'] = json_response
            return redirect('news-results')
    else:
        form = NewsSourceForm()
    return render(request, 'news/home.html', {'form': form})
