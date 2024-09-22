from jinja_render import jinja_render
from flask import request, Blueprint
from data_classes import *
from generate_data import *

session_instructions_bp = Blueprint('session_instructions', __name__)

@session_instructions_bp.route('/session_instructions')
def session_instructions():
    session_treatment = request.args.get('session_treatment', "rc")
    group_id = request.args.get('group_id', "TEST")
    
    tour_complete = request.args.get('tour_complete', '0')

    instructions = get_instructions(tour_complete, session_treatment, group_id)
    
    template_values = {
        'instructions': instructions,
        'session_treatment': session_treatment,
        'group_id': group_id
    }
    
    return jinja_render('Session_Instructions.html', template_values)


def get_instructions(tour_complete, session_treatment, group_id):
    if tour_complete == "1":
        disable_tour = " disabled"
    else:
        disable_tour = ""
    if session_treatment == "rc":
        page1 = dict(
            title="First, a Tour!",
            text="<p style=\"text-align:center\"> Before we begin, let's start with a quick tour of the game format.</p>",
            buttons=[
                "<a class=\"btn btn-theme btn-sm btn-min-block" + disable_tour + "\" href=\"/round_running/?session_treatment=tour_rc&group_id=" + group_id + "\">Start Tour</a>"
            ]
        )
        page2 = dict(
            title="Rounds",
            text="<p>Each round has a time limit. Within that time limit, you should answer as many hard or easy "
                    "questions as you like to earn money.</p><br><p>You may also end a round early and still earn a time "
                    "bonus. The value of ending a round early will be displayed.</p><br><p>At the end of each round, you "
                    "will be shown a detailed table of your activity during that round (and all previous rounds as "
                    "well). Use this table to improve your next round!</p>"
        )
        page3 = dict(
            title="Question Value",
            text="<p>You do not know the value of hard and easy questions until the end of each round, and they will "
                    "have different values each round. <b>So be sure to check in the round results!</b></p><br><p>On "
                    "average, hard questions will be worth more than easy questions, but this is not guaranteed to "
                    "be true every round.</p><br><p>You can submit a blank answer (or a wrong answer) with no penalty."
                    "</p><br><p>Please do not use any calculators or visit any other websites during the experiment, "
                    "though you are welcome to use the paper and pencil provided to help solve problems.</p>"
        )
        page4 = dict(
            title="Let's Go!",
            text="<p style=\"text-align:center\">In order to preserve a consistent experience across tests, the proctor can only help with " \
                    "technical assistance.</p>",
            buttons=[
                "<a class=\"btn btn-theme btn-sm btn-min-block\" href=\"/round_running/?session_treatment=rc&group_id=" + group_id + "\">Begin First Round!</a>"
            ]
        )
        instructions = [page1, page2, page3, page4]
    elif session_treatment == "cc":
        instructions = [dict(title="Not ready yet!", text="This set of instructions is incomplete :)")]
    else:
        instructions = [dict(title="Not ready yet!", text="This set of instructions is incomplete :)")]
    return instructions
