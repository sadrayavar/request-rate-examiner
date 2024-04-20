import os, json, logging, time, requests, threading
from datetime import datetime


class RateExaminer:
    current_path = os.path.dirname(os.path.abspath(__file__))
    log_file = ""
    json_file = ""
    thread_results = []
    request_id = 0
    url = "http://localhost/"
    requests_ok = True
    precision = {"timeframe": 1, "blocktime": 1, "request": 1}

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
                print("\n")
                given_array[int(user_input)]["func"]()
                print("\n")
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

    """################################################################################# request
    """  #################################################################################

    def send_req(self, id, save_to_results=False, log_enabled=False):
        try:
            # send request and calculate elapsed time
            request_time = time.time()  # saving request sent time
            response = requests.get(self.url)
            elapsed_time = time.time() - request_time

            # check if request is blocked or not
            good_codes = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]
            condition = response.status_code in good_codes  # is not blocked
            self.requests_ok = (True) if (condition) else (False)

            # Log the response
            if log_enabled:
                log_text = f"Response {id} status code is: {response.status_code}. time took to get the response: {elapsed_time}"
                log_type = "INFO" if self.requests_ok else "ERROR"
                self.log(log_text, log_type)

            # returning back the results
            return_value = {
                "ok": self.requests_ok,
                "code": response.status_code,
                "time": elapsed_time,
            }
            if save_to_results:
                self.thread_results.append(return_value)
            return return_value

        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: Error - {e}", "ERROR")

    def start_threads(
        self, number, given_time=False, log_enabled=False, stop_on_block=False
    ):
        # Start the thread
        threads = []
        for i in range(number):
            # exit point
            if stop_on_block and not self.requests_ok:
                self.requests_ok = True
                return i
            thread = threading.Thread(
                target=self.send_req, args=(i, False, log_enabled)
            )
            thread.start()
            threads.append(thread)

            # spread request accros given time
            if given_time and (i != number - 1):
                time.sleep(given_time / (number - 1))

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    def am_i_blocked(self):
        response = self.send_req(id=0)
        log_text = f"According to test result: you are{' not' if response['ok'] else ''} blocked"
        log_level = "INFO" if response["ok"] else "ERROR"
        self.log(log_text, log_level)
        return not response["ok"]

    """################################################################################# main method
    """  #################################################################################

    def start_operation(self):
        pass


RateExaminer()
