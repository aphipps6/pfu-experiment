import traceback
from flask import Flask, request, jsonify, redirect, session, url_for
from google.cloud import ndb
from jinja_render import jinja_render


from data_classes import *
#from generate_data import *
from data_constants import *
from admin_constants import AdminConstants

import json
import urllib.parse
import logging

from flask import Blueprint
flow_control = Blueprint('flow_control', __name__)


class UserFlowControl:
    tutorial_string = "tutorial"
    practice_string = "practice_round"
    
    def get_next_url(self, session_id, pause=True, return_dict=False, proctor=False, increment = False):
        if not proctor:
            logging.info(f"Getting next URL for session_id: {session_id}")
        
            session = Session.get_by_id(session_id)
            if not session:
                logging.error(f"Session not found for id: {session_id}")
                return '/'  # Redirect to start if session not found

            # the welcome screen needs the continue link to be set for the hnext step
            # This is only for recovery purposes
            if increment == True:
                session.current_step += 1
                session.put()
            next_step = session.current_step + 1
            
        
        else:
           # guide_info = f'session_id=&step=0'
            next_step = 0

        url_order = {
            0: {'name': 'welcome_screen', 'url': '/'},
            1: {'name': 'risk_assessment', 'url': url_for('risk_assessment_handler',session_id=session_id, step=next_step)},  
            2: {'name': UserFlowControl.tutorial_string, 'url': url_for('in_round_running_main',session_id=session_id, treatment=SessionConstants.tutorial_string, step=next_step)}, 
            3: {'name': UserFlowControl.practice_string, 'url': url_for('in_round_running_main', session_id=session_id,treatment=SessionConstants.practice_string, step=next_step)},  
            4: {'name': 'treatment_1', 'url': url_for('in_round_running_main',session_id=session_id,treatment=1, step=next_step)},  
            5: {'name': 'treatment_2', 'url': url_for('in_round_running_main',session_id=session_id,treatment=2, step=next_step)},  
            6: {'name': 'survey', 'url': url_for('survey_handler',session_id=session_id,treatment=SessionConstants.survey_string, step=next_step)},  
            7: {'name': 'summary_screen', 'url': url_for('summary_screen_handler',session_id=session_id, step=next_step)},  
        }
        
        if next_step >= len(url_order):
            logging.info("No more steps. Redirecting to END")
            next_step = len(url_order) - 1

        next_url = url_order[next_step]['url']
        if pause:
            props = {'name': url_order[next_step]['name'], 'url': next_url, 'session_id': session_id}
            return url_for('pause_handler') + '?' + urllib.parse.urlencode(props)  
        elif return_dict:
            return url_order
        else:
            return next_url

    def get_instructions(self, name, session_id, proctor=False):
        logging.info(f"Getting instructions for name: {name}, session_id: {session_id}")
        try:
            session = Session.get_by_id(session_id)
            if not session:
                logging.error(f"Session not found for id: {session_id}")
                return "Invalid session"

            logging.info(f"Session retrieved successfully: {session}")

            if name == 'risk_assessment':
                instructions = InstructionConstants.risk_assessment
            elif name == UserFlowControl.tutorial_string:
                instructions = InstructionConstants.tutorial
            elif name == UserFlowControl.practice_string:
                instructions = InstructionConstants.fixed_wage
            elif name == "treatment_1" or name == "treatment_2":
                if proctor:
                    instructions = InstructionConstants.proctor_session_instructions
                else:
                    if name == "treatment_1":
                        n = 0
                    else:
                        n = 1
                    participant = ParticipantInformation.query(
                        ParticipantInformation.participant_id == session.email,
                        ancestor=session.experiment_key
                    ).get()
                    if participant.treatment_keys is None:
                        logging.info("treatment keys is none. probably need to assign treatments")
                    this_treatment_key_urlsafe = participant.treatment_keys[n]
                    treatment_type = ndb.Key(urlsafe=this_treatment_key_urlsafe).get().treatment_type
                    instructions = UserFlowControl.get_instructions_for_treatment(treatment_type)
            elif name == "survey":
                instructions = InstructionConstants.survey
            elif name == "summary_screen":
                instructions = InstructionConstants.summary_screen
            else:
                instructions = "No instructions found"
            return instructions
        except Exception as e:
            logging.error(f"Error in get_instructions: {str(e)}. Perhaps proctor needs to assign treatments?")
            return "Error in get_intructions: {str(e)}"

    def get_instructions_for_treatment(treatment_type):
        if treatment_type == SessionConstants.constant_coefficient_string:
            return InstructionConstants.constant_coefficient
        else:
            return InstructionConstants.random_coefficient


class InstructionConstants:
    basic_rules = """
        <h4>Basic Rules for All Sessions:</h4>
          <ul>
            <li>There is no penalty for wrong answers</li>
            <li>There are many possible questions (usually about 30 easy and 30 hard questions per round), but if you run
                out, the round will end</li>
            <li>You can always end a round by pressing "stop". This will take you to the next round.</li>
            <li>You can always leave the experiment at any time. To do so, pleas quietly come get the proctor to end your
                session. You will be paid according to how much you've completed.</li>
            <li>Use pen and paper provided if it will help, <span class="bg-danger">but nothing else!</span></li>
            <li>If you end a round early (this can be done by pressing stop), you are welcome to quietly browse other
                websites, </span class="bg-danger">but it must be in another browser.</span>
          </ul>
        """
    welcome_scressn = """
        <h2>Welcome, and Some Basics<h2>
        <ul>
        <li>Do not use your browser forward, back, or refresh buttons</li>
        <li>Sometimes it takes a while to interact with the AppEngine browser, so please be patient. If the browser is
            busy, do not resubmit or press refresh.</li>
        </ul>
    """
    risk_assessment = """
      <h2>Lottery Menu</h2><p>In this part, you will be offered a set of lottery options. For example, one option may be
      presented like this: "3/10 of $2.00 or 7/10 of $1.00" (option A), and the other option may be "3/10 of $4.00 or
      7/10 of $0.10" (option B).</p><p>For each row, you are to select the option that you would prefer. We will actually
      play one of these lotteries, so pick what you would actually prefer!</p><p>I will randomly pick a number between 1
      and 10 to determine your winnings. Because of this, you can think of the fractions (e.g. 3/10) as probabilities.
      </p><p>You will be told at the end of the experiment what the results of the lottery were.</p>"""

    tutorial = """
      <h2>Tutorial</h2>
      <p>In the next part, you will be taken through a guided tour of the game we will be playing. None of the
      answers you submit in this round will count towards your final payoff. Make sure you understand how to interpret
      the results at the end of a round.</p>"""

    fixed_wage = """
      <h2>Fixed Payment Session</h2>
      <p> In this session, you will be paid a flat rate of $""" + '%.2f' % AdminConstants.PRACTICE_FEE + """
      <span class="bg-danger">regardless of how many questions you answer correctly</span>. We encourage you to do
      your best, since this will be helpful to us. While it is helpful for us that you do a mix of easy and hard problems,
       hard problems usually provide more information (at least in this part). Just remember, there are more rounds coming!</p>
      """ + basic_rules + """
      <h4>Rules Unique to This Session:</h4>
      <ul>
        <li><span class="bg-danger">In this session, there is no payoff from time remaining on the clock.</span></li>
        <li>The round results will be the same as in the tutorial, but it will show 0 in the payoffs. Just remember,
        for this part, <span color="bg-danger">you will be paid $"""+ '%.2f' % AdminConstants.PRACTICE_FEE + """ no
        matter how well you do </span>.
      </ul>
      <h4>Simple Hints</h4>
      <ul>
        <li>Skipping a lot of questions can end up costing you a lot of time</li>
      </ul>"""

    proctor_session_instructions = """
      Please read carefully the instructions about the next section. Your instructions are unique to you."""

    constant_coefficient = """
      <h2>Constant Piece-Rate</h2>
      <p> In this session, you will be paid  $""" + '%.2f' % AdminConstants.CONSTANT_COEFFICIENTS_EASY + """
      for each easy question you answer correctly, and $""" + '%.2f' % AdminConstants.CONSTANT_COEFFICIENTS_HARD + """
      for each hard question you answer correctly.</p>
      <h4>Rules Unique to This Session:</h4>
      <ul>
        <li>You will receive $""" + '%.2f' % AdminConstants.TIME_VALUE + """
            for each minute remaining on the clock when you end the round.</li>
      </ul>
      <h4>Simple Hints</h4>
      <ul>
        <li>Skipping a lot of questions can end up costing you a lot of time</li>
      </ul>""" + basic_rules

    random_coefficient = """
      <h2>Uncertain Piece-Rate</h2>
      <p> In this session, you will be paid for each correctly answered easy question, and for each correctly answered
      hard question. However, <span class="bg-danger">you do not know the exact amount that each is worth until the end of each round.
      </span> Furthermore, the amount you are paid will change each round. In other words, your payment for each
      question is randomly drawn from a distribution <span class="bg-danger">each round</span>.</p>
      <h4>Rules Unique to This Session:</h4>
      <ul>
        <li><span class="bg-danger">The distributions for easy and hard payments do not change each round.</span></li>
        <li><span class="bg-danger">The average payment for a hard question is higher than the average payment for
            an easy question.</span></li>
        <li><span class="bg-danger">It is not guaranteed that a hard question will always be worth more than an easy
            question!</span></li>
        <li>You will receive $""" + '%.2f' % AdminConstants.TIME_VALUE + """
            for each minute remaining on the clock when you end the round.</li>
      </ul>
      <h4>Simple Hints</h4>
      <ul>
        <li>Pay attention to how much the payoffs change each round!</li>
        <li>Skipping a lot of questions can end up costing you a lot of time</li>
      </ul>""" + basic_rules

    survey = """<h2>Brief Questionaire</h2><p>Next you will answer a few simple questions. Please answer as accurately
      as possible. <span class="bg-danger">You can skip any part of the survey without any penalty.</span></p>"""

    summary_screen = """<h2>Summary</h2><p>That ends the experiment! In the next screen, you will be shown your total earnings.
      Please be sure to enter the rounded earnings in your receipt form.</p>"""

@flow_control.route('/pause/')
def pause_function():
    next_url = request.args.get('url')
    logging.info(f"Pause function called with next_url: {next_url}")

    name = request.args.get('name')
    session_id = request.args.get('session_id')
    
    logging.info(f"Pause handler called with session_id: {session_id}")

    try:
        session = Session.get_by_id(session_id)
        if not session:
            logging.error(f"Session not found for id: {session_id}")
            return redirect(url_for('welcome_screen'))
        
        logging.info(f"Session retrieved successfully: {session}")
        experiment = session.experiment_key.get()
        
        user_flow_control = UserFlowControl()
        instructions = user_flow_control.get_instructions(name, session_id)
        
        continue_link = next_url
        check_data = {'name': name, 'session_id': session_id}
        condition_check_link = url_for('flow_control.check_condition', **check_data)
        
        template_values = {
            'instructions': instructions,
            'continue_link': continue_link,
            'condition_check_link': condition_check_link,
            'session_id': session_id
        }
        
        return jinja_render("Pause.html", template_values)
    except Exception as e:
        logging.error(f"Error in pause_handler: {str(e)}")
        return jsonify({'error': str(e)}), 500


@flow_control.route('/check_continue_condition/')
def check_condition():
    name = request.args.get('name')
    session_id = request.args.get('session_id')
    
    logging.info(f"Checking condition for name: {name}, session_id: {session_id}")
    
    if not session_id:
        logging.warning("Session ID not provided")
        return jsonify({'keep_going': False, 'error': 'Session ID not provided'}), 400
    
    try:
        session_key = ndb.Key('Session', session_id)
        logging.info(f"Attempting to retrieve session with key: {session_key}")
        session = session_key.get()

        if not session:
            logging.warning(f"Session not found for id: {session_id}")
            return jsonify({'keep_going': False, 'error': 'Session not found'})
        
        logging.info(f"Session retrieved: {session}")

        if not session.experiment_key:
            logging.warning(f"Experiment key not found for session: {session_id}")
            return jsonify({'keep_going': False, 'error': 'Experiment key not found'}), 404
        
        logging.info(f"Attempting to retrieve experiment with key: {session.experiment_key}")

        experiment = session.experiment_key.get()
        if not experiment:
            logging.warning(f"Experiment not found for session: {session_id}")
            return jsonify({'keep_going': False, 'error': 'Experiment not found'})
        
        logging.info(f"Experiment retrieved: {experiment}")

        keep_going = False
        
        if name == 'risk_assessment':
            keep_going = experiment.risk_assessment_enabled
        elif name == UserFlowControl.tutorial_string:
            keep_going = experiment.tutorial_enabled
        elif name == UserFlowControl.practice_string:
            keep_going = experiment.practice_enabled
        elif name == "treatment_1" or name == "treatment_2":
            keep_going = experiment.session_enabled
        elif name == "survey":
            keep_going = experiment.survey_enabled
        elif name == "summary_screen":
            keep_going = experiment.summary_enabled
        else:
            logging.warning(f"Unknown condition name: {name}")
            return jsonify({'keep_going': False, 'error': 'Unknown condition'}), 400
            
        logging.info(f"Condition check result for {name}: {keep_going}")
        return jsonify({'keep_going': keep_going})
    
    except Exception as e:
        logging.error(f"Error in check_condition_handler: {str(e)}")
        logging.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'keep_going': False, 'error': 'Internal server error'}), 500