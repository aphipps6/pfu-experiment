from flask import request, redirect
from flask import session as flask_session
from google.cloud import ndb
import datetime
from data_classes import *
from flow_control import UserFlowControl, flow_control
import logging

def end_session():
    session_id = request.args.get('session_id')
    session = Session.get_by_id(session_id)
    if not session:
        return redirect('/')  # Redirect to home if session not found


    logging.info(f"Ending session for session_id: {session_id}")
    participant_session_key = flask_session.pop('participant_session_key', None)
    if participant_session_key:
        participant_session = ndb.Key(urlsafe=participant_session_key).get()
        participant_session.datetime_end = datetime.datetime.now()
        participant_session.put()
        logging.info(f"SESSION FOUND AND SAVED: {session_id}")
    else:
        logging.info(f"COULD NOT FIND SESSION TO SAVE INFO {session_id}")
        # now, if they hit refresh, there will be no active participant session key in the flow_session
        # and the redirect url will be set correctly
    
  

    # Get the next URL
    url = UserFlowControl().get_next_url(session_id=session_id, increment=False)
    return redirect(url)
