from Rule import Rule


class RuleManager:
    rules: list[Rule]

    def __init__(self) -> None:
        self.rules = []

    def add(self, rule: Rule):
        self.rules.append(rule)

    def apply(self, file: str):
        for rule in self.rules:
            rule.apply(file)
