from jinja_render import jinja_render

from google.appengine.api import users
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
        p_key = self.request.get('participant', default_value='')
        experiment_key = self.request.get('experiment', default_value='')
        step = self.request.get('step')

        if p_key == '' or experiment_key == '':
            message = urllib.urlencode({'redirect_message': 'page: /risk_assessment/. Missing participant id or experiment key'})
            self.redirect("/?" + message)

        this_menu = AversionMenu.query(AversionMenu.aversion_menu_name == SessionConstants.standard_aversion_menu_name).fetch(1)[0]
        list_of_lotteries = this_menu.list_of_lotteries
        aversion_menu_name = this_menu.aversion_menu_name
        continue_link = UserFlowControl().get_next_url(current_step=step, participant_key=p_key,
                                                       experiment_key=experiment_key)
        template_values = dict(
            list_of_lotteries=list_of_lotteries,
            aversion_menu_name=aversion_menu_name,
            continue_link=continue_link,
            participant=p_key
        )
        self.response.write(jinja_render('Risk_Assessment.html', template_values))


class EndRiskAssessmentHandler(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        risk_results = data["radio_results"]
        menu_name = data["menu_name"]
        p_key = data["participant"]
        logging.info(risk_results)

        aversion_results = AversionResult(aversion_menu_name=menu_name, list_of_choices=risk_results)
        p_info = ndb.Key(urlsafe=p_key).get()
        p_info.aversion = aversion_results
        p_info.put()

        self.response.out.write(json.dumps(({'success': 'TRUE'})))