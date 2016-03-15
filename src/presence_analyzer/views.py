# -*- coding: utf-8 -*-
"""
Defines views.
"""
import calendar
import locale
import logging

from flask import abort, redirect, url_for, make_response # pylint: disable=F0401
from flask.ext.mako import render_template # pylint: disable=F0401

from .main import app
from .utils import (
    assign_ids_to_names_from_xml,
    get_data,
    group_by_average_start_end_time,
    group_by_average_monthly_hours,
    group_by_weekday,
    jsonify,
    mean
)

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
locale.setlocale(locale.LC_COLLATE, "pl_PL.UTF-8")

@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect(url_for('show_data'))


@app.route('/api/v1/users', methods=['GET'])
@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
@jsonify
def users_view(user_id=None):
    """
    Users listing for dropdown.
    """
    data = get_data()
    assigned_data = assign_ids_to_names_from_xml(data, user_id)
    result = []

    if len(assigned_data) == 2: #single user returned
            return assigned_data
    else: #transform dict into list so we can sort it with sorted()
        for k, v in assigned_data.iteritems():
            v['id'] = k
            result.append(v)

        result = sorted(result, key=lambda k: k['name'], cmp=locale.strcoll)

    return result


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns averaged start and end time grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    result = [
        [calendar.day_abbr[part[0]], part[1], part[2]]
        for part in group_by_average_start_end_time(data[user_id])
    ]

    return result


@app.route('/api/v1/average_by_month/<int:user_id>', methods=['GET'])
@jsonify
def average_by_month_view(user_id):
    """
    Returns average hours worked per month.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    result = [
        [calendar.month_abbr[month_count],
        number_of_hours if number_of_hours else 0]
        for month_count, number_of_hours
        in enumerate(group_by_average_monthly_hours(data[user_id]), start=1)
    ]

    return result


@app.route('/show')
@app.route('/show/<string:template_name>')
def show_data(template_name='presence_weekday'):
    """
    Main view for presenting data bookmarks.
    """
    try:
        return make_response(render_template(template_name + '.html'))
    except:
        abort(404)#pylint: disable=bare-except
