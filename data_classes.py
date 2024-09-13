from google.appengine.ext import ndb


class AversionMenu(ndb.Model):
    """list_of_lotteries is a list of dictionaries"""
    aversion_menu_name = ndb.StringProperty()
    list_of_lotteries = ndb.JsonProperty(indexed=False)


class SurveyResponse(ndb.Model):
    survey_name = ndb.StringProperty()
    list_of_responses = ndb.JsonProperty(indexed=False)


class Survey(ndb.Model):
    survey_name = ndb.StringProperty()
    list_of_questions = ndb.JsonProperty(indexed=False)


class AversionResult(ndb.Model):
    """
    A model for each response to aversion questions
    list of choices is a list of dictionary objects!
    """
    aversion_menu_name = ndb.StringProperty()
    list_of_choices = ndb.JsonProperty(indexed=False)


class QuestionClass(ndb.Model):
    """A set of properties for questions"""
    type_name = ndb.StringProperty()
    hard_description = ndb.StringProperty(indexed=False)
    easy_description = ndb.StringProperty(indexed=False)
    class_properties = ndb.JsonProperty(indexed=False)


class ParticipantInformation(ndb.Model):
    """A model for information about users"""
    _default_indexed = False
    participant_id = ndb.StringProperty()
    participant_name = ndb.StringProperty()
    survey_result = ndb.StructuredProperty(SurveyResponse)
    aversion = ndb.StructuredProperty(AversionResult)
    active = ndb.BooleanProperty()
    treatment_keys = ndb.JsonProperty(indexed=False)


class SubmittedQuestion(ndb.Model):
    """A main model for representing a question response"""
    question_key = ndb.KeyProperty()
    datetime_start = ndb.DateTimeProperty(indexed=False)
    datetime_end = ndb.DateTimeProperty(indexed=False)
    submitted_answer = ndb.StringProperty(indexed=False)


class ParticipantMultitaskRound(ndb.Model):
    """A main model for representing a specific round"""
    earnings = ndb.FloatProperty()
    datetime_start = ndb.DateTimeProperty()
    datetime_end = ndb.DateTimeProperty()
    round_treatment_key = ndb.KeyProperty()
    round_number = ndb.IntegerProperty()
    # submitted_questions = ndb.StructuredProperty(SubmittedQuestion, repeated=True)


class ParticipantMultitaskSession(ndb.Model):
    """
    A model for representing an individual UserSession. This functions as the root model
    treatment_group is same as in MultitaskSessionTreatment
    """
    session_treatment_key = ndb.KeyProperty()
    datetime_start = ndb.DateTimeProperty()
    datetime_end = ndb.DateTimeProperty()
    treatment_group = ndb.StringProperty()


class MultitaskSessionTreatment(ndb.Model):
    """
    A model to be used as a session template
    treatment_type in {"tutorial","practice","rc","cc"}
    treatment_group is just a name that can be used to group session treatments
    """
    treatment_type = ndb.StringProperty()
    treatment_group = ndb.StringProperty()
    hard_payoff_distribution = ndb.JsonProperty()
    easy_payoff_distribution = ndb.JsonProperty()
    hard_high_variance = ndb.BooleanProperty()


class MultitaskRoundTreatment(ndb.Model):
    """A template for running a round"""
    hard_payoff = ndb.FloatProperty()
    easy_payoff = ndb.FloatProperty()
    payoff_known = ndb.BooleanProperty()
    round_number = ndb.IntegerProperty()
    question_keys_hard = ndb.KeyProperty(repeated=True)
    question_keys_easy = ndb.KeyProperty(repeated=True)
    time_limit_minutes = ndb.FloatProperty()
    time_value = ndb.FloatProperty()


class Question(ndb.Model):
    """A model for question templates, from which questions are populated in the experiment"""
    text = ndb.StringProperty(indexed=False)
    answer = ndb.StringProperty(indexed=False)
    difficulty = ndb.StringProperty()
    question_class = ndb.StringProperty()

class Session(ndb.Model):
    email = ndb.StringProperty()
    experiment_key = ndb.KeyProperty()
    current_step = ndb.IntegerProperty(default=0)
    last_activity = ndb.DateTimeProperty(auto_now=True)
    active = ndb.BooleanProperty(default=True)

class ExperimentManagement(ndb.Model):
    """
    A model for data relevant to managing the administration of an experiment
    lottery_played is the randomly selected lottery from the menu. This is a dictionary!
    lottery_result is the outcome of the played lottery
    treatment_session_id_list is a dictionary with rc and cc treatment sessions
    """
    experiment_name = ndb.StringProperty()
    experiment_running = ndb.BooleanProperty()
    aversion_menu_name = ndb.StringProperty()
    lottery_played = ndb.JsonProperty(indexed=False)
    lottery_result = ndb.IntegerProperty(indexed=False)
    tutorial_session_id = ndb.KeyProperty(indexed=False)
    practice_session_id = ndb.KeyProperty(indexed=False)
    treatment_session_id_list = ndb.JsonProperty(indexed=False)
    risk_assessment_enabled = ndb.BooleanProperty(indexed=False)
    tutorial_enabled = ndb.BooleanProperty(indexed=False)
    practice_enabled = ndb.BooleanProperty(indexed=False)
    session_enabled = ndb.BooleanProperty(indexed=False)
    survey_enabled = ndb.BooleanProperty(indexed=False)
    summary_enabled = ndb.BooleanProperty(indexed=False)
