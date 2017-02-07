from jinja_render import jinja_render
from data_constants import *

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
import urllib
from administrator import *


class SurveyHandler(webapp2.RequestHandler):
    def get(self):
        step = self.request.get('step')
        experiment = self.request.get('experiment')
        participant = self.request.get('participant')
        template_values = dict(
            continue_link=UserFlowControl().get_next_url(current_step=step, experiment_key=experiment, participant_key=participant),
            participant=participant,
            survey_price="$" + '%.2f' % AdminConstants.survey_fee
        )
        self.response.write(jinja_render('Survey.html', template_values))

class SurveyEndHandler(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        survey_results = data['results']
        participant = ndb.Key(urlsafe=data['participant']).get()

        survey_response = SurveyResponse(survey_name='pilot', list_of_responses=survey_results)
        participant.survey_result = survey_response
        participant.put()
        self.response.out.write(json.dumps(({'success': 'TRUE'})))