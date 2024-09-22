import hashlib
from jinja_render import jinja_render
from flask import render_template, request, make_response, redirect, url_for, Blueprint
from flask import session as flask_session
from data_classes import ExperimentManagement, ParticipantInformation, Session, client
from google.cloud import ndb
from flow_control import UserFlowControl
import uuid
from contextlib import contextmanager
import logging


session_welcome_bp = Blueprint('session_welcome_bp', __name__)


@session_welcome_bp.route('/session_welcome/')
def session_welcome():
    experiment_name = request.args.get('experiment_name', '')
    redirect_message = request.args.get('redirect_message', '')
    email = request.args.get('email', '')

    if experiment_name == '':
        return jinja_render('SelectExperiment.html', {'redirect_message': redirect_message})

    
    experiment = ExperimentManagement.query(ExperimentManagement.experiment_name == experiment_name).get()
    if not experiment:
        return jinja_render('SelectExperiment.html', {'message': '*Invalid experiment entered'})

    experiment_key = experiment.key

    if email:
        
        query = ParticipantInformation.query(
            ParticipantInformation.participant_id == email,
            ParticipantInformation.active == True,
            ancestor=experiment_key
        )
        participant = query.get()
        if not participant:
            participant = generate_participant_record(email=email, experiment_key=experiment_key)
        
        session_id = create_session(email, experiment_key=experiment_key,experiment_name = experiment_name)
        logging.info(f"Created session with id: {session_id}")
        continue_link = UserFlowControl().get_next_url(session_id=session_id)
    else:
        continue_link = '/'

    template_values = {
        'email': email,
        'experiment_name': experiment_name,
        'step': 0,
        'continue_link': continue_link,
        'redirect_message': redirect_message
    }

    response = make_response(render_template('Welcome_Screen.html', **template_values))
    #if email:
        #response.set_cookie('session_id', session_id, httponly=True, secure=True)
    return response

def generate_participant_record(email, experiment_key):
    logging.info(f"Generating participant record for email: {email}")
    
    participant = ParticipantInformation(
        parent=experiment_key,
        participant_id=email,active=True
        )
    key = participant.put()
    logging.info(f"Generated participant record: {participant}")
    return key

def create_session(email, experiment_key,experiment_name):
    flask_session.clear()
    combined = f"{email}:{experiment_name}"
    session_id = hashlib.sha256(combined.encode()).hexdigest()
    if not isinstance(experiment_key, ndb.Key):
        try:
            experiment_key = ndb.Key(urlsafe=experiment_key)
        except:
            print(f"Error: Invalid experiment key: {experiment_key}")
            return None 
    
    session = Session(
        id=session_id,
        email=email,
        experiment_key=experiment_key,
        active=True,
        current_step=0
    )
    key = session.put()
    created_session = key.get()
    if created_session is None:
        print(f"Error: Session creation failed for id: {session_id}")
        return None
    logging.info(f"Created session: {session}")
    return session_id