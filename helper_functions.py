from data_classes import *
class HelperFunctions:
    @staticmethod
    def mean_time(list_of_times):
        return float(sum([i.total_seconds() for i in list_of_times])) / max(len(list_of_times), 1)

    @staticmethod
    def generate_fake_users(number_of_users, experiment_key_urlsafe):
        for i in range(number_of_users):
            p = ParticipantInformation(
                parent=ndb.Key(urlsafe=experiment_key_urlsafe),
                participant_id="test"+str(i)+"@test.com",
                participant_name="test"+str(i)+"@test.com",
                active=True
            ).put()