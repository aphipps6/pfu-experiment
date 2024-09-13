from jinja_render import jinja_render

from data_classes import *
from generate_data import *
import json
import jinja2
import webapp2
import datetime

import os, sys
import jinja2
import webapp2
import logging
import urllib
from flow_control import *

class RiskAssessmentHandler(webapp2.RequestHandler):
    def get(self):
        session_id = self.request.get('session_id', default_value='')
        step = self.request.get('step')

        if session_id == '':
            message = urllib.urlencode({'redirect_message': 'page: /risk_assessment/. Missing session id'})
            self.redirect("/?" + message)
        
        session = Session.get_by_id(session_id)
        if not session:
            self.redirect('/')
            return
        
        this_menu = AversionMenu.query(AversionMenu.aversion_menu_name == SessionConstants.standard_aversion_menu_name).fetch(1)[0]
        list_of_lotteries = this_menu.list_of_lotteries
        aversion_menu_name = this_menu.aversion_menu_name
        continue_link = UserFlowControl().get_next_url(session_id=session_id)
        template_values = dict(
            list_of_lotteries=list_of_lotteries,
            aversion_menu_name=aversion_menu_name,
            continue_link=continue_link,
            session_id=session_id
        )
        self.response.write(jinja_render('Risk_Assessment.html', template_values))


class EndRiskAssessmentHandler(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        risk_results = data["radio_results"]
        menu_name = data["menu_name"]
        session_id = data["session_id"]
        
        session = Session.get_by_id(session_id)
        if not session:
            self.response.out.write(json.dumps({'success': 'FALSE', 'error': 'Invalid session'}))
            return
        
        aversion_results = AversionResult(aversion_menu_name=menu_name, list_of_choices=risk_results)
        
        participant = ParticipantInformation.query(
            ParticipantInformation.participant_id == session.email,
            ancestor=session.experiment_key
        ).get()
        
        if not participant:
            self.response.out.write(json.dumps({'success': 'FALSE', 'error': 'Participant not found'}))
            return

        participant.aversion = aversion_results
        participant.put()

        logging.info(f"Risk assessment completed for session {session_id}, participant {session.email}")
        self.response.out.write(json.dumps({'success': 'TRUE'}))