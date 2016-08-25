import json

from flask import abort, Blueprint, redirect, render_template, url_for, flash
from flask_login import current_user, login_required

from forms import EventForm
from models import db, Event
from util import admin_required, isoformat

blueprint = Blueprint('events', __name__, template_folder='templates')


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def events_create():
    event_create_form = EventForm()
    if event_create_form.validate_on_submit():
        new_event = Event(owner=current_user)
        event_create_form.populate_obj(new_event)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('.events_owned'))
    return render_template('events/create.html', event_create_form=event_create_form)


@blueprint.route('/list/json')
def events_list_json():
    events = Event.query.filter_by().order_by(Event.start_time.desc()).all()
    event_list = []
    for event in events:
        start_time = event.start_time
        obj = {
            'id': event.id,
            'approved': event.approved,
            'name': event.title,
            'startTime': start_time * 1000,
            'startTimeFormat': isoformat(start_time),
            'endTime': (start_time + event.duration * 60 * 60) * 1000,
            'duration': event.duration
        }
        event_list.append(obj)
    return json.dumps(event_list)


@blueprint.route('/')
@blueprint.route('/all')
def events_all():
    events = Event.query.filter_by(approved=True, removed=False).order_by(Event.start_time.desc()).all()
    for event in events:
        event.start_time_format = isoformat(event.start_time)
    return render_template('events/list.html', tab='all', events=events)


# todo
@blueprint.route('/upcoming')
def events_upcoming():
    events = Event.query.filter_by(approved=True, removed=False).order_by(Event.start_time.desc()).all()
    for event in events:
        event.start_time_format = isoformat(event.start_time)
    return render_template('events/list.html', tab='upcoming', events=events)


# todo
@blueprint.route('/past')
def events_past():
    events = Event.query.filter_by(approved=True, removed=False).order_by(Event.start_time.desc()).all()
    for event in events:
        event.start_time_format = isoformat(event.start_time)
    return render_template('events/list.html', tab='past', events=events)


@blueprint.route('/unapproved')
@admin_required
def events_unapproved():
    unapproved_events = Event.query.filter_by(approved=False, removed=False).order_by(Event.start_time.desc()).all()
    for event in unapproved_events:
        event.start_time_format = isoformat(event.start_time)
    return render_template('events/list.html', tab='unapproved', events=unapproved_events, enabled_actions=['approve'])


@blueprint.route('/owned')
@login_required
def events_owned():
    owned_events = current_user.events.filter_by(removed=False)
    for event in owned_events:
        event.start_time_format = isoformat(event.start_time)
    return render_template('events/list.html', tab='owned', events=owned_events, enabled_actions=['manage', 'remove'])


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
