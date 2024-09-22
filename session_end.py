from flask import request, redirect
from flask import session as flask_session
from google.cloud import ndb
import datetime
from data_classes import *
from flow_control import UserFlowControl, flow_control
import logging

def end_session():
    session_id = request.args.get('session_id')
    participant_session_key = flask_session.pop('participant_session_key', None)
    
    session = Session.get_by_id(session_id)
    if not session:
        return redirect('/')  # Redirect to home if session not found

    participant_session = ndb.Key(urlsafe=participant_session_key).get()
    participant_session.datetime_end = datetime.datetime.now()
    participant_session.put()

    # Get the next URL
    url = UserFlowControl().get_next_url(session_id=session_id)

    return redirect(url)
