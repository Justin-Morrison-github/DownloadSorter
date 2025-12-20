import json
from re import A

from Rule import Rule
from Keywords import *
from RuleManager import RuleManager


class RuleParser:
    filepath: str

    def __init__(self, filepath) -> None:
        self.filepath = filepath

    def parse(self) -> RuleManager:
        rule_manager = RuleManager()

        with open(self.filepath) as f:
            data = json.load(f)
            rules = data[RULES]
            for name in rules:
                rule_json = rules[name]
                rule: Rule = self._parse_rule(None, rule_json, name)
                rule_manager.add(rule)

        return rule_manager

    def _parse_rule(self, parent: Rule | None, rule_json: dict, name: str) -> Rule:
        tag = rule_json.get(TAG, "")
        aliases = rule_json.get(ALIASES)
        path: str = rule_json.get(PATH, "")
        method: str = rule_json.get(METHOD, "")
        type: str = rule_json.get(TYPE, "")
        rule = Rule(name, tag, type, path, aliases, method, parent=parent)
        rule.resolve_path()

        children = rule_json.get(CHILD_RULES)
        if children is not None:
            for child_name in children:
                rule.add_child(self._parse_rule(rule, children[child_name], child_name))

        return rule
