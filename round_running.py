import datetime
import logging
from data_classes import MultitaskRoundTreatment, ParticipantInformation, ParticipantMultitaskRound, ParticipantMultitaskSession, Question, Session, SubmittedQuestion, client
from jinja_render import jinja_render
from data_constants import *
from google.cloud import ndb

from flow_control import UserFlowControl
import urllib
from flask import render_template, request, redirect, url_for, jsonify
from flask import session as flask_session

def round_running():
    session_id = request.args.get('session_id', default='')
    treatment = request.args.get('treatment', default='')
    
    if not treatment:
        logging.error(f"Missing treatment value for session {session_id}")

    if session_id == '':
        message = urllib.parse.urlencode({'redirect_message': 'page: /round_running/. Missing session id'})
        return redirect(f"/?{message}")
        
    session = Session.get_by_id(session_id)
    if not session:
        message = urllib.parse.urlencode({'redirect_message': 'page: /round_running/. Session not found'})
        return redirect(f"/?{message}")
    
    step = session.current_step
    experiment = session.experiment_key.get()
    #treatment_group = experiment.treatment_group
    participant = ParticipantInformation.query(ParticipantInformation.participant_id == session.email).get()
    
    # check if round is currently in flask_session -- this could result if they hit "refresh". it should be empty
    test_round_key = flask_session.get('round_key')
    if test_round_key:
        logging.warning(f"Round key found in flask session when there shouldn't be one -- probably hit refresh")
        logging.warning(f"ending round {test_round_key}")
        redirect = url_for('end_round_handler', session_id=session_id, treatment=treatment)
    
    # Check for participant session key in flask session
    participant_session_key = flask_session.get('participant_session_key')
    if participant_session_key:
        try:
            participant_session_key_obj = ndb.Key(urlsafe=participant_session_key)
            participant_session = participant_session_key_obj.get()
            if participant_session is None:
                logging.warning(f"No entity found for key: {participant_session_key}")
                participant_session_key = None
            elif participant_session.key.parent() != participant.key:
                logging.warning(f"Session {participant_session.key} does not belong to participant {participant.key}")
                participant_session_key = None
        except Exception as e:
            logging.error(f"Error processing participant_session_key: {participant_session_key}. Error: {str(e)}")
            participant_session_key = None
    
    # Check the database if there is one
    if not participant_session_key:
        if treatment == SessionConstants.tutorial_string:
                session_treatment_key = experiment.tutorial_session_id
        elif treatment == SessionConstants.practice_string:
            session_treatment_key = experiment.practice_session_id
        else:
            try:
                index = int(treatment) - 1
                session_treatment_key = ndb.Key(urlsafe=participant.treatment_keys[index])
            except (ValueError, IndexError):
                    # Handle invalid treatment value
                raise ValueError(f"Invalid treatment value: {treatment}")
        logging.info(f"Checking for existing ParticipantMultitaskSession for participant {participant.participant_id}, session_id: {session_id}")
        participant_session = ParticipantMultitaskSession.query(
            ancestor=participant.key
        ).filter(ParticipantMultitaskSession.session_treatment_key == session_treatment_key
        ).get()
        if participant_session:
            flask_session['participant_session_key'] = participant_session.key.urlsafe().decode()
            logging.info(f"Found existing ParticipantMultitaskSession for participant {participant.participant_id}, session_id: {session_id}")

        # there really isn't one, so make one:
        else:
            # Create a new ParticipantMultitaskSession if it doesn't exist
            logging.info(f"Creating new ParticipantMultitaskSession for participant {participant.participant_id}, session_id: {session_id}")
            
            participant_session = create_participant_session(session_treatment_key, participant)
            flask_session['participant_session_key'] = participant_session.key.urlsafe().decode()
            session_treatment = participant_session.session_treatment_key.get()

    session_treatment = participant_session.session_treatment_key.get()
   

    # 2 - set up this round and round treatment
    # how many rounds in all? get all treatmentRounds tied to this session treatment
    
    total_rounds = MultitaskRoundTreatment.query(ancestor=session_treatment.key).count()

    # get round treatment
    round_number = ParticipantMultitaskRound.query(ancestor=participant_session.key).count()
    #round_treatment = MultitaskRoundTreatment.query(ancestor=participant_session.session_treatment_key).get()
    round_treatment = MultitaskRoundTreatment.query(
        MultitaskRoundTreatment.round_number == round_number,
        ancestor=participant_session.session_treatment_key
    ).get()

    if not round_treatment:
        # Handle the case where no matching round treatment is found
        return "No matching round treatment found", 404




    # create round record
    this_round = ParticipantMultitaskRound(
        parent=participant_session.key,
        round_treatment_key=round_treatment.key,
        round_number=round_number
    )
    round_key = this_round.put()
    
    # this makes it easy to pass round_key to the round_end screen
    flask_session['round_key'] = round_key.urlsafe().decode()

    # set up round
    round_minutes = round_treatment.time_limit_minutes
    round_minutes_string = f"{int(round_minutes):02d}"

    on_tour = session_treatment.treatment_type == SessionConstants.tutorial_string
    price_info = None

    if round_treatment.payoff_known:
        price_info = {
        'hard': f"${round_treatment.hard_payoff:.2f}",
        'easy': f"${round_treatment.easy_payoff:.2f}"
    }
    if session_treatment.treatment_type == SessionConstants.random_coefficient_string:
        price_info =dict(
            hard="--",
            easy="--"
        )

    logging.info(f"Round {round_number + 1} started, round_key {round_key.urlsafe().decode()} for participant {participant.participant_id}")


    template_values = {
        'round_minutes': int(round_minutes),
        'round_minutes_string': round_minutes_string,
        'session_id': session_id,
        'treatment': treatment,
        'session_treatment': session_treatment.treatment_type,
        'round_number': round_number + 1,
        'round_key': round_key.urlsafe().decode(),
        'total_rounds': total_rounds,
        'participant': participant.participant_id,
        'price_info': price_info,
        'step': step
    }

    ## REMOVED FOR DEBUGGING PURPOSES
    #template_name = "Tour_Round.html" if on_tour else "InSession_Running_Main.html"
    template_name =  "InSession_Running_Main.html"
    return render_template(template_name, **template_values)

def create_participant_session(session_treatment_key, participant):
    # the session_treatment_key is links to set of questions and payoffs
    session_treatment = session_treatment_key.get()
    participant_session = ParticipantMultitaskSession(
            parent=participant.key,
            session_treatment_key=session_treatment_key,
            datetime_start=datetime.datetime.now(),
            treatment_group=session_treatment.treatment_group
        )
    participant_session_id = participant_session.put()
    return participant_session

def question_submission():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400
    submitted_question_key = data.get('submitted_question_key')
    if not submitted_question_key:
        return jsonify({'error': 'No submitted_question_key provided'}), 400
    try:
        submitted_question = ndb.Key(urlsafe=submitted_question_key).get()
        if not submitted_question:
            return jsonify({'error': 'Submitted question not found'}), 404
        
        submitted_question.datetime_end = datetime.datetime.now()
        submitted_question.submitted_answer = data.get('submitted_answer')
        submitted_question.put()
        
        question = submitted_question.question_key.get()
        return jsonify({'difficulty': question.difficulty})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

def load_question():
    data = request.json
    difficulty = data['question_difficulty']
    round_key = data['round_key']
    session_id = data['session_id']
    
    logging.info(f"Loading question for round {round_key} and session {session_id}")

    session = Session.get_by_id(session_id)
    if not session:
        message = urllib.parse.urlencode({'redirect_message': 'page: /round_running/. Session not found'})
        return redirect(f"/?{message}")
        
        
    this_round = ndb.Key(urlsafe=round_key).get()
    
    if data['first_question'] == 1:
        this_round.datetime_start = datetime.datetime.now()
        this_round.put()

    #question_number = get_question_number(this_round, difficulty)
    question_number = data['question_number']

    question = get_new_question(difficulty=difficulty, this_round=this_round, question_number=question_number)
    if question is None:
        return jsonify({'end_round': True})
    else:
        submitted_question = SubmittedQuestion(
            parent=ndb.Key(urlsafe=round_key),
            question_key=question.key,
            datetime_start=datetime.datetime.now()
        )
        submitted_question_key = submitted_question.put()
        return jsonify({
            'end_round': False,
            'question_text': question.text,
            'submitted_question_key': submitted_question_key.urlsafe().decode()
        })

def get_question_number(this_round, difficulty):
    # use projection to only grab question_key from submitted questions
    completed_question_keys = [i.question_key for i in SubmittedQuestion.query(ancestor=this_round.key).fetch(
        projection=[SubmittedQuestion.question_key]) if i.question_key is not None]
    if len(completed_question_keys) > 0:
        # return the count; notice that this will be the correct number for the next question
        return Question.query(ndb.AND(Question.difficulty == difficulty,
                                        Question.key.IN(completed_question_keys))).count()
    else:
        return 0

def get_new_question(difficulty, this_round, question_number):
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