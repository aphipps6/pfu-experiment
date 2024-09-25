from flask import Blueprint, render_template, request, redirect, url_for
from google.cloud import ndb
from data_classes import Session, ParticipantInformation, ExperimentManagement
from data_constants import SessionConstants
from admin_constants import AdminConstants
from administrator import AdminFunctions
import math
from jinja_render import jinja_render

def summary_screen():
    session_id = request.args.get('session_id')
    step_str = request.args.get('step')

    # Safely convert step to an integer
    try:
        step = int(step_str)
    except (ValueError, TypeError):
        # Handle the error - redirect to an error page or set a default value
        return redirect(url_for('error_page', message="Invalid step value"))

    session = Session.get_by_id(session_id)
    if not session:
        return redirect(url_for('welcome_screen'))
    
    session.current_step = step
    participant = ParticipantInformation.query(
        ParticipantInformation.participant_id == session.email,
        ancestor=session.experiment_key
    ).get()

    if not participant:
        return "Participant not found", 404
    
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
        ['Participation', AdminConstants.PARTICIPATION_FEE],
        ['Lottery Winnings', AdminFunctions.get_lottery_winnings(participant=participant)],
        ['Fixed Wage Round', AdminConstants.PRACTICE_FEE],
        [s1_name, AdminFunctions.get_session_earnings(participant=participant, session_index=0)],
        [s2_name, AdminFunctions.get_session_earnings(participant=participant, session_index=1)]
    ]

    total_earnings = sum(earning[1] for earning in list_of_earnings)
    adjusted_earnings = get_adjusted_earnings(total_earnings)
    
    if adjusted_earnings[0] == total_earnings:
        adjusted_earnings_message = None
    else:
        adjusted_earnings_message = adjusted_earnings[1]
    
    rounded_earnings = math.ceil(adjusted_earnings[0])
    list_of_earnings_strings = [[earning[0], f'{earning[1]:.2f}'] for earning in list_of_earnings]
    
    template_values = {
        'list_of_earnings': list_of_earnings_strings,
        'total_earnings': f'{total_earnings:.2f}',
        'rounded_earnings': f'{rounded_earnings:.2f}',
        'adjusted_earnings_message': adjusted_earnings_message,
        'adjusted_earnings': f'{adjusted_earnings[0]:.2f}'
    }
    return render_template('Summary_Screen.html', **template_values)


def get_adjusted_earnings(total_earnings):
    if total_earnings > AdminConstants.MAX_EARNINGS:
        return [AdminConstants.MAX_EARNINGS, "Maximum allowable earnings reached."]
    elif total_earnings < AdminConstants.MIN_EARNINGS:
        return [AdminConstants.MIN_EARNINGS, "Your earnings were below the minimum allowed earnings, so they have been adjusted upwards."]
    else:
        return [total_earnings, ""]