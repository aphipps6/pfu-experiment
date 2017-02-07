import random
import datetime
from data_classes import *
import logging
from data_constants import *


def generate_session_treatment(treatment_type,
                               treatment_group,
                               number_of_questions,
                               question_class,
                               hard_payoff_generating_function,
                               easy_payoff_generating_function,
                               number_of_rounds,
                               time_limit_minutes,
                               time_value,
                               payoff_known,
                               question_key_exclusion_list,
                               hard_high=None,
                               hard_payoff_distribution=None,
                               easy_payoff_distribution=None,
                               ):
    """Generate a session treatment - this will create questions and treatment templates and tie them to a new
        Session Treatment object"""

    session_key = MultitaskSessionTreatment(treatment_type=treatment_type,
                                            treatment_group=treatment_group,
                                            hard_payoff_distribution=hard_payoff_distribution,
                                            easy_payoff_distribution=easy_payoff_distribution,
                                            hard_high_variance=hard_high,
                                            ).put()

    # Because every round treatment has only one parent, creating a new session requires creating new rounds
    rounds = generate_new_rounds(number_of_rounds=number_of_rounds,
                                 number_of_questions=number_of_questions,
                                 time_limit_minutes=time_limit_minutes,
                                 time_value=time_value,
                                 question_class=question_class,
                                 hard_payoff_generating_function=hard_payoff_generating_function,
                                 easy_payoff_generating_function=easy_payoff_generating_function,
                                 payoff_known=payoff_known,
                                 session_key=session_key,
                                 question_key_exclusion_list=question_key_exclusion_list)
    return session_key


def generate_new_rounds(number_of_rounds, number_of_questions, time_limit_minutes, time_value, question_class,
                        hard_payoff_generating_function, easy_payoff_generating_function, payoff_known, session_key,
                        question_key_exclusion_list):
    easy_questions, hard_questions = get_questions(number_of_questions=number_of_questions * number_of_rounds,
                                                   question_class=question_class,
                                                   question_key_exclusion_list=question_key_exclusion_list)
    round_list = []
    logging.info("IN: generate_data lin 45")
    logging.info(time_value)
    for n in range(number_of_rounds):
        this_easy_questions = easy_questions[n * number_of_questions:(n + 1) * number_of_questions]
        this_hard_questions = hard_questions[n * number_of_questions:(n + 1) * number_of_questions]
        round_list.append(MultitaskRoundTreatment(parent=session_key,
                                                  hard_payoff=hard_payoff_generating_function(),
                                                  easy_payoff=easy_payoff_generating_function(),
                                                  round_number=n,
                                                  payoff_known=payoff_known,
                                                  question_keys_hard=this_hard_questions,
                                                  question_keys_easy=this_easy_questions,
                                                  time_limit_minutes=time_limit_minutes,
                                                  time_value=time_value).put())
    return round_list


def get_questions(number_of_questions, question_class, question_key_exclusion_list):
    ret_list = []
    for difficulty in ['easy', 'hard']:
        question_keys = Question.query(Question.question_class == question_class.type_name,
                                       Question.difficulty == difficulty).fetch(keys_only=True)
        filtered_keys = [i for i in question_keys if i not in question_key_exclusion_list]
        if len(filtered_keys) != number_of_questions:
            num_to_generate = number_of_questions - len(filtered_keys)
            filtered_keys.extend(
                generate_new_questions(question_class=question_class,
                                       number_to_generate=num_to_generate,
                                       difficulty_list=[difficulty]
                                       )
            )
        random.shuffle(filtered_keys)
        ret_list.append(filtered_keys)
    return ret_list[0], ret_list[1]


def generate_new_questions(question_class, number_to_generate, difficulty_list=["easy", "hard"]):
    list_of_keys = []
    for difficulty in difficulty_list:
        for n in range(number_to_generate):
            list_of_keys.append(generate_new_question(question_class=question_class, difficulty=difficulty))
    return list_of_keys


def generate_new_question(question_class, difficulty):
    problem = []
    if difficulty == "easy":
        number_to_add = question_class.class_properties['easy_n']
        number_digits = question_class.class_properties['easy_digits']
    else:
        number_to_add = question_class.class_properties['hard_n']
        number_digits = question_class.class_properties['hard_digits']
    for n in range(number_to_add):
        new_number = random_with_n_digits(number_digits)
        if new_number % 10 == 0:
            new_number += random_with_n_digits(1)
        problem.append(new_number)
    components = ["&nbsp&nbsp&nbsp" + str(i) + "<br>" for i in problem[:number_to_add - 1]] + [
        "+&nbsp" + str(problem[number_to_add - 1]) + "<br>"]
    text = "".join(components)
    answer = sum(problem)
    return Question(text=text,
                    answer=str(answer),
                    difficulty=difficulty,
                    question_class=question_class.type_name).put()


def generate_standard_risk_menu():
    list_of_lotteries = []
    for i in range(1, 11):
        alt_prob = 10 - i
        name = "L" + "%02d" % (i,)
        lottery = dict(
            text_a=str(i) + "/10 of $2.00, &nbsp &nbsp" + str(alt_prob) + "/10 of $1.60",
            text_b=str(i) + "/10 of $3.85, &nbsp &nbsp" + str(alt_prob) + "/10 of $0.10",
            id_a=name + "A",
            id_b=name + "B",
            name=name,
            a_props=dict(probability=i, p1=2, p2=1.6),
            b_props=dict(probability=i, p1=3.85, p2=0.1)
        )
        list_of_lotteries.append(lottery)
    this_menu = AversionMenu(aversion_menu_name=SessionConstants.standard_aversion_menu_name, list_of_lotteries=list_of_lotteries)
    this_menu.put()


def random_with_n_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return random.randint(range_start, range_end)
