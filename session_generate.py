from jinja_render import jinja_render
from flask import request, jsonify, redirect, url_for, Blueprint


from data_classes import *
from generate_data import *

def generate_session():
    if request.method == 'GET':
        template_values = {
                'questions_in_database': Question.query().count(),
                'default_question_class': 'add_hn4d2_en8d1'
            }

        return jinja_render('Generate_Sessions.html', template_values)
    
    elif request.method == 'POST':
        action = request.form.get('action', default='generate_questions')
        if action == 'generate_questions':
            question_class = request.form.get('question_class_to_generate')
            number_of_questions_to_generate = int(request.form.get('number_of_questions_to_generate'))
            question_difficulty = request.form.get('question_difficulty')
            for n in range(number_of_questions_to_generate):
                if question_difficulty == 'both':
                    generate_new_question(question_class, 'hard')
                    generate_new_question(question_class, 'easy')
                else:
                    generate_new_question(question_class, question_difficulty)

        elif action == 'generate_session':
            number_of_questions_per_round = int(request.form.get('number_of_questions_per_treatment'))
            number_of_rounds = int(request.form.get('number_of_rounds'))
            treatment_type = request.form.get('treatment_type')
            session_group = request.form.get('group_id')
            time_limit_minutes = int(request.form.get('time_limit_minutes'))
            session_question_class = request.form.get('session_question_class')
            generate_control = request.form.get('generate_control') == 'yes'
            generate_tour = request.form.get('generate_tour') == 'yes'
            control_type = request.form.get('control_type')
            
            treatment_session_key = generate_session_treatment(
                treatment_type=treatment_type,
                treatment_group=session_group,
                number_of_questions=number_of_questions_per_round,
                number_of_rounds=number_of_rounds,
                time_limit_minutes=time_limit_minutes,
                question_class=session_question_class
            )
            
            # Uncomment these lines when you're ready to implement these functions
            # if generate_control:
            #     control_session_key = generate_matching_control_session_treatment(
            #         matching_session_treatment_key=treatment_session_key, 
            #         treatment_type=control_type, 
            #         payoff_known=True
            #     )
            # if generate_tour:
            #     generate_matching_tour_session(matching_session_treatment_key=treatment_session_key)
        
        return redirect(url_for('generate_session'))
