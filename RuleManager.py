from Rule import Rule


class RuleManager:
    rules: list[Rule]

    def __init__(self) -> None:
        self.rules = []

    def add(self, rule: Rule):
        self.rules.append(rule)

    def get_path(self, file: str) -> str | None:
        best = None
        for rule in self.rules:
            path = rule.get_path(file)
            if path is not None:
                best = path
        return best
