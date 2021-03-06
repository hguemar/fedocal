#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
 (c) 2012 - Copyright Pierre-Yves Chibon
 Author: Pierre-Yves Chibon <pingou@pingoured.fr>

 Distributed under License GPLv3 or later
 You can find a copy of this license on the website
 http://www.gnu.org/licenses/gpl.html

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 MA 02110-1301, USA.

 fedocal.model test script
"""

__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources

import unittest
import sys
import os

from datetime import date
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import fedocal
import fedocal.api
import fedocal.fedocallib as fedocallib
from tests import Modeltests, TODAY


# pylint: disable=E1103
class FlaskApitests(Modeltests):
    """ Flask application API tests. """

    def __setup_db(self):
        """ Add a calendar and some meetings so that we can play with
        something. """
        from test_meeting import Meetingtests
        meeting = Meetingtests('test_init_meeting')
        meeting.session = self.session
        meeting.test_init_meeting()

    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        super(FlaskApitests, self).setUp()

        fedocal.APP.config['TESTING'] = True
        fedocal.SESSION = self.session
        fedocal.api.SESSION = self.session
        self.app = fedocal.APP.test_client()

    def test_api(self):
        """ Test the index function. """
        output = self.app.get('/api')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/api/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<title> API   - Fedocal</title>' in output.data)
        self.assertTrue('<h1 class="title">API documentation</h1>' in output.data)
        #self.assertTrue('<code>/api/date/calendar_name/</code>' \
            #in output.data)
        #self.assertTrue('<code>/api/place/region/calendar_name/</code>' \
            #in output.data)

    def test_api_date_default(self):
        """ Test the api_date_default function. """
        output = self.app.get('/api/meetings/?calendar=foobar')
        self.assertEqual(output.status_code, 200)
        start_date = date.today() - timedelta(days=30)
        end_date = date.today() + timedelta(days=180)
        self.assertEqual(output.data,
            '{"meetings": [], "arguments": {"start": "%s", '
            '"calendar": "foobar", "end": "%s", "region": null}}'
            % (start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')))

        self.__setup_db()

        output = self.app.get('/api/meetings/?calendar=test_calendar')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(' "meeting_manager": "pingou, shaiton,",' in \
            output.data)
        self.assertTrue('"meeting_name": "test-meeting2"' in output.data)
        self.assertEqual(output.data.count('meeting_name'), 49)

        output = self.app.get('/api/meetings/?calendar=test_calendar4')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data.count('meeting_name'), 3)

    def test_api_date(self):
        """ Test the api_date function. """
        end_date = TODAY + timedelta(days=10)
        output = self.app.get('/api/meetings/?calendar=foobar&start=%s&end=%s'
            % (TODAY, end_date))
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data,
            '{"meetings": [], "arguments": {"start": "%s", '
            '"calendar": "foobar", "end": "%s", "region": null}}'
            % (TODAY.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

        self.__setup_db()

        output = self.app.get('/api/meetings/?calendar=test_calendar'
            '&start=%s&end=%s' % (TODAY, end_date))
        self.assertEqual(output.status_code, 200)
        self.assertTrue(' "meeting_manager": "pingou, shaiton,",' in \
            output.data)
        self.assertTrue('"meeting_name": "Another test meeting2",' in \
            output.data)
        self.assertEqual(output.data.count('meeting_name'), 8)

        end_date = TODAY + timedelta(days=2)
        output = self.app.get('/api/meetings/?calendar=test_calendar4'
            '&start=%s&end=%s' % (TODAY, end_date))
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data.count('meeting_name'), 2)

        end_date = TODAY + timedelta(days=2)
        output = self.app.get('/api/meetings/?start=%s&end=%s'
                              % (TODAY, end_date))
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data.count('meeting_name'), 5)

    def test_api_date_error(self):
        """ Test the api_date function with wrong input. """
        self.__setup_db()

        output = self.app.get('/api/meetings/?calendar=test_calendar'
            '&start=%s&end=2012-09-aw' % (TODAY))
        self.assertEqual(output.status_code, 400)
        self.assertTrue('"error": "Invalid end date format: ' in \
                        output.data)

    def test_api_place_default(self):
        """ Test the api_place_default function. """

        output = self.app.get('/api/meetings/?calendar=foobar&region=EMEA')
        self.assertEqual(output.status_code, 200)
        start_date = date.today() - timedelta(days=30)
        end_date = date.today() + timedelta(days=180)
        self.assertEqual(output.data,
            '{"meetings": [], '
            '"arguments": {'
            '"start": "%s", '
            '"calendar": "foobar", '
            '"end": "%s", '
            '"region": "EMEA"}'
            '}' % (start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')))

        self.__setup_db()

        output = self.app.get('/api/meetings/?calendar=test_calendar4&region=APAC')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data,
            '{"meetings": [], "arguments": {"start": "%s", '
            '"calendar": "test_calendar4", "end": "%s", '
            '"region": "APAC"}}' %(start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')))

        output = self.app.get('/api/meetings/?calendar=test_calendar4&region=NA')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data.count('meeting_name'), 1)

        output = self.app.get('/api/meetings/?calendar=test_calendar4&region=EMEA')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data.count('meeting_name'), 2)

    def test_api_place(self):
        """ Test the api_place function. """
        end_date = TODAY + timedelta(days=25)
        output = self.app.get('/api/meetings/?calendar=foobar&region=APAC'
                              '&start=%s&end=%s' % (TODAY, end_date))
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data,
            '{"meetings": [], "arguments": {"start": "%s", '
            '"calendar": "foobar", "end": "%s", '
            '"region": "APAC"}}' % (TODAY.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')))

        self.__setup_db()

        output = self.app.get('/api/meetings/?calendar=test_calendar4&region=APAC'
                              '&start=%s&end=%s' % (TODAY, end_date))
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data,
            '{"meetings": [], "arguments": {"start": "%s", '
            '"calendar": "test_calendar4", "end": "%s", '
            '"region": "APAC"}}' % (TODAY.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')))

        output = self.app.get('/api/meetings/?calendar=test_calendar4&region=NA'
                              '&start=%s&end=%s' % (TODAY, end_date))
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data.count('meeting_name'), 1)

        output = self.app.get('/api/meetings/?calendar=test_calendar4&region=EMEA'
                              '&start=%s&end=%s' % (TODAY, end_date))
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data.count('meeting_name'), 2)

        output = self.app.get('/api/meetings/?region=EMEA'
                              '&start=%s&end=%s' % (TODAY, end_date))
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data.count('meeting_name'), 2)

        end_date = TODAY + timedelta(days=1)

        output = self.app.get('/api/meetings/?calendar=test_calendar4&region=NA'
                              '&start=%s&end=%s' % (TODAY, end_date))
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data,
            '{"meetings": [], "arguments": {"start": "%s", '
            '"calendar": "test_calendar4", "end": "%s", '
            '"region": "NA"}}' % (TODAY.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')))

        output = self.app.get('/api/meetings/?calendar=test_calendar4&region=EMEA'
                              '&start=%s&end=%s' % (TODAY, end_date))
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data,
            '{"meetings": [], "arguments": {"start": "%s", '
            '"calendar": "test_calendar4", "end": "%s", '
            '"region": "EMEA"}}' % (TODAY.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')))

    def test_api_place_error(self):
        """ Test the api_date function with wrong input. """
        self.__setup_db()

        end_date = TODAY + timedelta(days=1)
        output = self.app.get('/api/meetings/?calendar=test_calendar4&region=EMEA'
                              '&end=%s&start=2012-12-as' % (end_date))
        self.assertEqual(output.status_code, 400)
        self.assertTrue('"error": "Invalid start date format: ' in \
            output.data)

    def test_api_calendar(self):
        """ Test the api_calendar function. """
        output = self.app.get('/api/calendars/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data,
            '{"calendars": []}')

        self.__setup_db()

        output = self.app.get('/api/calendars/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data.count('calendar_name'), 4)


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(FlaskApitests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
