from typing import Any
from terminal_utils import pretty_substring, user_choice_bool
from math import e
from enum import IntEnum, StrEnum, auto
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from prompt_toolkit.filters.base import Condition
from InquirerPy.utils import patched_print
from prompt_toolkit import print_formatted_text

import json
from pathlib import Path
from colorama import Fore
from Course import Course

BASE_DST_PATH = Path("C:/Users/morri/Onedrive/University")
BASE_SRC_PATH = Path("C:/Users/morri/Downloads")
COURSE_JSON = "./courses.json"

cursor_pos = 0


class Folder(StrEnum):
    LAB = "Lab"
    ASSIGNMENT = "Assignment"
    REVIEW = "Review"
    LECTURE = "Lecture"
    TUTORIAL = "Tutorial"
    INFO = "Info"
    OTHER = "Other"


class Payload():
    def __init__(self, src: Path, dst: Path, course_code: str, course: Course):
        self.type = None
        self.src = src
        self.dst = self.generate_dst_path(dst)
        self.sent = False
        self.course_code = course_code
        self.course = course

    def __eq__(self, o: object) -> bool:
        if type(o) != Payload:
            return False

        return self.type == o.type and self.src == o.src and self.dst == o.dst and self.sent == o.sent and self.course_code == o.course_code

    def generate_dst_path(self, dst: Path) -> Path:
        for folder in Folder:
            if folder in self.src.name:
                self.type = folder.value
                return dst.joinpath(folder, self.src.name)
        return Path("error")

    def __repr__(self):
        return f"{self.src.name:<40} {Fore.YELLOW}{self.dst.parent.name:<40}{Fore.RESET}"

    __str__ = __repr__

    def name(self):
        return f"{self.src.name} [{self.dst.parent.name}]"

    def send(self, send_enabled=False, debug_mode=False) -> bool:
        """
        Sends a file from src to dst. Prints out certain results.
        Returns True on success, False otherwise.
        """

        def log(from_path, to_path, status_msg="", color=Fore.RESET):
            print(f"{color}From: {from_path}\n  To: {to_path} \n{status_msg}{Fore.RESET}\n")

        if not send_enabled:
            if debug_mode:
                log(self.src, self.dst, "Sending Not Enabled", Fore.YELLOW)
            return False

        try:
            if not self.src.exists():
                if debug_mode:
                    log(self.src, self.dst, "Src File Does Not Exist", Fore.YELLOW)
                return False

            if self.dst.exists():
                if debug_mode:
                    log(self.src, self.dst, "Dst File Already Exists", Fore.YELLOW)
                return False

            if not self.dst.parent.exists():
                if debug_mode:
                    log(self.src, pretty_substring(str(self.dst), self.dst.parent.name),
                        f"'{self.dst.parent.name}' Does Not Exist", Fore.YELLOW)
                if self.prompt_to_create_folder(self.dst.parent.name):
                    self.dst.parent.mkdir(parents=True, exist_ok=True)
                else:
                    return False

            self.src.rename(self.dst)
            if debug_mode:
                log(self.src, self.dst, "SUCCESS", Fore.GREEN)
            return True

        except FileNotFoundError as e:
            if debug_mode:
                log(self.src, self.dst, f"File Not Found: {e}", Fore.RED)
            return False

        except Exception as error:
            if debug_mode:
                print(Fore.RED + f"Unexpected Error: {error}" + Fore.RESET)
            return False

    def prompt_to_create_folder(self, folder_name: str):
        return inquirer.confirm(  # type: ignore
            message=f"Create {folder_name}? (y/n): ",
            default=False
        ).execute()

    def success(self):
        return f"{Fore.GREEN}☑ {self.name()}{Fore.RESET}"

    def error(self, msg="N/A"):
        return f"{Fore.RED}☒ {self.name()} ({msg}){Fore.RESET}"


class Selection(StrEnum):
    ALL = "ALL"


class CLIApp():
    def __init__(self):
        self.built_courses_dict: dict[str, Course] = {}
        self.courses_by_year: dict[str, list[Course]] = {}
        self.payloads_to_send: list[Payload] = []
        self.years: list[str] = []
        self.year_to_folder: dict[str, str] = self.load_year_to_folder()
        self.selected_years: list[int] = []
        self.selected_courses: list[Any] = []
        self.selected_payloads: list[Payload] = []

    def start(self):
        self.load_data()
        self.filter_years()
        self.filter_courses()
        self.filter_payloads()
        self.prompt_to_send_payloads()

    def load_year_to_folder(self):
        with open("year_to_folder.json", "r") as f:
            data = json.load(f)

        return data

    def get_choice_start(self):
        return Choice(Selection.ALL, "All",  enabled=False)  # type: ignore

    def traverse_folder(self, src_folder_path: Path, built_course_dict: dict) -> list[Payload]:
        files_to_be_sent: list[Payload] = []

        for file in src_folder_path.iterdir():

            for course_code in built_course_dict:
                if course_code not in file.name:
                    continue

                course: Course = built_course_dict[course_code]
                payload = Payload(file, course.dst_path, course_code, course)
                files_to_be_sent.append(payload)

        return files_to_be_sent

    def load_data(self):
        with open(COURSE_JSON, "r") as f:
            courses_json = json.load(f)
            for folder in BASE_DST_PATH.iterdir():
                self.years.append(folder.name)
                if folder.is_dir() and folder.name in courses_json:
                    for semester in courses_json[folder.name]:
                        if semester in courses_json[folder.name]:
                            for course_code, course_json in courses_json[folder.name][semester].items():
                                parent_path = folder.absolute().joinpath(semester)
                                c = Course(course_code, course_json, parent_path)
                                self.built_courses_dict[course_code] = c

                                alt_course_code = course_code[0:4] + " " + course_code[4:]
                                self.built_courses_dict[alt_course_code] = c

                                self.courses_by_year.setdefault(folder.name, []).append(c)

        self.payloads_to_send = self.traverse_folder(BASE_SRC_PATH, self.built_courses_dict)

    def build_output_files_string(self) -> str:
        last_course_code = None
        s = ""
        for payload in self.selected_payloads:
            if payload.course_code != last_course_code:
                last_course_code = payload.course_code
                s += f"\n{Fore.BLUE}{last_course_code}{Fore.RESET}"

            s += f"\n  {Fore.BLUE}❯{Fore.RESET} {payload}"

        return s + '\n'

    def filter_years(self):
        choices = [Choice(value, name) for name, value in self.year_to_folder.items()]

        self.selected_years = self.select_input("Filter by year: ", choices)

        self.filtered_courses: list[Course] = []
        for year, courses in self.courses_by_year.items():
            if year in self.selected_years:
                self.filtered_courses.extend(courses)

    def seperate_course_code(self, course_code: str):
        if " " in course_code:
            return course_code
        elif "_" in course_code:
            return course_code.replace("_", "")
        return course_code[0:4] + " " + course_code[4:]

    def filter_courses(self):
        if not self.filtered_courses:
            print("No courses in selected years\n")
            exit(0)
        choices = [Choice(course, self.seperate_course_code(course.course_code)) for course in self.filtered_courses]

        list_of_courses: list[Course] = self.select_input("Filter by Course", choices)
        self.selected_courses = [self.seperate_course_code(c.course_code) for c in list_of_courses]

    def filter_payloads(self):
        if not self.selected_courses:
            print("No selected courses")
            exit(0)

        print(f"{Fore.CYAN}Root: {BASE_SRC_PATH}{Fore.RESET}")

        choices = [Choice(payload, payload.src.name) for payload in self.payloads_to_send
                   if self.seperate_course_code(payload.course_code) in self.selected_courses]

        if not len(choices):
            print("No files match selected courses")
            exit(0)

        self.selected_payloads = self.select_input("Select files to send", choices)
        print(self.build_output_files_string())

    def select_input(self, prompt: str, choices: list[Choice]):
        choices.insert(0, self.get_choice_start())

        p = inquirer.checkbox(  # type: ignore
            message=prompt,
            choices=choices,
            instruction="(Use <space> to select, <enter> to confirm)",

            cycle=False,
            show_cursor=False,
            filter=lambda result: choices if "All" in result else result,
            transformer=lambda result: "All" if Selection.ALL in result else ", ".join(str(r) for r in result)
        )

        result = p.execute()

        # If "All" is selected, return all actual values (exclude All itself)
        if Selection.ALL in result:
            return [c.value for c in choices if c.value != Selection.ALL]

        # Otherwise, just return the selected values
        return result

    def prompt_to_send_payloads(self):
        if not self.selected_payloads:
            print("No payloads selected")
            exit(0)

        send = inquirer.confirm(  # type: ignore
            message="Send Payloads:",
            default=False
        ).execute()

        if send:
            self.send_payloads()
        else:
            print("Exiting Program...")

    def send_payloads(self):
        to_delete: list = []
        for payload in self.selected_payloads:
            try:
                if payload.send(send_enabled=True):  # send file
                    to_delete.append(payload)
                    print(payload.success())
                else:
                    print(payload.error())
            except Exception as e:
                print(f"ERROR: {e}")
                continue


def main():
    app = CLIApp()
    app.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:  # type: ignore
        print(Fore.RESET)
