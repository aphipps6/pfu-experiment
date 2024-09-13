from jinja_render import jinja_render

from data_classes import *
from generate_data import *
from flow_control import *
import webapp2
import datetime
import os, sys
import jinja2
import webapp2
import urllib
import uuid


class WelcomeScreenHandler(webapp2.RequestHandler):
    def get(self):
        experiment_name = self.request.get('experiment_name', default_value='')
        redirect_message = self.request.get('redirect_message', default_value='')
        email = self.request.get('email', default_value='')

        if experiment_name == '':
            self.response.write(jinja_render('SelectExperiment.html', {'redirect_message': redirect_message}))
            return

        if ExperimentManagement.query(ExperimentManagement.experiment_name == experiment_name).count() == 0:
            self.response.write(jinja_render('SelectExperiment.html', {'message': '*Invalid experiment entered'}))
            return

        experiment_key = ExperimentManagement.query(
            ExperimentManagement.experiment_name == experiment_name).get(keys_only=True).urlsafe()

        if email:
            query = ParticipantInformation.query(ParticipantInformation.participant_id == email,
                                                 ParticipantInformation.active == True,
                                                 ancestor=ndb.Key(urlsafe=experiment_key))
            if query.count() > 0:
                p_key = query.fetch(1, keys_only=True)[0]
            else:
                p_key = self.generate_participant_record(email=email, experiment_key=experiment_key)

            session_id = self.create_session(email, experiment_key)
            self.response.set_cookie('session_id', session_id, httponly=True, secure=True)

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
        self.response.write(jinja_render('Welcome_Screen.html', template_values))

    def generate_participant_record(self, email, experiment_key):
        p_key = ParticipantInformation(parent=ndb.Key(urlsafe=experiment_key),
                                       participant_id=email,
                                       active=True).put()
        return p_key

    def create_session(self, email, experiment_key):
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            email=email,
            experiment_key=ndb.Key(urlsafe=experiment_key),
            active=True
        )
        session.put()
        return session_id