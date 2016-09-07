import json
import time

from flask import abort, Blueprint, redirect, render_template, url_for, flash
from flask_login import current_user, login_required

import config
from forms import EventForm
from models import db, Event
from util import admin_required, isoformat, RateLimitedException, rate_limit

blueprint = Blueprint('events', __name__, template_folder='templates')


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def events_create():
    event_create_form = EventForm()
    if event_create_form.validate_on_submit():
        try:
            create_event(event_create_form)
        except RateLimitedException, e:
            return str(e), 429
        return redirect(url_for('.events_owned'))
    return render_template('events/create.html', event_create_form=event_create_form)


@rate_limit(limit=1, interval=24 * 3600, scope_func=lambda: 'user:%s' % current_user.username)
def create_event(event_create_form):
    new_event = Event(owner=current_user)
    event_create_form.populate_obj(new_event)
    db.session.add(new_event)
    db.session.commit()


@blueprint.route('/list/json')
@blueprint.route('/list/json/page/<int:page_number>')
def events_list_json(page_number=1):
    if page_number <= 0:
        abort(404)

    page_size = config.EVENT_LIST_PAGE_SIZE
    page_offset = (page_number - 1) * page_size
    events = Event.query.order_by(Event.start_time.desc()).offset(page_offset).limit(page_size).all()
    if page_number != 1 and not events:
        abort(404)

    event_list = [{
                      'id': event.id,
                      'approved': event.approved,
                      'name': event.title,
                      'startTime': event.start_time * 1000,
                      'startTimeFormat': isoformat(event.start_time),
                      'endTime': (event.start_time + event.duration * 60 * 60) * 1000,
                      'duration': event.duration
                  } for event in events]
    return json.dumps(event_list)


@blueprint.route('/')
@blueprint.route('/all')
@blueprint.route('/all/page/<int:page_number>')
def events_all(page_number=1):
    if page_number <= 0:
        abort(404)

    page_size = config.EVENT_LIST_PAGE_SIZE
    page_offset = (page_number - 1) * page_size
    # Offset + limit for pagination is inefficient; implement page_start based pages if perf issues.
    events = Event.query.filter_by(approved=True, removed=False).order_by(Event.start_time.desc()) \
        .offset(page_offset).limit(page_size + 1).all()
    if page_number != 1 and not events:
        abort(404)

    last_page = len(events) <= page_size
    if not last_page:
        events.pop()

    return render_template('events/list.html', tab='all', page_number=page_number, last_page=last_page, events=events)


# todo
@blueprint.route('/upcoming')
@blueprint.route('/upcoming/page/<int:page_number>')
def events_upcoming(page_number=1):
    if page_number <= 0:
        abort(404)

    page_size = config.EVENT_LIST_PAGE_SIZE
    page_offset = (page_number - 1) * page_size
    upcoming_events = Event.query.filter_by(approved=True, removed=False).filter(Event.start_time > time.time()) \
        .order_by(Event.start_time.desc()).offset(page_offset).limit(page_size + 1).all()
    if page_number != 1 and not upcoming_events:
        abort(404)

    last_page = len(upcoming_events) <= page_size
    if not last_page:
        upcoming_events.pop()

    return render_template('events/list.html', tab='upcoming', page_number=page_number, last_page=last_page,
                           events=upcoming_events)


# todo
@blueprint.route('/past')
@blueprint.route('/past/page/<int:page_number>')
def events_past(page_number=1):
    if page_number <= 0:
        abort(404)

    page_size = config.EVENT_LIST_PAGE_SIZE
    page_offset = (page_number - 1) * page_size
    past_events = Event.query.filter_by(approved=True, removed=False).filter(Event.end_time <= time.time()) \
        .order_by(Event.start_time.desc()).offset(page_offset).limit(page_size + 1).all()
    if page_number != 1 and not past_events:
        abort(404)

    last_page = len(past_events) <= page_size
    if not last_page:
        past_events.pop()

    return render_template('events/list.html', tab='past', page_number=page_number, last_page=last_page,
                           events=past_events)


@blueprint.route('/unapproved')
@blueprint.route('/unapproved/page/<int:page_number>')
@admin_required
def events_unapproved(page_number=1):
    if page_number <= 0:
        abort(404)

    page_size = config.EVENT_LIST_PAGE_SIZE
    page_offset = (page_number - 1) * page_size
    unapproved_events = Event.query.filter_by(approved=False, removed=False).order_by(Event.start_time.desc()) \
        .offset(page_offset).limit(page_size + 1).all()
    if page_number != 1 and not unapproved_events:
        abort(404)

    last_page = len(unapproved_events) <= page_size
    if not last_page:
        unapproved_events.pop()

    return render_template('events/list.html', tab='unapproved', page_number=page_number, last_page=last_page,
                           events=unapproved_events, enabled_actions=['approve'])


@blueprint.route('/owned')
@blueprint.route('/owned/page/<int:page_number>')
@login_required
def events_owned(page_number=1):
    if page_number <= 0:
        abort(404)

    page_size = config.EVENT_LIST_PAGE_SIZE
    page_offset = (page_number - 1) * page_size
    owned_events = current_user.events.filter_by(removed=False).order_by(Event.start_time.desc()) \
        .offset(page_offset).limit(page_size + 1).all()
    if page_number != 1 and not owned_events:
        abort(404)

    last_page = len(owned_events) <= page_size
    if not last_page:
        owned_events.pop()

    return render_template('events/list.html', tab='owned', page_number=page_number, last_page=last_page,
                           events=owned_events, enabled_actions=['manage', 'remove'])


@blueprint.route('/<int:event_id>')
def events_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('events/detail.html', event=event)


@blueprint.route('/<int:event_id>/approve', methods=['POST'])
@admin_required
def events_approve(event_id):
    event = Event.query.get_or_404(event_id)
    if event.approved:
        flash('\'%s\' already approved!' % event.title)
    else:
        event.approved = True
        db.session.commit()
        flash('\'%s\' approved!' % event.title)
    return redirect(url_for('.events_unapproved'))


@blueprint.route('/<int:event_id>/manage', methods=['GET', 'POST'])
@login_required
def events_manage(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user != event.owner:
        abort(403)
    event_form = EventForm(obj=event)
    if event_form.validate_on_submit():
        event_form.populate_obj(event)
        db.session.commit()
        return redirect(url_for('.events_detail', event_id=event_id))
    return render_template('events/manage.html', event=event, event_form=event_form)


@blueprint.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def events_remove(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user != event.owner:
        abort(403)
    event.removed = True
    db.session.commit()
    return redirect(url_for('.events_owned'))
