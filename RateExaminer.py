import os, json, logging, time, requests, threading
from datetime import datetime


class RateExaminer:
    current_path = os.path.dirname(os.path.abspath(__file__))
    log_file = ""
    json_file = ""
    thread_results = []
    request_id = 0
    url = "http://localhost/"
    requests_blocked = False
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

        # json folder and files
        json_folder_path = os.path.join(self.current_path, "json")
        self.json_file = os.path.join(json_folder_path, f"{current_time}.json")
        if not os.path.exists(json_folder_path):
            os.makedirs(json_folder_path)
        with open(self.json_file, "w") as file:
            json.dump({"data": []}, file)

        self.main_loop()

    """################################################################################# UI
    """  #################################################################################

    def main_loop(self):
        while True:
            menu_items = [
                {"text": f"Enter URL ( current: {self.url} )", "func": self.enter_url},
                {"text": f"Start operation", "func": self.start_operation},
            ]
            self.show_menu(menu_items)

    def show_menu(self, given_array):
        print("MENU OF OPTIONS")
        for i in range(len(given_array)):
            print(f"{i}:\t{given_array[i]['text']}")

        while True:
            user_input = input("Select an option from list above by its number: ")
            if user_input.isdigit() and int(user_input) < len(given_array):
                given_array[int(user_input)]["func"]()
                print("################################################\n\n")
                break
            else:
                print("Invalid input")

    def enter_url(self):
        while True:
            url = input(f"\nEnter your desired URL: ( current is: {self.url} ) ")
            if url == "0":
                return
            else:
                self.url = url
                self.log(f"the target URL changed to {url}")
                break

    """################################################################################# saving & log
    """  #################################################################################

    def save_json(self, dict):
        file_content = self.read_json()
        with open(self.json_file, "w") as f:
            final_data = {"data": file_content["data"] + [dict]}
            json.dump(final_data, f, indent=4)

    def read_json(self):
        with open(self.json_file, "r") as f:
            return json.load(f)

    def log(self, message, level="INFO"):
        # Configure logging (optional for basic usage)
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="[%(asctime)s] [%(levelname)s] %(message)s",
        )

        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level not in valid_levels:
            raise ValueError(
                f"Invalid log level: '{level}'. Valid levels are: {', '.join(valid_levels)}"
            )

        # Log the message using the logging module
        log_text = f"{message}"
        print(f"{level+': ' if level!='INFO' else ''}{log_text}")
        logging.log(getattr(logging, level.upper()), log_text)

    """################################################################################# general
    """  #################################################################################

    def send_req(self, save_to_results=False, log_enabled=False):
        try:
            request_id = (
                self.request_id
            )  # saving in function's own stack so the other threads doesnt change it

            # send request and calculate elapsed time
            request_time = time.time()  # saving request sent time
            response = requests.get(self.url)
            elapsed_time = time.time() - request_time

            # check if request is blocked or not
            self.requests_blocked = False
            good_codes = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]
            if response.status_code not in good_codes:
                self.requests_blocked = True

            # Log the response
            if log_enabled:
                log_text = f"Response {request_id} status code is: {response.status_code}. time took to get the response: {elapsed_time}"
                log_type = "ERROR" if self.requests_blocked else "INFO"
                self.log(log_text, log_type)

            # returning back the results
            return_value = {
                "ok": self.requests_blocked,
                "code": response.status_code,
                "time": elapsed_time,
            }
            if save_to_results:
                self.thread_results.append(return_value)
            return return_value

        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: Error - {e}", "ERROR")

    def start_threads(
        self, number, given_time=False, log_enabled=False, stop_on_block=True
    ):
        # Start the thread
        threads = []
        for i in range(number):
            # exit point
            if stop_on_block and self.requests_blocked:
                self.requests_blocked = False
                return i
            thread = threading.Thread(target=self.send_req, args=(True, log_enabled))
            thread.start()
            self.request_id += 1
            threads.append(thread)
            if given_time:
                time.sleep(given_time / number)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # reset requests id
        self.request_id = 0

    def am_i_blocked(self):
        test_req = self.send_req()
        self.log(
            f"According to test result: you are{' not' if test_req['ok'] else ''} blocked",
            "INFO" if test_req["ok"] else "ERROR",
        )
        return not test_req["ok"]

    """################################################################################# main
    """  #################################################################################

    def start_operation(self):
        pass
