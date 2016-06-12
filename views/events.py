from flask import Blueprint, render_template, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user
from forms import EventCreateForm

from models import Event
from util import admin_required

import json

blueprint_events = Blueprint('events', __name__, template_folder='templates')

@blueprint_events.route('/create', methods=['GET', 'POST'])
@login_required
def events_create():
    event_create_form = EventCreateForm()
    if event_create_form.validate_on_submit():
        new_event = Event(owner=current_user,
                          title=event_create_form.title.data,
                          start_time=event_create_form.start_time.data,
                          duration=event_create_form.duration.data,
                          description=event_create_form.description.data,
                          link=event_create_form.link.data)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('.events_list'))
    return render_template('events/create.html', event_create_form=event_create_form)


@blueprint_events.route('/list/json')
def events_list_json():
    events = Event.query.filter_by().order_by(Event.start_time.desc()).all()
    event_list = []
    for event in events:
        start_time = int(event.start_time.strftime("%s"))
        obj = {
            "id": event.id,
            "name": event.title,
            "startTime": start_time * 1000,
            "endTime": (start_time + event.duration * 60 * 60) * 1000,
            "duration": event.duration
        }
        event_list.append(obj)
    return json.dumps(event_list)


@blueprint_events.route('/')
@blueprint_events.route('/all')
def events_all():
    events = Event.query.filter_by(approved=True).order_by(Event.start_time.desc()).all()
    return render_template('events/list.html', tab="all", events=events)

#todo
@blueprint_events.route('/upcoming')
def events_upcoming():
    events = Event.query.filter_by(approved=True).order_by(Event.start_time.desc()).all()
    return render_template('events/list.html', tab="upcoming", events=events)

#todo
@blueprint_events.route('/past')
def events_past():
    events = Event.query.filter_by(approved=True).order_by(Event.start_time.desc()).all()
    return render_template('events/list.html', tab="past", events=events)


@blueprint_events.route('/unapproved')
@admin_required
def events_unapproved():
    unapproved_events = Event.query.filter_by(approved=False).order_by(Event.start_time.desc()).all()
    return render_template('events/list.html', tab="unapproved", events=unapproved_events, enabled_actions=['approve'])


@blueprint_events.route('/<int:event_id>')
def events_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('events/detail.html', event=event)


@blueprint_events.route('/<int:event_id>/approve', methods=['POST'])
@admin_required
def events_approve(event_id):
    event = Event.query.get_or_404(event_id)
    if event.approved:
        flash("Event %d already approved!" % event_id)
    else:
        event.approved = True
        db.session.commit()
        flash("Event %d approved!" % event_id)
    return redirect(url_for('.events_unapproved'))