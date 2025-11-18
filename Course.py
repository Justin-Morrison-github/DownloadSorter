from pathlib import Path
from typing import Any


class Course():
    def __init__(self, course_code: str, course_json: dict[str, Any], parent_path: Path):
        self.name = course_json["name"]
        self.section = course_json["section"]
        self.crn = course_json["crn"]
        self.folders = course_json["folders"]
        self.course_code = course_code
        self.course_json = course_json
        self.dst_path = parent_path.joinpath(self.name)

    def __str__(self):
        return f"{self.course_code}"

    def __repr__(self):
        return f"{self.course_code}"
