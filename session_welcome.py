from jinja_render import jinja_render

from google.appengine.api import users
from data_classes import *
from generate_data import *
from flow_control import *
import json
import jinja2
import webapp2
import datetime

import os, sys
import jinja2
import webapp2


class WelcomeScreenHandler(webapp2.RequestHandler):
    def get(self):
        experiment_name = self.request.get('experiment_name', default_value='')
        redirect_message = self.request.get('redirect_message', default_value='')
        if experiment_name == '':
            self.response.write(jinja_render('SelectExperiment.html', {'redirect_message': redirect_message}))
        else:
            # check that experiment entered is valid
            if ExperimentManagement.query(ExperimentManagement.experiment_name == experiment_name).count() > 0:
                experiment_key = ExperimentManagement.query(
                    ExperimentManagement.experiment_name == experiment_name).get(keys_only=True).urlsafe()
                user = users.get_current_user()
                if user:
                    url = users.create_logout_url(self.request.uri)
                    url_linktext = 'Logout'
                    query = ParticipantInformation.query(ParticipantInformation.participant_id == user.email(),
                                                         ParticipantInformation.active == True)
                    if query.count() > 0:

                        p_key = query.fetch(1, keys_only=True)[0]
                    else:
                        p_key = self.generate_participant_record(user=user, experiment_key=experiment_key)
                    continue_link = UserFlowControl().get_next_url(current_step=0, participant_key=p_key.urlsafe(),
                                                                   experiment_key=experiment_key)
                else:
                    url = users.create_login_url(self.request.uri)
                    url_linktext = 'Login'
                    continue_link = '/'
                template_values = {
                    'user': user,
                    'url': url,
                    'url_linktext': url_linktext,
                    'experiment_name': experiment_name,
                    'step': 0,
                    'continue_link': continue_link,
                    'redirect_message': redirect_message
                }
                self.response.write(jinja_render('Welcome_Screen.html', template_values))
            else:
                self.response.write(jinja_render('SelectExperiment.html', {'message': '*Invalid experiment entered'}))

    def generate_participant_record(self, user, experiment_key):
        p_key = ParticipantInformation(parent=ndb.Key(urlsafe=experiment_key),
                                       participant_id=user.email(),
                                       active=True
                                       ).put()
        return p_key
