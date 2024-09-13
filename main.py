from round_running import *
from round_end import *
from session_welcome import *
from session_end import *
from session_generate import *
from session_instructions import *
from risk_assessment import *
from administrator import *
from survey import *
from summary_screen import *
from data_constants import *

import webapp2

# [START app]
app = webapp2.WSGIApplication([
    ('/', WelcomeScreenHandler),
    ('/round_running/', InRoundRunningMain),
    ('/submit_question/', QuestionSubmission),
    ('/load_question/', QuestionHandler),
    ('/end_round/', EndRoundHandler),
    ('/end_session/', EndSessionHandler),
    ('/session_instructions/', SessionInstructionsHandler),
    ('/session_generator/', GenerateSessionHandler),
    ('/risk_assessment/', RiskAssessmentHandler),
    ('/risk_assessment_end/', EndRiskAssessmentHandler),
    ('/survey/', SurveyHandler),
    ('/survey_end/', SurveyEndHandler),
    ('/pause/', PauseHandler),
    ('/check_continue_condition/', CheckConditionHandler),
    ('/summary_screen/', SummaryScreenHandler),
    ('/admin/', AdminHomepageHandler),
    ('/admin/generate_experiment/', GenerateExperimentHandler),
    ('/admin/get_experiment/', GetExperimentHandler),
    ('/admin/reset_experiment/', ResetExperimentHandler),
    ('/admin/enable_risk_assessment/', EnableRiskAssessmentHandler),
    ('/admin/enable_tutorial/', EnableTutorialHandler),
    ('/admin/enable_practice/', EnablePracticeHandler),
    ('/admin/enable_session/', EnableSessionHandler),
    ('/admin/enable_survey/', EnableSurveyHandler),
    ('/admin/randomize_treatment/', RandomizeTreatmentHandler),
    ('/admin/get_earnings/', GetEarningsHandler),
    ('/admin/list_participants/', ListParticipantsHandler),
    ('/admin/prompts/', AdminPromptsHandler),
    ('/admin/download_multitask_data/', AdminDataDownloadHandler),
    ('/admin/download_aversion_data/', AdminAversionDownloadHandler),
    ('/admin/generate_fake_participants/', GenerateFakeParticipantsHandler)
    
], debug=True)
