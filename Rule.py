from pathlib import Path
from Keywords import *
import re


class Rule:

    tag: str
    path: str
    aliases: list[str]
    children: list["Rule"]
    parent: "Rule | None"

    def __init__(self, name, tag, type, path, aliases, method, parent=None):
        self.name = name
        self.tag = tag
        self.type = type
        self.path = path
        self.aliases = aliases
        self.children = []
        self.parent = parent
        self.method = method

    def add_child(self, rule: "Rule"):
        self.children.append(rule)

    def __str__(self) -> str:
        parent_str = f'"{self.parent.tag}"' if self.parent else None
        return f"Rule[{self.name}|{self.tag}](\n\tpath={self.path}, \n\taliases={self.aliases}, \n\tparent={parent_str}, \n\tchildren={[child.tag for child in self.children]}, \n)"

    __repr__ = __str__

    def resolve_path(self) -> None:
        if self.path == "":
            return

        if PARENT_PATH in self.path:
            if self.parent == None:
                self.path = self.path.replace(PARENT_PATH, "")
            else:
                self.path = self.path.replace(PARENT_PATH,  self.parent.path)

        if SELF_TAG in self.path:
            self.path = self.path.replace(SELF_TAG, self.tag)

    def _apply_method(self):
        print(self.method)

    def apply(self, file: str):

        if self.type == REGEX:
            if self.parent is None:
                print("Parent is None")
            else:
                pattern = re.compile(
                    fr'^.*{re.escape(self.parent.tag)} \d+.*$'
                )
                print(pattern)
                print(file)
                print(bool(pattern.fullmatch(file)))

        if self.tag in file:

            if self.method:
                self._apply_method()

            print(self.path)
            for child_rule in self.children:
                child_rule.apply(file)
            return self.path
