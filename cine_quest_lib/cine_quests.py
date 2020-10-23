# Library to perform queries to TMDB and IMDB databases

from cine_quest_lib import config
import requests
from bs4 import BeautifulSoup
import json


def query_tmdb_link(name):
    """Provides a query the TMDB databser
    :param name: A name of the movie/series to look for
    """
    tmdb_endpoint = 'https://api.themoviedb.org/3/search/multi?'
    tmdb_dct = {
        'api_key': config.tmdb_key,
        'language': 'ru',
        'query': name,
        'page': 1,
        'include_adult': 'false'
        }
    return requests.get(tmdb_endpoint, params=tmdb_dct)


def get_movie_imdb_id(tmdb_id):
    """Get movie's imdb_id in the TMDB database
    """
    movie_endpoint = 'https://api.themoviedb.org/3/movie/{}/external_ids?'.format(tmdb_id)
    tmdb_dct = {
        'api_key': config.tmdb_key
        }
    external_ids = requests.get(movie_endpoint, params=tmdb_dct).json()
    return external_ids['imdb_id']


def get_tv_imdb_id(tmdb_id):
    """Get TV show imdb_id in the TMDB database
    """
    tv_endpoint = 'https://api.themoviedb.org/3/tv/{}/external_ids?'.format(tmdb_id)
    tmdb_dct = {
        'api_key': config.tmdb_key
        }
    external_ids = requests.get(tv_endpoint, params=tmdb_dct).json()
    return external_ids['imdb_id']


def get_imdb_rating(tmdb_id, flag='movie'):
    """Get IMDB rating
    """
    if flag == 'movie':
        imdb_id = get_movie_imdb_id(tmdb_id)
    else:
        imdb_id = get_tv_imdb_id(tmdb_id)

    rating = None

    if imdb_id is not None:
        r = requests.get('https://www.imdb.com/title/{}'.format(imdb_id))
        r_soup = BeautifulSoup(r.text, 'html.parser')
        data = json.loads(r_soup.find("script", type="application/ld+json").text)
        rating = data['aggregateRating']['ratingValue']
        duration = data['duration'].split('T')[1]
    return rating, duration
