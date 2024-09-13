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


class GenerateSessionHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'questions_in_database': Question.query().count(),
            'default_question_class': 'add_hn4d2_en8d1'
        }

        self.response.write(jinja_render('Generate_Sessions.html', template_values))

    def post(self):
        action = self.request.get('action', default_value='generate_questions')
        if action == 'generate_questions':
            question_class = self.request.get('question_class_to_generate')
            number_of_questions_to_generate = int(self.request.get('number_of_questions_to_generate'))
            question_difficulty = self.request.get('question_difficulty')
            for n in range(number_of_questions_to_generate):
                if question_difficulty == 'both':
                    generate_new_question(question_class, 'hard')
                    generate_new_question(question_class, 'easy')
                else:
                    generate_new_question(question_class, question_difficulty)

        elif action == 'generate_session':
            number_of_questions_per_round = int(self.request.get('number_of_questions_per_treatment'))
            number_of_rounds = int(self.request.get('number_of_rounds'))
            treatment_type = self.request.get('treatment_type')
            session_group = self.request.get('group_id')
            time_limit_minutes = int(self.request.get('time_limit_minutes'))
            session_question_class = self.request.get('session_question_class')
            generate_control = self.request.get('generate_control') == 'yes'
            generate_tour = self.request.get('generate_tour') == 'yes'
            control_type = self.request.get('control_type')
            treatment_session_key = generate_session_treatment(treatment_type=treatment_type,
                                                               treatment_group=session_group,
                                                               number_of_questions=number_of_questions_per_round,
                                                               number_of_rounds=number_of_rounds,
                                                               time_limit_minutes=time_limit_minutes,
                                                               question_class=session_question_class)
            if generate_control:
                control_session_key = generate_matching_control_session_treatment(
                    matching_session_treatment_key=treatment_session_key, treatment_type=control_type, payoff_known=True
                )
            if generate_tour:
                generate_matching_tour_session(matching_session_treatment_key=treatment_session_key)
