from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from google.cloud import ndb
from data_classes import Session, ParticipantInformation, SurveyResponse
from admin_constants import AdminConstants
from flow_control import UserFlowControl
import json
from jinja_render import jinja_render

def survey_load():
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
    session.put()
    template_values = {
        'continue_link': UserFlowControl().get_next_url(session_id=session_id, increment=False),
        'session_id': session_id,
        'survey_price': f"${AdminConstants.SURVEY_FEE:.2f}"
    }
    return jinja_render('Survey.html', template_values)

def survey_end():
    data = request.get_json()
    survey_results = data['results']
    session_id = data['session_id']
    
    session = Session.get_by_id(session_id)
    if not session:
        return jsonify({'success': False, 'error': 'Invalid session'}), 400
    
    participant = ParticipantInformation.query(
        ParticipantInformation.participant_id == session.email,
        ancestor=session.experiment_key
    ).get()

    survey_response = SurveyResponse(survey_name='pilot', list_of_responses=survey_results)
    participant.survey_result = survey_response
    participant.put()
    
    
    return jsonify({'success': True})
  