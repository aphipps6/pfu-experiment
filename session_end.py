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


class EndSessionHandler(webapp2.RequestHandler):
    def get(self):
        this_session = ndb.Key(urlsafe=self.request.get('session_key')).get()
        this_session.datetime_end = datetime.datetime.now()
        this_session.put()
        step = self.request.get('step')
        participant_key = this_session.key.parent().urlsafe()
        experiment_key = this_session.key.parent().parent().urlsafe()
        url = UserFlowControl().get_next_url(current_step=step, participant_key=participant_key,
                                             experiment_key=experiment_key)
        self.redirect(url)
