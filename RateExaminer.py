import os
from datetime import datetime


class RateExaminer:
    current_path = os.path.dirname(os.path.abspath(__file__))
    log_file = ""
    json_file = ""
    thread_results = []
    request_id = 0
    url = "http://localhost/"
    requests_blocked = True
    precision = {"time": 1, "request": 1}

    timeframe = {"min": 0, "max": 4, "last_decreased": ""}
    fallbacker = {"value": timeframe["max"], "decrease_twice": False}

    def __init__(self):
        current_time = datetime.now()

        # log folder and files
        log_folder_path = os.path.join(self.current_path, "logs")
        self.log_file = os.path.join(log_folder_path, f"{current_time}.log")
        if not os.path.exists(log_folder_path):
            os.makedirs(log_folder_path)
