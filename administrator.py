import math
import numpy


from jinja_render import jinja_render

from google.appengine.api import users
from google.appengine.ext import ndb

from data_classes import *
from generate_data import *
from data_constants import *
from flow_control import *
from admin_constants import *
from helper_functions import *
import json
import jinja2
import webapp2
import datetime

import os, sys
import jinja2
import webapp2
import logging
import csv


class AdminHomepageHandler(webapp2.RequestHandler):
    def get(self):
        experiment = self.request.get('experiment', default_value='')
        list_of_participants = []
        if experiment != '':
            list_of_participants = self.get_list_of_participants(experiment)
        template_values = dict(
            experiment=experiment,
            list_of_instructions=AdminFunctions().get_prompts(),
            list_of_participants=list_of_participants
        )
        self.response.write(jinja_render('Admin_Dashboard.html', template_values=template_values))

    def get_list_of_participants(self, experiment_key_urlsafe):
        participants = ParticipantInformation.query(ancestor=ndb.Key(urlsafe=experiment_key_urlsafe)).fetch()
        list_of_participants = []
        for p in participants:
            risk_status = ''
            if p.aversion is not None:
                risk_status = "Completed"

            tutorial_status = ''
            practice_status = ''
            t1 = dict(round='', total='')
            t2 = dict(round='', total='')
            survey_status = ''

            p_rounds = ParticipantMultitaskRound.query(ancestor=p.key).fetch()
            p_sessions = ParticipantMultitaskSession.query(ancestor=p.key).fetch()

            session_treatments = [i.session_treatment_key.get() for i in p_sessions]

            if SessionConstants.tutorial_string in [i.treatment_type for i in session_treatments]:
                t_session = [i for i in p_sessions if i.session_treatment_key == [j.key for j in session_treatments if
                                                                                  j.treatment_type == SessionConstants.tutorial_string][
                    0]][0]
                if t_session.datetime_end is not None:
                    tutorial_status = 'Completed'
                else:
                    tutorial_status = 'Started'

            if SessionConstants.practice_string in [i.treatment_type for i in session_treatments]:
                practice_session = [i for i in p_sessions if i.session_treatment_key ==
                                    [j.key for j in session_treatments if
                                     j.treatment_type == SessionConstants.practice_string][0]][0]
                if practice_session.datetime_end is not None:
                    practice_status = 'Completed'
                else:
                    practice_status = 'Started'

            treatment_sessions = [i for i in session_treatments if
                                  i.treatment_type not in [SessionConstants.practice_string,
                                                           SessionConstants.tutorial_string]]

            p_treatment_sessions = [i for i in p_sessions if
                                    i.session_treatment_key in [j.key for j in treatment_sessions]]

            if len([i.datetime_start for i in p_treatment_sessions if i.datetime_start is not None]) == 1:
                t1_treatment_round_keys = MultitaskRoundTreatment.query(ancestor=treatment_sessions[0].key).fetch(
                    keys_only=True)
                t1_rounds = [r for r in p_rounds if r.round_treatment_key in t1_treatment_round_keys]
                n_rounds = len([i for i in t1_rounds if i.datetime_end is not None])
                total_rounds = len(t1_treatment_round_keys)
                t1 = dict(rounds=n_rounds, total=total_rounds)

            elif len([i.datetime_start for i in p_treatment_sessions if i.datetime_start is not None]) > 1:
                treatment_sessions.sort(
                    key=lambda x: [i.datetime_start for i in p_sessions if x.key == i.session_treatment_key][0])
                t1_treatment_round_keys = MultitaskRoundTreatment.query(ancestor=treatment_sessions[0].key).fetch(
                    keys_only=True)
                t1_rounds = [r for r in p_rounds if r.round_treatment_key in t1_treatment_round_keys]
                n_rounds = len([i for i in t1_rounds if i.datetime_end is not None])
                total_rounds = len(t1_treatment_round_keys)
                t1 = dict(rounds=n_rounds, total=total_rounds)

                t2_treatment_round_keys = MultitaskRoundTreatment.query(ancestor=treatment_sessions[1].key).fetch(
                    keys_only=True)
                t2_rounds = [r for r in p_rounds if r.round_treatment_key in t2_treatment_round_keys]
                n_rounds = len([i for i in t2_rounds if i.datetime_end is not None])
                total_rounds = len(t2_treatment_round_keys)
                t2 = dict(rounds=n_rounds, total=total_rounds)

            if p.survey_result is not None:
                survey_status = "Completed"

            list_of_participants.append(dict(
                name=p.participant_id,
                risk_status=risk_status,
                tutorial_status=tutorial_status,
                practice_status=practice_status,
                t1=t1,
                t2=t2,
                survey_status=survey_status
            ))

        return list_of_participants


class EnableRiskAssessmentHandler(webapp2.RequestHandler):
    def get(self):
        e_key = self.request.get('experiment')
        experiment = ndb.Key(urlsafe=e_key).get()
        experiment.risk_assessment_enabled = True
        experiment.put()
        self.redirect('/admin/?experiment=' + e_key)


class GenerateExperimentHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get('experiment_name')
        experiment_key = AdminFunctions().generate_experiment(name).urlsafe()
        self.redirect('/admin/?experiment=' + experiment_key)


class GetExperimentHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get('experiment_name')
        experiment_key = \
            ExperimentManagement.query(ExperimentManagement.experiment_name == name).fetch(1, keys_only=True)[0]
        self.redirect('/admin/?experiment=' + experiment_key.urlsafe())


class ResetExperimentHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get('experiment_name')
        experiment = ExperimentManagement.query(ExperimentManagement.experiment_name == name).fetch(1)[0]
        experiment.risk_assessment_enabled = False
        experiment.tutorial_enabled = False
        experiment.practice_enabled = False
        experiment.session_enabled = False
        experiment.survey_enabled = False
        experiment.summary_enabled = False
        experiment.put()
        self.redirect('/admin/?experiment=' + experiment.key.urlsafe())


class GetEarningsHandler(webapp2.RequestHandler):
    def get(self):
        experiment_name = self.request.get('experiment_name')
        experiment = ExperimentManagement.query(ExperimentManagement.experiment_name == experiment_name).fetch(1)[0]
        list_of_earnings = []
        list_of_participants = ParticipantInformation.query(ancestor=experiment.key).fetch()
        for p in list_of_participants:
            this_list_of_earnings = [
                ['Participation', AdminConstants.participation_fee],
                ['Lottery Winnings', AdminFunctions().get_lottery_winnings(participant=p)],
                ['Fixed Wage Round', AdminConstants.practice_fee],
                ['Session 1', AdminFunctions().get_session_earnings(participant=p, session_index=0)],
                ['Session 2', AdminFunctions().get_session_earnings(participant=p, session_index=1)]
            ]
            list_of_earnings.append([p.participant_id, sum([i[1] for i in this_list_of_earnings])])

        template_values = dict(
            list_of_earnings=list_of_earnings,
            experiment_name=experiment_name
        )
        self.response.write(jinja_render('Admin_DisplayEarnings.html', template_values=template_values))


class ListParticipantsHandler(webapp2.RequestHandler):
    def get(self):
        e_key = self.request.get('experiment')
        experiment_key = ndb.Key(urlsafe=e_key)
        list_of_participants = ParticipantInformation.query(ancestor=experiment_key).fetch()
        template_values = dict(
            list_of_participants=[p.participant_id for p in list_of_participants]
        )
        self.response.write(jinja_render('Admin_DisplayParticipants.html', template_values=template_values))


class EnableTutorialHandler(webapp2.RequestHandler):
    def get(self):
        e_key = self.request.get('experiment')
        experiment = ndb.Key(urlsafe=e_key).get()
        experiment.tutorial_enabled = True
        experiment.put()
        self.redirect('/admin/?experiment=' + e_key)


class EnablePracticeHandler(webapp2.RequestHandler):
    def get(self):
        e_key = self.request.get('experiment')
        experiment = ndb.Key(urlsafe=e_key).get()
        experiment.practice_enabled = True
        experiment.put()
        self.redirect('/admin/?experiment=' + e_key)


class EnableSessionHandler(webapp2.RequestHandler):
    def get(self):
        e_key = self.request.get('experiment')
        experiment = ndb.Key(urlsafe=e_key).get()
        experiment.session_enabled = True
        experiment.put()
        self.redirect('/admin/?experiment=' + e_key)


class EnableSurveyHandler(webapp2.RequestHandler):
    def get(self):
        e_key = self.request.get('experiment')
        experiment = ndb.Key(urlsafe=e_key).get()
        experiment.survey_enabled = True
        experiment.put()

        AdminFunctions().run_lottery(experiment)

        self.redirect('/admin/?experiment=' + e_key)


class EnableSummaryHandler(webapp2.RequestHandler):
    def get(self):
        e_key = self.request.get('experiment')
        experiment = ndb.Key(urlsafe=e_key).get()
        experiment.summary_enabled = True
        experiment.put()
        self.redirect('/admin/?experiment=' + e_key)


class RandomizeTreatmentHandler(webapp2.RequestHandler):
    def get(self):
        experiment = self.request.get('experiment')
        AdminFunctions().randomize_participants(experiment_key=experiment)
        self.redirect('/admin/?experiment=' + experiment)


class AdminPromptsHandler(webapp2.RequestHandler):
    def get(self):
        list_of_instructions = AdminFunctions().get_prompts()
        self.response.out.write(json.dumps(list_of_instructions))


class AdminDataDownloadHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/csv'
        self.response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
        writer = csv.writer(self.response.out)
        experiment_name = self.request.get("experiment_name", default_value='')
        if experiment_name == '':
            raise ValueError("No experiment name provided")
        experiment = ExperimentManagement.query(ExperimentManagement.experiment_name == experiment_name).fetch()[0]
        data = AdminFunctions.generate_multitask_csv(experiment=experiment)
        writer.writerows(data)


class AdminAversionDownloadHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/csv'
        self.response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
        writer = csv.writer(self.response.out)
        experiment_name = self.request.get("experiment_name", default_value='')
        if experiment_name == '':
            raise ValueError("No experiment name provided")
        experiment = ExperimentManagement.query(ExperimentManagement.experiment_name == experiment_name).fetch()[0]
        data = AdminFunctions.generate_aversion_csv(experiment=experiment)
        writer.writerows(data)


class GenerateFakeParticipantsHandler(webapp2.RequestHandler):
    def get(self):
        experiment = self.request.get('experiment', default_value='')
        if experiment == '':
            return
        HelperFunctions.generate_fake_users(number_of_users=5, experiment_key_urlsafe=experiment)


class AdminFunctions:
    @staticmethod
    def generate_aversion_csv(experiment):
        data = []
        lotteries = ['L01', 'L02', 'L03', 'L04', 'L05', 'L06', 'L07', 'L08', 'L09', 'L10']
        participants = ParticipantInformation.query(ancestor=experiment.key).fetch()
        for p in participants:
            email = p.participant_id
            results = AdminFunctions.get_aversion_list(p, lotteries)
            data.append([email] + results)
        header = ['email'] + lotteries
        return [header] + data

    @staticmethod
    def get_aversion_list(participant, lotteries):
        chosen_lotteries = participant.aversion.list_of_choices
        choice_dict = {i[:3]: i[3] for i in chosen_lotteries}
        results = []
        for lot in lotteries:
            if choice_dict[lot]:
                results.append(choice_dict[lot])
            else:
                results.append(None)
        return results

    @staticmethod
    def get_aversion_switch(participant, lotteries):
        results = AdminFunctions.get_aversion_list(participant, lotteries)
        switch_point = None
        if "B" in results:
            switch_point = results.index("B") + 1
        return switch_point

    @staticmethod
    def generate_multitask_csv(experiment):
        data = []
        participants = ParticipantInformation.query(ancestor=experiment.key).fetch()
        for p in participants:
            lotteries = ['L01', 'L02', 'L03', 'L04', 'L05', 'L06', 'L07', 'L08', 'L09', 'L10']
            aversion_switch = AdminFunctions.get_aversion_switch(p, lotteries)
            email = p.participant_id
            sessions = ParticipantMultitaskSession.query(ancestor=p.key).fetch()
            all_treatment_keys = [ndb.Key(urlsafe=i) for i in p.treatment_keys]
            logging.info(all_treatment_keys)

            for s in sessions:
                session_treatment_key = s.session_treatment_key
                session_treatment = session_treatment_key.get()
                treatment_name = session_treatment.treatment_type
                if treatment_name == SessionConstants.random_coefficient_string:
                    hard_dist = session_treatment.hard_payoff_distribution
                    easy_dist = session_treatment.easy_payoff_distribution
                    hard_mean = hard_dist['mean']
                    easy_mean = easy_dist['mean']
                    ahard = hard_dist['a']
                    bhard = hard_dist['b']
                    aeasy = easy_dist['a']
                    beasy = easy_dist['b']
                else:
                    hard_mean = None
                    easy_mean = None
                    ahard = None
                    aeasy = None
                    bhard = None
                    beasy = None
                if treatment_name in [SessionConstants.practice_string, SessionConstants.tutorial_string]:
                    session_number = None
                else:
                    session_number = all_treatment_keys.index(session_treatment_key)
                rounds = ParticipantMultitaskRound.query(ancestor=s.key)
                for r in rounds:
                    r_treatment = r.round_treatment_key.get()
                    r_number = r.round_number
                    n_correct_hard = 0
                    n_correct_easy = 0
                    list_of_times_hard = []
                    list_of_times_correct_hard = []
                    list_of_times_easy = []
                    list_of_times_correct_easy = []
                    questions = SubmittedQuestion.query(ancestor=r.key)
                    n_attempt_hard = 0
                    n_attempt_easy = 0
                    for q in questions:
                        original = q.question_key.get()
                        if original.difficulty == "hard":
                            n_attempt_hard += 1
                            if q.datetime_end and q.datetime_start:
                                list_of_times_hard.append(q.datetime_end - q.datetime_start)
                            if q.submitted_answer == original.answer:
                                n_correct_hard += 1
                                list_of_times_correct_hard.append(q.datetime_end - q.datetime_start)
                        else:
                            n_attempt_easy += 1
                            if q.datetime_end and q.datetime_start:
                                list_of_times_easy.append(q.datetime_end - q.datetime_start)
                            if q.submitted_answer == original.answer:
                                n_correct_easy += 1
                                list_of_times_correct_easy.append(q.datetime_end - q.datetime_start)
                    if treatment_name == SessionConstants.random_coefficient_string:
                        production_value = n_correct_hard * hard_mean + n_correct_easy * easy_mean
                    elif treatment_name == SessionConstants.constant_coefficient_string:
                        production_value = n_correct_easy * r_treatment.easy_payoff + n_correct_hard * r_treatment.hard_payoff
                    elif treatment_name == SessionConstants.practice_string:
                        production_value = n_correct_hard * AdminConstants.constant_coefficients_hard + n_correct_easy * AdminConstants.constant_coefficients_easy
                    else:
                        production_value = None
                    data.append(
                        [email, session_number, treatment_name, r_number,
                         n_attempt_hard,
                         n_correct_hard,
                         HelperFunctions.mean_time(list_of_times_hard),
                         HelperFunctions.mean_time(list_of_times_correct_hard),
                         n_attempt_easy,
                         n_correct_easy,
                         HelperFunctions.mean_time(list_of_times_easy),
                         HelperFunctions.mean_time(list_of_times_correct_easy),
                         r_treatment.time_limit_minutes,
                         (r.datetime_end - r.datetime_start).total_seconds(),
                         r_treatment.easy_payoff,
                         r_treatment.hard_payoff,
                         session_treatment.hard_high_variance,
                         hard_mean, ahard, bhard, easy_mean, aeasy, beasy,
                         production_value,
                         aversion_switch
                         ])
        header = ["email", "session_number", "treatment_name", "round_number", "n_attempt_hard", "n_correct_hard",
                  "avg_time_hard", "avg_time_correct_hard", "n_attempt_easy", "n_correct_easy", "avg_time_easy",
                  "avg_time_correct_easy", "time_limit", "round_time", "easy_payoff", "hard_payoff", "hard_high_var",
                  "hard_payoff_mean", "hard_a", "hard_b", "easy_payoff_mean", "easy_a", "easy_b", "production_value",
                  "aversion_switch"]
        return [header] + data

    
    def calculate_price_per_question(self, questions_per_minute, n_rounds, minutes_per_round,
                                     expected_session_earnings):
        return expected_session_earnings / (questions_per_minute * n_rounds * minutes_per_round)

    
    def calculate_price_per_minute(self, total_time_value_of_session, n_rounds, minutes_per_round):
        return total_time_value_of_session / (n_rounds * minutes_per_round)

    @staticmethod
    def get_session_earnings(participant, session_index):
        if participant.treatment_keys is None:
            return 0
        session_treatment_key = ndb.Key(urlsafe=participant.treatment_keys[session_index])
        list_of_round_treatment_keys = MultitaskRoundTreatment.query(ancestor=session_treatment_key).fetch(
            keys_only=True)
        
        # find the participantMultitaskSession for this treatment
        participant_session = ParticipantMultitaskSession.query(
            ParticipantMultitaskSession.session_treatment_key == session_treatment_key,
            ancestor=participant.key
        ).get()
        
        if not participant_session:
            return 0
        
        list_of_earnings = ParticipantMultitaskRound.query(
            ParticipantMultitaskRound.round_treatment_key.IN(list_of_round_treatment_keys),
            ancestor=participant_session.key
        ).fetch(projection=[ParticipantMultitaskRound.earnings])
        
        total_earnings = sum([i.earnings for i in list_of_earnings if i.earnings is not None])
        return total_earnings

    def get_prompts(self):
        url_dict = UserFlowControl().get_next_url(participant_key="", experiment_key="", current_step=0, pause=False,
                                                  return_dict=True)
        instruction_names = [v['name'] for k, v in url_dict.iteritems()]

        list_of_instructions = [[i, UserFlowControl().get_instructions(name=i, participant_key="", proctor=True)] for i
                                in instruction_names]

        return list_of_instructions

    def run_lottery(self, experiment):
        aversion_menu = AversionMenu.query(AversionMenu.aversion_menu_name == experiment.aversion_menu_name).fetch(1)[0]
        list_of_lotteries = aversion_menu.list_of_lotteries
        experiment.lottery_played = list_of_lotteries[random.randint(0, len(list_of_lotteries) - 1)]
        experiment.lottery_result = random.randint(1, len(list_of_lotteries))
        experiment.put()

    @staticmethod
    def get_lottery_winnings(participant):
        experiment = participant.key.parent().get()
        lottery_played = experiment.lottery_played
        lottery_result = experiment.lottery_result
        if participant.aversion is None:
            return 0
        list_of_choices = participant.aversion.list_of_choices

        aprops = lottery_played['a_props']
        bprops = lottery_played['b_props']

        prob_a = aprops['probability']
        prob_b = bprops['probability']

        p1_a = aprops['p1']
        p2_a = aprops['p2']
        p1_b = bprops['p1']
        p2_b = bprops['p2']

        lname = lottery_played['name']
        possible_choices = [lname + 'A', lname + 'B']
        user_selected = bool(set(list_of_choices) & set(possible_choices))

        if not user_selected:
            winnings = 0
        else:
            chosen_lottery = [i for i in list_of_choices if i in possible_choices][0]
            if chosen_lottery[-1] == 'A':
                if prob_a >= lottery_result:
                    winnings = p1_a
                else:
                    winnings = p2_a
            else:
                if prob_b >= lottery_result:
                    winnings = p1_b
                else:
                    winnings = p2_b
        return winnings

    @staticmethod
    def randomize_participants(experiment_key):
        experiment = ndb.Key(urlsafe=experiment_key).get()
        dict_of_session_treatments = experiment.treatment_session_id_list
        list_of_participants = ParticipantInformation.query(ancestor=ndb.Key(urlsafe=experiment_key)).fetch()
        list_of_rc_treatments = dict_of_session_treatments[SessionConstants.random_coefficient_string]
        list_of_cc_treatments = dict_of_session_treatments[SessionConstants.constant_coefficient_string]

        if len(list_of_rc_treatments) > 2:
            raise ValueError("Cannot have more than 2 sub-treatments")

        if len(list_of_cc_treatments) > 1:
            raise ValueError("Cannot have more than 1 constant coefficients round")

        # define possible treatment assignments
        cc = list_of_cc_treatments[0]
        rc_1 = list_of_rc_treatments[0]
        rc_2 = list_of_rc_treatments[1]
        treatment_combos = [[cc, rc_1], [cc, rc_2], [rc_1, cc], [rc_2, cc]]

        # shuffle order of possible treatment assignments. This way, if we frequently have odd number
        # of participants, the last treatment assignment won't be under-represented
        random.shuffle(treatment_combos)
        random.shuffle(list_of_participants)

        split_list_of_participants = numpy.array_split(list_of_participants, len(treatment_combos))
        q = 0
        for g in split_list_of_participants:
            for p in g:
                p.treatment_keys = treatment_combos[q]
                p.put()
            q += 1

    @staticmethod
    def generate_experiment(self, name):
        # treatment_group = "pilot_102816"
        treatment_group = name
        query = ExperimentManagement.query(ExperimentManagement.experiment_name == treatment_group)
        if query.count() > 0:
            return query.fetch(1, keys_only=True)[0]

        hard_n = 6
        hard_digits = 2
        easy_n = 3
        easy_digits = 2
        question_class_name = "add_hn06d2_en03d2"
        questions_per_round = 30
        number_of_rounds = 8
        time_limit_minutes = 3
        time_value = AdminConstants.time_value

        practice_time_limit = 2
        practice_n_rounds = 3

        generate_new_rc_rounds = True

        a = 0.08
        b = 0.18
        sigma_squared = math.pow(1 / 12 * (b - a), 2)
        m = (b + a) / 2
        hard_payoff_distribution_high_variance = dict(name='uniform', a=a, b=b, sigma_squared=sigma_squared, mean=m)
        hard_payoff_generating_function_high_variance = lambda: random.uniform(0.08, 0.18)

        logging.info("*************************************************************")
        logging.info(a)
        logging.info(b)
        logging.info(hard_payoff_distribution_high_variance)
        logging.info(m)

        a = 0.11
        b = 0.15
        sigma_squared = math.pow(1 / 12 * (b - a), 2)
        m = (b + a) / 2
        hard_payoff_distribution_low_variance = dict(name='uniform', a=a, b=b, sigma_squared=sigma_squared, mean=m)
        hard_payoff_generating_function_low_variance = lambda: random.uniform(0.11, 0.15)

        logging.info("*************************************************************")
        logging.info(a)
        logging.info(b)
        logging.info(hard_payoff_distribution_low_variance)

        a = 0.01
        b = 0.11
        sigma_squared = math.pow(1 / 12 * (b - a), 2)
        m = (b + a) / 2
        easy_payoff_distribution_high_variance = dict(name='uniform', a=a, b=b, sigma_squared=sigma_squared, mean=m)
        easy_payoff_generating_function_high_varaince = lambda: random.uniform(0.01, 0.11)

        logging.info("*************************************************************")
        logging.info(a)
        logging.info(b)
        logging.info(easy_payoff_distribution_high_variance)

        a = 0.04
        b = 0.08
        sigma_squared = math.pow(1 / 12 * (b - a), 2)
        m = (b + a) / 2
        easy_payoff_distribution_low_variance = dict(name='uniform', a=a, b=b, sigma_squared=sigma_squared, mean=m)
        easy_payoff_generating_function_low_varaince = lambda: random.uniform(0.04, 0.08)

        logging.info("*************************************************************")
        logging.info(a)
        logging.info(b)
        logging.info(easy_payoff_distribution_low_variance)

        constant_hard_payoff = lambda: hard_payoff_distribution_low_variance['mean']
        constant_easy_payoff = lambda: easy_payoff_distribution_low_variance['mean']
        tutorial_hard_payoff = lambda: 0
        tutorial_easy_payoff = lambda: 0

        # Check for question class by name. If doesn't exist, create
        class_query = QuestionClass.query(QuestionClass.type_name == question_class_name)
        if class_query.count() == 0:
            question_class = QuestionClass(type_name=question_class_name,
                                           class_properties=dict(
                                               hard_n=hard_n,
                                               hard_digits=hard_digits,
                                               easy_n=easy_n,
                                               easy_digits=easy_digits
                                           ))
            question_class.put()
        else:
            question_class = class_query.fetch(1)[0]

        # Check for Aversion Menu. Create if doesn't exist
        if AversionMenu.query(
                        AversionMenu.aversion_menu_name == SessionConstants.standard_aversion_menu_name).count() == 0:
            generate_standard_risk_menu()

        # List of questions not to be reused
        question_key_exclusion_list = []

        tutorial_id = generate_session_treatment(treatment_type=SessionConstants.tutorial_string,
                                                 treatment_group=treatment_group,
                                                 number_of_questions=questions_per_round,
                                                 question_class=question_class,
                                                 hard_payoff_generating_function=tutorial_hard_payoff,
                                                 easy_payoff_generating_function=tutorial_easy_payoff,
                                                 number_of_rounds=1,
                                                 time_limit_minutes=time_limit_minutes,
                                                 time_value=time_value,
                                                 payoff_known=False,
                                                 question_key_exclusion_list=question_key_exclusion_list
                                                 )
        generated_rounds = MultitaskRoundTreatment.query(ancestor=tutorial_id).fetch()[0]
        question_key_exclusion_list.extend(generated_rounds.question_keys_hard)
        question_key_exclusion_list.extend(generated_rounds.question_keys_easy)

        practice_id = generate_session_treatment(treatment_type=SessionConstants.practice_string,
                                                 treatment_group=treatment_group,
                                                 number_of_questions=questions_per_round,
                                                 question_class=question_class,
                                                 hard_payoff_generating_function=lambda: 0,
                                                 easy_payoff_generating_function=lambda: 0,
                                                 number_of_rounds=practice_n_rounds,
                                                 time_limit_minutes=practice_time_limit,
                                                 time_value=0,
                                                 payoff_known=False,
                                                 question_key_exclusion_list=question_key_exclusion_list
                                                 )

        generated_rounds = MultitaskRoundTreatment.query(ancestor=practice_id).fetch()
        for this_round in generated_rounds:
            question_key_exclusion_list.extend(this_round.question_keys_hard)
            question_key_exclusion_list.extend(this_round.question_keys_easy)

        t1_id_hard_high_variance = generate_session_treatment(treatment_type=SessionConstants.random_coefficient_string,
                                                              treatment_group=treatment_group,
                                                              number_of_questions=questions_per_round,
                                                              question_class=question_class,
                                                              hard_payoff_generating_function=hard_payoff_generating_function_high_variance,
                                                              easy_payoff_generating_function=easy_payoff_generating_function_low_varaince,
                                                              number_of_rounds=number_of_rounds,
                                                              time_limit_minutes=time_limit_minutes,
                                                              time_value=time_value,
                                                              payoff_known=False,
                                                              question_key_exclusion_list=question_key_exclusion_list,
                                                              hard_high=True,
                                                              hard_payoff_distribution=hard_payoff_distribution_high_variance,
                                                              easy_payoff_distribution=easy_payoff_distribution_low_variance
                                                              )

        t1_id_hard_low_variance = generate_session_treatment(treatment_type=SessionConstants.random_coefficient_string,
                                                             treatment_group=treatment_group,
                                                             number_of_questions=questions_per_round,
                                                             question_class=question_class,
                                                             hard_payoff_generating_function=hard_payoff_generating_function_low_variance,
                                                             easy_payoff_generating_function=easy_payoff_generating_function_high_varaince,
                                                             number_of_rounds=number_of_rounds,
                                                             time_limit_minutes=time_limit_minutes,
                                                             time_value=time_value,
                                                             payoff_known=False,
                                                             question_key_exclusion_list=question_key_exclusion_list,
                                                             hard_high=False,
                                                             hard_payoff_distribution=hard_payoff_distribution_low_variance,
                                                             easy_payoff_distribution=easy_payoff_distribution_high_variance
                                                             )

        generated_rounds = MultitaskRoundTreatment.query(ancestor=t1_id_hard_high_variance).fetch()
        for this_round in generated_rounds:
            question_key_exclusion_list.extend(this_round.question_keys_hard)
            question_key_exclusion_list.extend(this_round.question_keys_easy)

        t2_id = generate_session_treatment(treatment_type=SessionConstants.constant_coefficient_string,
                                           treatment_group=treatment_group,
                                           number_of_questions=questions_per_round, question_class=question_class,
                                           hard_payoff_generating_function=constant_hard_payoff,
                                           easy_payoff_generating_function=constant_easy_payoff,
                                           number_of_rounds=number_of_rounds,
                                           time_limit_minutes=time_limit_minutes,
                                           time_value=time_value,
                                           payoff_known=True,
                                           question_key_exclusion_list=question_key_exclusion_list
                                           )

        experiment_key = ExperimentManagement(experiment_name=treatment_group,
                                              practice_session_id=practice_id,
                                              tutorial_session_id=tutorial_id,
                                              treatment_session_id_list={
                                                  SessionConstants.random_coefficient_string: [
                                                      t1_id_hard_high_variance.urlsafe(),
                                                      t1_id_hard_low_variance.urlsafe()],
                                                  SessionConstants.constant_coefficient_string: [t2_id.urlsafe()]},
                                              aversion_menu_name=SessionConstants.standard_aversion_menu_name,
                                              experiment_running=True,
                                              risk_assessment_enabled=False,
                                              tutorial_enabled=False,
                                              practice_enabled=False,
                                              session_enabled=False,
                                              survey_enabled=False).put()
        return experiment_key
