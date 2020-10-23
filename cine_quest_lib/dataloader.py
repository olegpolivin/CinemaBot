# Class to find and load data
from bs4 import BeautifulSoup
from collections import namedtuple
import requests

from cine_quest_lib import config
from cine_quest_lib import cine_quests


class Fetcher:
    """Class to fetch data using the TMDB site as main source.
    """
    def __init__(self):
        self.output = {}
        self.num_movies = None

    def get_data(self, name):
        """Get data from the TMDB site.
        Also gets rating, duration data from IMDB site.
        :param name: Movie/TV show name to get data for.
        """
        self.output = {}
        request = cine_quests.query_tmdb_link(name).json()
        self.num_movies = request['total_results']
        r_dct = request['results']

        for i in range(len(r_dct)):
            if i > config.limit:
                break
            dct = r_dct[i]
            search_id = dct['id']
            media_type = dct['media_type']
            movie_data = self.parse_tmdb_dict(dct, media_type)
            rating, duration = self.get_imdb_data(search_id, media_type)

            self.output[search_id] = {
                'title': movie_data.title,
                'rating': rating,
                'release_date': movie_data.release_date,
                'poster_path': movie_data.path,
                'overview': movie_data.overview,
                'duration': duration
                }

    def get_imdb_data(self, search_id, media_type):
        """A separate method to get imdb data: rating and duration
        """
        # IMDB rating
        try:
            rating, duration = cine_quests.get_imdb_rating(search_id, media_type)
            rating = f'{rating}/10'
        except Exception:
            rating, duration = 'Нет данных', 'Нет данных'
        return rating, duration

    def parse_tmdb_dict(self, tmdb_dct, media_type):
        """Method to parse tmdb dictionary returned by the request
        to the TMDB database. It consists of two methods:
        normal case and special case, and returns a namedtuple.
        """
        movie_desc = namedtuple('Description', ['title',
                                                'release_date',
                                                'path',
                                                'overview'])
        if 'known_for' in tmdb_dct:
            movie_data = movie_desc(*self.parse_tmdb_dict_special_case(tmdb_dct))
        else:
            movie_data = movie_desc(*self.parse_tmdb_dict_normal_case(tmdb_dct, media_type))
        return movie_data

    def parse_tmdb_dict_normal_case(self, tmdb_dct, media_type):
        """A separate method to parse the dictionary returned to
        a request to TMDB database. It returns title, release date,
        path to a poster and an overview for a movie/tv series.
        """
        try:
            poster_path = tmdb_dct['poster_path']
            path = config.poster_path+poster_path
        except Exception:
            path = None
        try:
            overview = tmdb_dct['overview']
        except Exception:
            overview = ''

        if media_type == 'movie':
            title = tmdb_dct.get('title', ''), tmdb_dct.get('original_title', '')
            release_date = tmdb_dct.get('release_date', 'Нет')
        elif media_type == 'tv':
            title = tmdb_dct.get('original_name', ''), 'Сериал'
            release_date = tmdb_dct.get('first_air_date', 'Нет')
        else:
            title = 'Имени нет'
            release_date = 'Нет'
        return title, release_date, path, overview

    def parse_tmdb_dict_special_case(self, tmdb_dct):
        """A special case treatment when a field "known_for"
        is present in the dictionary returned by the tmdb database.
        It overwrites 'title', 'release date', path' and 'overview'
        data of a movie in that case.
        """
        try:
            title = tmdb_dct['known_for'][0].get('title', ''), tmdb_dct['known_for'][0].get('original_title', '')
        except Exception:
            title = tmdb_dct.get('name', 'Нет данных'), 'Нет данных'
        try:
            release_date = tmdb_dct['known_for'][0].get('release_date', 'Нет')
        except Exception:
            release_date = 'Нет'
        try:
            path = config.poster_path+tmdb_dct['known_for'][0]['poster_path']
        except Exception:
            path = None
        try:
            overview = tmdb_dct['known_for'][0].get('overview', '')
        except Exception:
            overview = ''
        return title, release_date, path, overview

    def pretty_output(self):
        pretty = ''
        for j, search_id in enumerate(self.output):
            item_number = j + 1
            dct = self.output[search_id]
            title, original_title = dct['title']
            year = dct['release_date'][:4]
            rating = dct['rating']
            duration = dct['duration']
            pretty += (
                f'{item_number}.'
                f' {title} '
                f'({original_title})\n'
                f'⌚:{duration} \n'
                f'[Год выпуска ({year}), Рейтинг ({rating})]\n'
                f'/i{search_id}\n\n'
            )
        return pretty
