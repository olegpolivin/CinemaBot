import pytest
import requests

from cine_quest_lib import config
from cine_quest_lib import cine_quests as cq




class MockResponse:
    @staticmethod
    def json():
        return {'username': 'ioranaBot'}


def get_json(url):
    r = requests.get(url)
    return r.json()


def test_bot_name(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse()
    method = 'getMe'
    url = 'https://api.telegram.org/bot{0}/{1}'.format(config.token, method)
    monkeypatch.setattr(requests, "get", mock_get)
    result = get_json(url)
    assert result['username'] == 'ioranaBot'


def test_bot_name2():
    method = 'getMe'
    url = 'https://api.telegram.org/bot{0}/{1}'.format(config.token, method)
    general_info = get_json(url)['result']
    assert general_info['username'] == 'ioranaBot'

class CaseYear(object):
    def __init__(self, movie_name, expected_release_year):
        self.movie_name = movie_name
        self.expected_release_year = expected_release_year


TEST_CASES_RELEASE_YEAR= [
    CaseYear(movie_name='Солдат Джейн', expected_release_year='1997'),
    CaseYear(movie_name='Веном', expected_release_year='2018'),
    CaseYear(movie_name='Магия лунного света', expected_release_year='2014'),
    CaseYear(movie_name='Мстители: Война бесконечности', expected_release_year='2018'),
    CaseYear(movie_name='Вертикаль', expected_release_year='1966'),
    CaseYear(movie_name='127 часов', expected_release_year='2010'),
]
ids = ['IGJane', 'Venom', 'Magic in the moonlight', 'Avengers', 'Vertikal', '127 hours']

@pytest.mark.parametrize('test_case', TEST_CASES_RELEASE_YEAR, ids=ids)
def test_release_year(test_case):
    json_data = cq.query_tmdb_link(test_case.movie_name).json()
    release_date = json_data['results'][0]['release_date']
    release_year = release_date[:4]
    assert release_year == test_case.expected_release_year


class CaseIMDBRating(object):
    def __init__(self, tmdb_id, expected_rating):
        self.tmdb_id = tmdb_id
        self.expected_rating = expected_rating


TEST_CASES_IMDB_RATING= [
    CaseIMDBRating(tmdb_id=680, expected_rating='8.9'),
]
ids = ['Pulp Fiction', 'Hackers']

@pytest.mark.parametrize('test_case', TEST_CASES_IMDB_RATING, ids=ids)
def test_imdb_rating(test_case):
    rating, _ = cq.get_imdb_rating(test_case.tmdb_id)
    assert rating == test_case.expected_rating