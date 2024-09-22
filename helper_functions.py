from data_classes import ParticipantInformation
from google.cloud import ndb
from typing import List
from datetime import timedelta

class HelperFunctions:
    @staticmethod
    def mean_time(list_of_times: List[timedelta]) -> float:
        total_seconds = sum(i.total_seconds() for i in list_of_times)
        return float(total_seconds) / max(len(list_of_times), 1)

    @staticmethod
    def generate_fake_users(number_of_users: int, experiment_key_urlsafe: str) -> None:
        for i in range(number_of_users):
            participant_id = f"test{i}@test.com"
            p = ParticipantInformation(
                parent=ndb.Key(urlsafe=experiment_key_urlsafe),
                participant_id=participant_id,
                participant_name=participant_id,
                active=True
            ).put()