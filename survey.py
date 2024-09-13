from jinja_render import jinja_render
from data_constants import *

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
        session_id = self.request.get('session_id')
        step = self.request.get('step')
        
        session = Session.get_by_id(session_id)
        if not session:
            self.redirect('/')
            return
        
        template_values = dict(
            continue_link=UserFlowControl().get_next_url(session_id=session_id),
            session_id=session_id,
            survey_price="$" + '%.2f' % AdminConstants.survey_fee
        )
        self.response.write(jinja_render('Survey.html', template_values))

class SurveyEndHandler(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        survey_results = data['results']
        session_id = data['session_id']
        
        session = Session.get_by_id(session_id)
        if not session:
            self.response.out.write(json.dumps({'success': 'FALSE', 'error': 'Invalid session'}))
            return
        
        
        participant = ParticipantInformation.query(ParticipantInformation.participant_id == session.email,
                                                   ancestor=session.experiment_key).get()

        survey_response = SurveyResponse(survey_name='pilot', list_of_responses=survey_results)
        participant.survey_result = survey_response
        participant.put()
        self.response.out.write(json.dumps(({'success': 'TRUE'})))