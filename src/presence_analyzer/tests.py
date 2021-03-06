# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
from __future__ import unicode_literals

import datetime
import json
import os.path
import unittest

from presence_analyzer import main
from presence_analyzer import utils
from presence_analyzer.helpers import func

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..',
    'runtime', 'data', 'test_data.csv'
)
TEST_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..',
    'runtime', 'data', 'sample_users.xml'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_USERS_XML': TEST_DATA_XML})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/show')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data['10'], {
            'image': 'https://intranet.stxnext.pl:443/api/images/users/141',
            'name': 'Adam P.'
        })

    def test_api_presence_weekday(self):
        """
        Tests presence weekday api response.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        received_data = json.loads(resp.data)
        expected_data = [
            ['Weekday', 'Presence (s)'],
            ['Mon', 0],
            ['Tue', 30047],
            ['Wed', 24465],
            ['Thu', 23705],
            ['Fri', 0],
            ['Sat', 0],
            ['Sun', 0]
        ]

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(expected_data, received_data)

    def test_api_presence_mean_time(self):
        """
        Tests presence weekday api mean time response.
        """
        expected_data = [
            ['Mon', 0],
            ['Tue', 30047],
            ['Wed', 24465],
            ['Thu', 23705],
            ['Fri', 0],
            ['Sat', 0],
            ['Sun', 0]
        ]

        resp = self.client.get('/api/v1/mean_time_weekday/10')
        received_data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(expected_data, received_data)

    def test_api_average_start_end_time(self):
        """
        Tests average start and end time api respone.
        """
        expected_data = [
            ['Mon', 0, 0],
            ['Tue', 34745.0, 64792.0],
            ['Wed', 33592.0, 58057.0],
            ['Thu', 38926.0, 62631.0],
            ['Fri', 0, 0],
            ['Sat', 0, 0],
            ['Sun', 0, 0]
        ]

        resp = self.client.get('/api/v1/presence_start_end/10')
        received_data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(expected_data, received_data)

    def test_api_average_by_month(self):
        """
        Tests average hourly presence by month api response.
        """
        expected_data = [
            ['Jan', []],
            ['Feb', []],
            ['Mar', []],
            ['Apr', []],
            ['May', []],
            ['Jun', []],
            ['Jul', []],
            ['Aug', []],
            ['Sep', 20],
            ['Oct', []],
            ['Nov', []],
            ['Dec', []]
        ]

        resp = self.client.get('/api/v1/average_by_month/10')
        received_data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(expected_data, received_data)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_group_by_weekday(self):
        """
        Test grouping of entries.
        """
        data = utils.get_data()
        result_from_function = utils.group_by_weekday(data[10])

        self.assertEqual(result_from_function,
                         [[], [30047], [24465], [23705], [], [], []])

    def test_seconds_since_midnight(self):
        """
        Test if function returns positive value.
        """
        time_sample = datetime.datetime.strptime('7:20:21', '%H:%M:%S').time()
        result_from_function = utils.seconds_since_midnight(time_sample)

        self.assertEqual(result_from_function, 26421)

    def test_interval(self):
        """
        Test if function returns correct value.
        """
        start_time_sample = datetime.datetime.strptime('7:20:21',
                                                       '%H:%M:%S').time()
        end_time_sample = datetime.datetime.strptime('16:59:21',
                                                     '%H:%M:%S').time()
        interval_function_result = utils.interval(start_time_sample,
                                                  end_time_sample)

        self.assertEqual(interval_function_result, 34740)

    def test_mean(self):
        """
        Test if function returns positive value.
        """
        result_from_function = utils.mean([24123.0, 16564.0, 25321.0,
                                           22984.0, 6426.0, 0, 0])

        self.assertEqual(result_from_function, 13631.142857142857)

    def test_average_start_end_times(self):
        """
        Test if function returns correct average.
        """
        expected_data = [
            [0, 0, 0],
            [1, 34745.0, 64792.0],
            [2, 33592.0, 58057.0],
            [3, 38926.0, 62631.0],
            [4, 0, 0],
            [5, 0, 0],
            [6, 0, 0]
        ]

        data = utils.get_data()
        result_from_function = utils.group_by_average_start_end_time(data[10])

        self.assertEqual(result_from_function, expected_data)

    def test_caching_decorator(self):
        """
        Test if caching decorator returns result from cache.
        """
        cache_func = utils.cache(600)(func)

        self.assertEqual(cache_func(10), 10)
        self.assertEqual(cache_func(123), 10)

        utils.STORAGE['func']['TIME'] = 0
        self.assertEqual(124, cache_func(124))

        def test_all_ids_to_names_xml(self): # pylint: disable=unused-variable
            """
            Test multiple ids to names assignment return value
            """
            expected_data = [{
                "10":{
                    "image":
                        "https://intranet.stxnext.pl:443/api/images/users/141",
                    "name": "Adam P."},
                "11":{
                    "image":
                        "https://intranet.stxnext.pl:443/api/images/users/176",
                    "name": "Adrian K."}
            }]
            data = utils.get_data()
            result_from_function = utils.assign_ids_to_names_from_xml(data)

            self.assertEqual(result_from_function, expected_data)

        def test_single_id_to_names_xml(self): # pylint: disable=unused-variable
            """
            Test single id to name assignment return value
            """
            expected_data = [{
                "image": "https://intranet.stxnext.pl:443/api/images/users/176",
                "name":
                "Adrian K."
            }]
            data = utils.get_data()
            result_from_function = utils.assign_ids_to_names_from_xml(data, 11)

            self.assertEqual(expected_data, result_from_function)

    def test_average_by_month(self):
    """
    Test if function returns correct list of averages.
    """
    expected_data = [[], [], [], [], [], [], [], [], 20, [], [], []]

    data = utils.get_data()
    result_from_function = utils.group_by_average_monthly_hours(data[10])

    self.assertEqual(result_from_function, expected_data)


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
