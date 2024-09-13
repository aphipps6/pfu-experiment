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
import logging


class InRoundRunningMain(webapp2.RequestHandler):
    def get(self):
        session_id = self.request.get('session_id', default_value='')
        step = self.request.get('step')
        treatment = self.request.get('treatment', default_value='')
        
        if session_id == '':
            message = urllib.urlencode({'redirect_message': 'page: /round_running/. Missing session id'})
            self.redirect("/?" + message)
            return
        
        session = Session.get_by_id(session_id)
        if not session:
            self.redirect('/')
            return
        
        experiment = session.experiment_key.get()
        participant = ParticipantInformation.query(
            ParticipantInformation.participant_id == session.email,
            ancestor=session.experiment_key
        ).get()
        
        # Check if a ParticipantMultitaskSession already exists for this treatment
        participant_session = ParticipantMultitaskSession.query(
            ancestor=participant.key
        ).filter(
            ParticipantMultitaskSession.treatment_group == treatment
        ).get()
        
        if not participant_session:
            # Create a new ParticipantMultitaskSession if it doesn't exist
            if treatment == UserFlowControl.tutorial_string:
                session_treatment_key = experiment.tutorial_session_id
            elif treatment == UserFlowControl.practice_string:
                session_treatment_key = experiment.practice_session_id
            else:
                session_treatment_key = ndb.Key(urlsafe=participant.treatment_keys[int(treatment)-1]
                
            session_treatment = session_treatment_key.get()
            participant_session = ParticipantMultitaskSession(
                parent=participant.key,
                session_treatment_key=session_treatment_key,
                datetime_start=datetime.datetime.now(),
                treatment_group=session_treatment.treatment_group
            )
            participant_session.put()
       

        # 2 - set up this round and round treatment
        # how many rounds in all? get all treatmentRounds tied to this session treatment
        total_rounds = MultitaskRoundTreatment.query(ancestor=session_treatment_key).count()

        # get round treatment
        round_number = ParticipantMultitaskRound.query(ancestor=participant_session.key).count()
        round_treatment = MultitaskRoundTreatment.query(
            MultitaskRoundTreatment.round_number == round_number,
            ancestor=participant_session.session_treatment_key).get()

        # create round record
        this_round = ParticipantMultitaskRound(
            parent=participant_session.key,
            round_treatment_key=round_treatment.key,
            round_number=round_number
        )
        round_key = this_round.put()
        
        logging.info("made it here")
        
        # set up round
        round_minutes = round_treatment.time_limit_minutes
        round_minutes_string = "%02d" % (round_minutes,)

        on_tour = session_treatment.treatment_type == SessionConstants.tutorial_string
        price_info = None

        if round_treatment.payoff_known:
            price_info = dict(
                hard="$" + '%.2f' % round_treatment.hard_payoff,
                easy="$" + '%.2f' % round_treatment.easy_payoff
            )
        if session_treatment.treatment_type == SessionConstants.random_coefficient_string:
            price_info =dict(
                hard="--",
                easy="--"
            )

        template_values = {
            'round_minutes': int(round_minutes),
            'round_minutes_string': round_minutes_string,
            'round_key': round_key.urlsafe(),
            'session_id': session_id,
            'session_treatment': session_treatment.treatment_type,
            'round_number': round_number + 1,
            'total_rounds': total_rounds,
            'participant': p_key,
            'experiment': experiment_key,
            'step': step,
            'price_info': price_info
        }

        if on_tour:
            template_name = "Tour_Round.html"
        else:
            template_name = "InSession_Running_Main.html"

        self.response.write(jinja_render(template_name, template_values))


class QuestionSubmission(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        submitted_question = ndb.Key(urlsafe=data['submitted_question_key']).get()
        submitted_question.datetime_end = datetime.datetime.now()
        submitted_question.submitted_answer = data['submitted_answer']
        submitted_question.put()
        question = submitted_question.question_key.get()
        self.response.out.write(json.dumps(({'difficulty': question.difficulty})))


class QuestionHandler(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        difficulty = data['question_difficulty']
        round_key = data['round_key']
        session_id = data['session_id']
        
        session = Session.get_by_id(session_id)
        if not session:
            self.response.out.write(json.dumps({'error': 'Invalid session'}))
            return
            
        this_round = ndb.Key(urlsafe=round_key).get()
        
        if data['first_question'] == 1:
            this_round.datetime_start = datetime.datetime.now()
            this_round.put()

        # question_number = self.get_question_number(this_round, difficulty)
        question_number = data['question_number']

        question = self.get_new_question(difficulty=difficulty, this_round=this_round, question_number=question_number)
        if question is None:
            self.response.out.write(json.dumps(({'end_round': True})))
        else:
            submitted_question = SubmittedQuestion(
                parent=ndb.Key(urlsafe=round_key),
                question_key=question.key,
                datetime_start=datetime.datetime.now()
            )
            submitted_question_key = submitted_question.put()
            self.response.out.write(json.dumps({
                'end_round': False,
                'question_text': question.text,
                'submitted_question_key': submitted_question_key.urlsafe()
            }))

    def get_question_number(self, this_round, difficulty):

        # use projection to only grab question_key from submitted questions
        completed_question_keys = [i.question_key for i in SubmittedQuestion.query(ancestor=this_round.key).fetch(
            projection=[SubmittedQuestion.question_key]) if i.question_key is not None]
        if len(completed_question_keys) > 0:
            # return the count; notice that this will be the correct number for the next question
            return Question.query(ndb.AND(Question.difficulty == difficulty,
                                          Question.key.IN(completed_question_keys))).count()
        else:
            return 0

    def get_new_question(self, difficulty, this_round, question_number):

        # need to provide questions in the right order based on how many previous questions of that difficulty
        # have been answered
        if difficulty == "hard":
            list_of_keys = this_round.round_treatment_key.get().question_keys_hard
            if len(list_of_keys) <= question_number:
                return None
            round_question_key = sorted(list_of_keys)[question_number]
        else:
            list_of_keys = this_round.round_treatment_key.get().question_keys_easy
            logging.info(len(list_of_keys))
            logging.info(question_number)
            if len(list_of_keys) <= question_number:
                return None
            round_question_key = sorted(list_of_keys)[question_number]
        question = round_question_key.get()
        return question
