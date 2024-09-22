import os
import sys
import logging

from survey import survey_end, survey_load
logging.basicConfig(level=logging.INFO)



# Add the 'lib' directory to the Python path
lib_path = os.path.join(os.path.dirname(__file__), 'lib')
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)


from flask import Flask, request, jsonify, send_file, redirect, url_for
from google.cloud import ndb


from round_running import load_question, question_submission, round_running
from round_end import end_round
from session_welcome import session_welcome
from session_end import end_session
from session_generate import generate_session
from session_instructions import session_instructions
from risk_assessment import end_risk_assessment, risk_assessment
from administrator import admin, admin_homepage, admin_prompts, download_aversion_data, download_multitask_data, enable_practice, enable_risk_assessment, enable_session, enable_survey, enable_tutorial, generate_experiment, generate_fake_participants, get_earnings, get_experiment, list_participants, randomize_treatment, reset_experiment
from summary_screen import summary_screen
from data_classes import client

from flow_control import check_condition, flow_control, UserFlowControl, pause_function
from administrator import admin

app = Flask(__name__)
app.secret_key = 'productionFunctionUncertainty'
logging.basicConfig(filename='app.log', level=logging.DEBUG) 

app.register_blueprint(flow_control)
app.register_blueprint(admin)


# NDB middleware
def ndb_wsgi_middleware(wsgi_app):
    def middleware(environ, start_response):
        with client.context():
            return wsgi_app(environ, start_response)
    return middleware

app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)

@app.route('/')
def welcome_screen():
    return session_welcome()

@app.route('/round_running/')
def in_round_running_main():
    return round_running()

@app.route('/submit_question/', methods=['POST'])
def question_submission_handler():
    return question_submission()

@app.route('/load_question/', methods=['POST'])
def load_question_handler():
    return load_question()

@app.route('/end_round/')
def end_round_handler():
    return end_round()

@app.route('/end_session/')
def end_session_handler():
    return end_session()

@app.route('/session_instructions/')
def session_instructions_handler():
    return session_instructions().get()

@app.route('/risk_assessment/')
def risk_assessment_handler():
    return risk_assessment()

@app.route('/risk_assessment_end/', methods=['POST'])
def end_risk_assessment_handler():
    return end_risk_assessment()

@app.route('/survey/')
def survey_handler():
    return survey_load()

@app.route('/survey_end/', methods=['POST'])
def survey_end_handler():
    return survey_end()

@app.route('/pause/')
def pause_handler():
    return pause_function().get()

@app.route('/check_continue_condition/')
def check_condition_handler():
    return check_condition().get()
    name = request.args.get('name')
    session_id = request.args.get('session_id')

@app.route('/summary_screen/')
def summary_screen_handler():
    return summary_screen()


'''
# Admin routes
@app.route('/session_generator/', methods=['GET', 'POST'])
def generate_session_handler():
    return generate_session().get()

@app.route('/admin/')
def admin_homepage_handler():
    return admin_homepage().get()

@app.route('/admin/generate_experiment/')
def generate_experiment_handler():
    return generate_experiment()

@app.route('/admin/get_experiment/')
def get_experiment_handler():
    return get_experiment().get()

@app.route('/admin/reset_experiment/')
def reset_experiment_handler():
    return reset_experiment().get()

@app.route('/admin/enable_risk_assessment/')
def enable_risk_assessment_handler():
    return enable_risk_assessment().get()

@app.route('/admin/enable_tutorial/')
def enable_tutorial_handler():
    return enable_tutorial().get()

@app.route('/admin/enable_practice/')
def enable_practice_handler():
    return enable_practice().get()

@app.route('/admin/enable_session/')
def enable_session_handler():
    return enable_session().get()

@app.route('/admin/enable_survey/')
def enable_survey_handler():
    return enable_survey().get()

@app.route('/admin/randomize_treatment/')
def randomize_treatment_handler():
    return randomize_treatment().get()

@app.route('/admin/get_earnings/')
def get_earnings_handler():
    return get_earnings().get()

@app.route('/admin/list_participants/')
def list_participants_handler():
    return list_participants().get()

@app.route('/admin/prompts/')
def admin_prompts_handler():
    return admin_prompts().get()

@app.route('/admin/download_multitask_data/')
def admin_data_download_handler():
    return download_multitask_data().get()

@app.route('/admin/download_aversion_data/')
def admin_aversion_download_handler():
    return download_aversion_data().get()

@app.route('/admin/generate_fake_participants/')
def generate_fake_participants_handler():
    return generate_fake_participants().get()
'''

if __name__ == '__main__':
    app.run(debug=True)