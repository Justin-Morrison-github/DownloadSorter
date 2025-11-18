import customtkinter as ctk
import json

from typing import TypedDict
from pathlib import Path
from colorama import Fore
from tkinter import Variable
from Course import Course
from enum import StrEnum
from math import e
from colorama import Fore
from terminal_utils import pretty_substring, user_choice_bool


class Folder(StrEnum):
    LAB = "Lab"
    ASSIGNMENT = "Assignment"
    REVIEW = "Review"
    LECTURE = "Lecture"
    TUTORIAL = "Tutorial"
    INFO = "Info"
    OTHER = "Other"


class Payload():
    def __init__(self, src: Path, dst: Path):
        self.src = src
        self.dst = self.generate_dst_path(dst)
        self.sent = False
        self.staged = False
        self.checkbox = None

    def to_tuple(self):
        return (self.checkbox, self.src, self.dst)

    def setCheckbox(self, checkbox: ctk.CTkCheckBox):
        self.checkbox = checkbox

    def toggle_staged(self):
        self.staged = not self.staged

    def set_staged(self, staged: bool):
        self.staged = staged

    def generate_dst_path(self, dst: Path):
        sub_folder = ""

        for folder in Folder:
            if folder in self.src.name:
                sub_folder = folder
                break

        return dst.joinpath(sub_folder, self.src.name)

    def __repr__(self):
        data = {
            'staged': {self.staged},
            'sent': {self.sent},
            'src': {self.src.name},
            'dst': {self.dst.parent.name},
        }
        return f"{data}"

    __str__ = __repr__

    def send(self, send_enabled=False) -> bool:
        """
        Sends a file from src to dst. Prints out certain results.
        Returns True on success, False otherwise.
        """

        def log(from_path, to_path, status_msg="", color=Fore.RESET):
            print(f"{color}From: {from_path}\n  To: {to_path} \n{status_msg}{Fore.RESET}\n")

        if not send_enabled:
            log(self.src, self.dst, "Sending Not Enabled", Fore.YELLOW)
            return False

        try:

            if not self.src.exists():
                log(self.src, self.dst, "Src File Does Not Exist", Fore.YELLOW)
                return False

            if self.dst.exists():
                log(self.src, self.dst, "Dst File Already Exists", Fore.YELLOW)
                return False

            if not self.dst.parent.exists():
                log(self.src, pretty_substring(str(self.dst), self.dst.parent.name),
                    f"'{self.dst.parent.name}' Does Not Exist", Fore.YELLOW)
                if self.prompt_to_create_folder(self.dst.parent.name):
                    self.dst.parent.mkdir(parents=True, exist_ok=True)
                else:
                    return False

            self.src.rename(self.dst)
            log(self.src, self.dst, "SUCCESS", Fore.GREEN)
            return True

        except FileNotFoundError as e:
            log(self.src, self.dst, f"File Not Found: {e}", Fore.RED)
            return False

        except Exception as error:
            print(Fore.RED + f"Unexpected Error: {error}" + Fore.RESET)
            return False

    def prompt_to_create_folder(self, folder_name: str):
        return user_choice_bool(f"Create {folder_name}? (y/n): ")


# Set appearance and theme
ctk.set_appearance_mode("dark")   # "light" or "dark"
ctk.set_default_color_theme("blue")  # themes: "blue", "green", "dark-blue"

BASE_DST_PATH = Path("C:/Users/morri/Onedrive/University")
BASE_SRC_PATH = Path("C:/Users/morri/Downloads")
COURSE_JSON = "./courses.json"


class FileRow(TypedDict):
    payload: Payload
    var: Variable
    checkbox: ctk.CTkCheckBox
    src_frame: ctk.CTkFrame
    dst_frame: ctk.CTkFrame


def traverse_folder(src_folder_path: Path, built_course_dict: dict) -> list[Payload]:
    files_to_be_sent: list[Payload] = []

    for file in src_folder_path.iterdir():

        if file.is_dir():
            files_to_be_sent += traverse_folder(file, built_course_dict)
        else:
            for course_code in built_course_dict:
                if course_code in file.name:
                    course: Course = built_course_dict[course_code]
                    payload = Payload(file, course.dst_path)
                    files_to_be_sent.append(payload)

    return files_to_be_sent


class GUIApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        with open(COURSE_JSON, "r") as f:
            self.courses_json = json.load(f)
        self.built_courses_dict = {}
        self.payloads_to_send = []

        self.load_data()

        self.geometry("1000x600")

        self.header = ctk.CTkFrame(self, height=100)
        self.header.pack(fill="x", padx=10, pady=10)
        header_buttons = [
            {"text": "Reload", "command": self.load_data},
        ]
        for col, button in enumerate(header_buttons):
            button = ctk.CTkButton(
                self.header,
                text=button.get("text", "Error"),
                command=button.get("command", "Error"),
            )
            button.pack(anchor="e")

        # Scrollable frame for rows
        self.table = ctk.CTkScrollableFrame(self)
        self.table.grid_columnconfigure(0, weight=1)   # checkbox col
        self.table.grid_columnconfigure(1, weight=9)               # source col
        self.table.grid_columnconfigure(2, weight=9)               # dest col
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        self.is_selecting_all = False

        control_bar_buttons = [
            {"text": "Select All", "command": self.select_all},
            {"text": f"Filter Source ({BASE_SRC_PATH})", "command": self.filter_src},
            {"text": f"Filter Destination ({BASE_DST_PATH})", "command": self.filter_dst},
            {"text": "Send", "command": self.send_payloads},
        ]

        for col, button in enumerate(control_bar_buttons):
            button = ctk.CTkButton(
                self.table,
                text=button.get("text", "Error"),
                command=button.get("command", "Error"),
            )
            button.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")

        # Store checkboxes
        self.checkbox_vars = []

        self.rows: list[FileRow] = []  # list of dicts with widgets per row

        # Add rows
        for row, payload in enumerate(self.payloads_to_send, start=1):
            var = ctk.BooleanVar(value=payload.staged)

            def on_toggle(v=var, p=payload):
                p.staged = v.get()  # update payload
                print(f"{p}")

            cb = ctk.CTkCheckBox(
                self.table,
                text="",
                variable=var,
                command=on_toggle
            )
            cb.grid(row=row, column=0, padx=5, pady=5)

            # Source subframe
            src_frame = ctk.CTkFrame(self.table)
            src_frame.grid(row=row, column=1, sticky="nsew", padx=5, pady=5)
            src_frame.grid_columnconfigure(0, weight=1)  # allows internal widgets to expand

            src_label = ctk.CTkLabel(
                src_frame,
                text=self.truncate_text(str(payload.src.relative_to(BASE_SRC_PATH)), 50),
                anchor="w",
            )
            src_label.pack(fill="both", expand=True)

            # Destination subframe
            dst_frame = ctk.CTkFrame(self.table)
            dst_frame.grid(row=row, column=2, sticky="nsew", padx=5, pady=5)
            dst_frame.grid_columnconfigure(0, weight=1)

            dst_label = ctk.CTkLabel(
                dst_frame,
                text=self.truncate_text(str(payload.dst.relative_to(BASE_DST_PATH)), 50),
                anchor="w",
            )
            dst_label.pack(fill="both", expand=True)

            # Store var reference so select all can easily iterate through
            self.checkbox_vars.append(var)

            # Store row widgets for easy deletion later
            self.rows.append({
                "payload": payload,
                "var": var,
                "checkbox": cb,
                "src_frame": src_frame,
                "dst_frame": dst_frame
            })

    def start(self):
        self.mainloop()

    def load_data(self):
        built_course_dict: dict[str, Course] = {}

        for folder in BASE_DST_PATH.iterdir():
            if folder.is_dir() and folder.name in self.courses_json:
                for semester in self.courses_json[folder.name]:
                    if semester in self.courses_json[folder.name]:
                        for course_code, course_json in self.courses_json[folder.name][semester].items():
                            parent_path = folder.absolute().joinpath(semester)
                            c = Course(course_code, course_json, parent_path)
                            built_course_dict[course_code] = c

                            alt_course_code = course_code[0:4] + " " + course_code[4:]
                            built_course_dict[alt_course_code] = c

        self.payloads_to_send = traverse_folder(BASE_SRC_PATH, built_course_dict)

    def filter_src(self):
        print("Filter src")

    def filter_dst(self):
        print("Filter dst")

    def select_all(self):
        self.is_selecting_all = not self.is_selecting_all  # If already on, turn off and vice versa
        for var, payload in zip(self.checkbox_vars, self.payloads_to_send):

            var.set(self.is_selecting_all)
            payload.staged = self.is_selecting_all
            print(f"{payload} staged → {payload.staged}")

    def truncate_text(self, text, max_chars=30):
        return text if len(text) <= max_chars else text[:max_chars-3] + "..."

    def send_payloads(self):
        to_delete: list[FileRow] = []
        for row in self.rows:
            payload: Payload = row["payload"]
            if payload.staged:
                try:
                    if payload.send(send_enabled=True):  # send file
                        # Cleanup on success
                        to_delete.append(row)
                    else:
                        print("Error during send()")
                except Exception as e:
                    print(f"ERROR: {e}")
                    continue

        # Can't delete while iterating, so must use auxilary list
        for row in to_delete:
            row["checkbox"].destroy()
            row["src_frame"].destroy()
            row["dst_frame"].destroy()
            self.rows.remove(row)
            self.checkbox_vars.remove(row["var"])
            self.payloads_to_send.remove(row["payload"])


def main():
    app = GUIApp()
    app.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:  # type: ignore
        print(Fore.RESET)
