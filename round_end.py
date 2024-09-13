from google.appengine.ext import ndb
from data_classes import Session, ParticipantInformation, ParticipantMultitaskRound, MultitaskRoundTreatment, SubmittedQuestion
from data_constants import SessionConstants
from flow_control import UserFlowControl
from jinja_render import jinja_render
import datetime
import logging

class EndRoundHandler(webapp2.RequestHandler):
    def get(self):
        round_key = self.request.get('round_key')
        session_id = self.request.get('session_id')
        step = self.request.get('step')
        
        session = Session.get_by_id(session_id)
        if not session:
            self.redirect('/')
            return
        
        
        this_round = ndb.Key(urlsafe=round_key).get()
        if this_round.datetime_end is None:
            this_round.datetime_end = datetime.datetime.now()
        if this_round.datetime_start is None:
            this_round.datetime_start = this_round.datetime_end
        this_round.put()
        
        participant_session_key = this_round.key.parent()
        participant_session = participant_session_key.get()

        is_tour = participant_session.session_treatment_key.get().treatment_type == SessionConstants.tutorial_string

        # set continue link to go to next round if this isn't the last
        if this_round.round_number + 1 == MultitaskRoundTreatment.query(
                ancestor=participant_session.session_treatment_key).count():
            continue_link = f"/end_session/?session_id={session_id}&step={step}"
        else:
            continue_link = f"/round_running/?session_id={session_id}&step={step}"

        list_of_round_results = self.get_list_of_round_results(participant_session_key)
        this_round.earnings = list_of_round_results[-1]['total_payoff']
        this_round.put()
        total_column = self.get_total_column(list_of_round_results)

        template_values = {
            'list_of_round_results': list_of_round_results,
            'total_column': total_column,
            'session_id': session_id,
            'round_number': this_round.round_number + 1,
            'total_num_rounds': MultitaskRoundTreatment.query(ancestor=participant_session.session_treatment_key).count(),
            'continue_link': continue_link
        }

        if is_tour:
            template_name = 'Tour_EndRound.html'
        else:
            template_name = 'End_Round.html'

        self.response.write(jinja_render(template_name, template_values))

    def get_list_of_round_results(self, participant_session_key):
        items = []
        for this_round in ParticipantMultitaskRound.query(ancestor=session_key).order(ParticipantMultitaskRound.round_number).fetch():
            round_treatment = this_round.round_treatment_key.get()
            num_easy, num_easy_correct, num_hard, num_hard_correct = self.get_results(this_round)
            payoff_per_easy = round_treatment.easy_payoff
            payoff_per_hard = round_treatment.hard_payoff
            time_used = this_round.datetime_end - this_round.datetime_start
            time_remaining = round_treatment.time_limit_minutes - (time_used.total_seconds() / 60)
            time_value = round_treatment.time_value
            payoff_easy = payoff_per_easy * num_easy_correct
            payoff_hard = payoff_per_hard * num_hard_correct
            time_payoff = time_remaining * time_value
            this_item = dict(
                payoff_per_easy=round(payoff_per_easy, 2),
                payoff_per_hard=round(payoff_per_hard, 2),
                num_easy=num_easy,
                num_hard=num_hard,
                num_easy_correct=num_easy_correct,
                num_hard_correct=num_hard_correct,
                payoff_easy=round(payoff_easy, 2),
                payoff_hard=round(payoff_hard, 2),
                time_limit=round_treatment.time_limit_minutes,
                time_used=round(time_used.total_seconds() / 60, 2),
                time_remaining=round(time_remaining, 2),
                time_value=round(time_value, 2),
                time_payoff=round(time_payoff, 2),
                round_number=this_round.round_number + 1,
                total_payoff=round(payoff_easy + payoff_hard + time_payoff, 2)
            )
            items.append(this_item)
        return sorted(items, key=lambda k: k['round_number'])

    def get_total_column(self, list_of_round_results):
        total_column = dict(
            num_easy=sum([i["num_easy"] for i in list_of_round_results]),
            num_hard=sum([i["num_hard"] for i in list_of_round_results]),
            num_easy_correct=sum([i["num_easy_correct"] for i in list_of_round_results]),
            num_hard_correct=sum([i["num_hard_correct"] for i in list_of_round_results]),
            payoff_per_easy=round(
                sum([i["payoff_per_easy"] for i in list_of_round_results]) / len(list_of_round_results), 2),
            payoff_per_hard=round(
                sum([i["payoff_per_hard"] for i in list_of_round_results]) / len(list_of_round_results), 2),
            payoff_easy=round(sum([i["payoff_easy"] for i in list_of_round_results]), 2),
            payoff_hard=round(sum([i["payoff_hard"] for i in list_of_round_results]), 2),
            time_used=round(sum([i["time_used"] for i in list_of_round_results]), 2),
            time_remaining=round(sum([i["time_remaining"] for i in list_of_round_results]), 2),
            time_payoff=round(sum([i["time_payoff"] for i in list_of_round_results]), 2),
            total_payoff=round(sum([i["total_payoff"] for i in list_of_round_results]), 2)
        )
        return total_column

    def get_results(self, this_round):
        submitted_questions = SubmittedQuestion.query(ancestor=this_round.key).fetch()
        num_easy = 0
        num_easy_correct = 0
        num_hard = 0
        num_hard_correct = 0
        for submitted_question in submitted_questions:
            question = submitted_question.question_key.get()
            correct = submitted_question.submitted_answer == question.answer
            if question.difficulty == "easy":
                num_easy += 1
                if correct: num_easy_correct += 1
            else:
                num_hard += 1
                if correct: num_hard_correct += 1
        return num_easy, num_easy_correct, num_hard, num_hard_correct
