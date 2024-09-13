from google.appengine.ext import ndb
from data_classes import Session, ParticipantInformation, ExperimentManagement
from data_constants import SessionConstants
from admin_constants import AdminConstants
from jinja_render import jinja_render
from administrator import AdminFunctions
import math

class SummaryScreenHandler(webapp2.RequestHandler):
    def get(self):
        session_id = self.request.get('session_id')
        step = self.request.get('step')

        session = Session.get_by_id(session_id)
        if not session:
            self.redirect('/')
            return
        
        participant = ParticipantInformation.query(
            ParticipantInformation.participant_id == session.email,
            ancestor=session.experiment_key
        ).get()

        if not participant:
            self.response.write("Participant not found")
            return
        
        participant.active = False
        participant.put()
        
        experiment = session.experiment_key.get()

        if ndb.Key(urlsafe=participant.treatment_keys[0]).get().treatment_type == SessionConstants.constant_coefficient_string:
            s1_name = "Constant Piece-Rate"
            s2_name = "Uncertain Piece-Rate"
        else:
            s1_name = "Uncertain Piece-Rate"
            s2_name = "Certain Piece-Rate"

        list_of_earnings = [
            ['Participation', AdminConstants.participation_fee],
            ['Lottery Winnings', AdminFunctions().get_lottery_winnings(participant=participant)],
            ['Fixed Wage Round', AdminConstants.practice_fee],
            [s1_name, AdminFunctions().get_session_earnings(participant=participant, session_index=0)],
            [s2_name, AdminFunctions().get_session_earnings(participant=participant, session_index=1)]
        ]

        total_earnings = sum([i[1] for i in list_of_earnings])
        adjusted_earnings = self.get_adjusted_earnings(total_earnings)
        if adjusted_earnings[0] == total_earnings:
            adjusted_earnings_message = None
        else:
            adjusted_earnings_message = adjusted_earnings[1]
        rounded_earnings = math.ceil(adjusted_earnings[0])
        list_of_earnings_strings = [[i[0], '%.2f' % i[1]] for i in list_of_earnings]
        
        template_values = dict(
            list_of_earnings=list_of_earnings_strings,
            total_earnings='%.2f' % total_earnings,
            rounded_earnings='%.2f' % rounded_earnings,
            adjusted_earnings_message=adjusted_earnings_message,
            adjusted_earnings='%.2f' % adjusted_earnings[0]
        )
        self.response.write(jinja_render('Summary_Screen.html', template_values))

    def get_adjusted_earnings(self, total_earnings):
        if total_earnings > AdminConstants.max_earnings:
            return [AdminConstants.max_earnings, "Maximum allowable earnings reached."]
        elif total_earnings < AdminConstants.min_earnings:
            return [AdminConstants.min_earnings, "Your earnings were below the minimum allowed earnings, so they have been adjusted upwards."]
        else:
            return [total_earnings, ""]