from jinja_render import jinja_render
from flask import request, jsonify, redirect, Blueprint, url_for
from contextlib import contextmanager
from data_classes import *
from generate_data import *
import logging
import urllib
from flask import render_template

from flow_control import UserFlowControl

def risk_assessment():
    session_id = request.args.get('session_id', default='')
    step = request.args.get('step')

    logging.info(f"Risk assessment started for session_id: {session_id}")

    if session_id == '':
        logging.error("Missing session id in risk assessment")
        return redirect(url_for('welcom_screen', redirect_message='page: /risk_assessment/. Missing session id'))
    
    
    session = Session.get_by_id(session_id)
    if not session:
        logging.error(f"Session not found for id: {session_id}")
        return redirect(url_for('welcom_screen'))

    this_menu = AversionMenu.query(AversionMenu.aversion_menu_name == SessionConstants.standard_aversion_menu_name).get()
    list_of_lotteries = this_menu.list_of_lotteries
    aversion_menu_name = this_menu.aversion_menu_name
    #continue_link = UserFlowControl().get_next_url(session_id=session_id)
    template_values = {
        'list_of_lotteries': list_of_lotteries,
        'aversion_menu_name': aversion_menu_name,
        #'continue_link': continue_link,
        'session_id': session_id
    }
    return render_template('Risk_Assessment.html', **template_values)

def end_risk_assessment():
    data = request.json
    risk_results = data.get("radio_results")
    menu_name = data.get("menu_name")
    session_id = data.get("session_id")

    logging.info(f"Risk assessment ended for session_id: {session_id}")
    logging.info(f"Received data: {data}")  # Log the received data for debugging

    if not all([risk_results, menu_name, session_id]):
        logging.error("Missing required data in risk assessment end")
        return jsonify({'success': False, 'error': 'Missing required data'}), 400
    
    
    logging.info(f"Attempting to retrieve session with id: {session_id}")
    session = Session.get_by_id(session_id)
    if not session:
        logging.error(f"Session not found for id: {session_id}")
        return jsonify({'success': False, 'error': 'Invalid session'}), 400
    
    formatted_results = risk_results
    aversion_results = AversionResult(aversion_menu_name=menu_name, list_of_choices=formatted_results)

    participant = ParticipantInformation.query(
        ParticipantInformation.participant_id == session.email,
        ancestor=session.experiment_key
    ).get()

    if not participant:
        logging.error(f"Participant not found for session: {session_id}")
        return jsonify({'success': False, 'error': 'Participant not found'}), 404

    participant.aversion = aversion_results
    participant.put()

    logging.info(f"Risk assessment completed for session {session_id}, participant {session.email}")
    next_url = UserFlowControl().get_next_url(session_id=session_id)
    
    parsed_url = urllib.parse.urlparse(next_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    query_params['session_id'] = [session_id]
    new_query = urllib.parse.urlencode(query_params, doseq=True)
    next_url = urllib.parse.urlunparse(parsed_url._replace(query=new_query))
    logging.info(f"Redirecting to {next_url} after risk assessment")
    return jsonify({'success': True, 'next_url': next_url})