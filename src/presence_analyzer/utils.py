# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""
import csv
import time # pylint: disable=W0611
from datetime import datetime
from functools import wraps
from json import dumps
from lxml import etree

from flask import Response # pylint: disable=F0401

from .main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def assign_ids_to_names_from_xml(data, user=None): # pylint:disable=unused-argument
    """
    Parses raw user id's from CSV data file and replaces them
    with their corresponding full name from xml file.
    """
    with open(app.config['DATA_USERS_XML'], 'r') as xmlfile:
        root = etree.parse(xmlfile) # pylint:disable=no-member
        server = root.find('server')
        host = server.find('host').text
        protocol = server.find('protocol').text
        port = server.find('port').text
        users = root.find('users')
        result = {
            int(user.get('id')): {
                'name': user.find('name').text,
                'image': "{protocol}://{host}:{port}{user_url}".format(
                    protocol=protocol,
                    host=host,
                    port=port,
                    user_url=user.find('avatar').text
                )
            }
            for user in users
        }

    if user:
        return result[user]
    else:
        return result


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def group_by_average_start_end_time(items):
    """
    Groups average start and end times by weekday.
    """
    buffer = {i: {'start': [], 'end': []} for i in xrange(7)} #pylint: disable=redefined-builtin

    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        buffer[date.weekday()]['start'].append(seconds_since_midnight(start))
        buffer[date.weekday()]['end'].append(seconds_since_midnight(end))

    for weekday in buffer:
        buffer[weekday]['start'] = mean(buffer[weekday]['start'])
        buffer[weekday]['end'] = mean(buffer[weekday]['end'])

    result = []
    for key in buffer:
        result.append([key, buffer[key]['start'], buffer[key]['end']])

    return result


def seconds_since_midnight(time): #pylint: disable=redefined-outer-name
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0
