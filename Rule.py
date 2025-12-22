from Keywords import *
import re

PLACEHOLDER_RE = re.compile(r"<([A-Z_]+)>")


class Rule:

    tag: str
    path: str
    aliases: list[str]
    children: list["Rule"]
    parent: "Rule | None"

    def __init__(self, name, tag, path, aliases: list[str], parent=None):
        self.name: str = name
        self.tag_template: str = tag
        self.path: str = path
        self.aliases: list[str] = aliases
        self.children: list[Rule] = []
        self.parent: Rule | None = parent
        self.case_sensitive = False
        self.tag_templates = [self.tag_template] + (self.aliases or [])
        self.patterns: list[re.Pattern] = []
        self.captures: dict[str, str] = {}

    def tag_templates_to_regex(self, templates: list[str]):
        """
        Converts a tag template like:
        'Assignment <N>' → r'Assignment\s+(\d+)'
        """
        flags = 0 if self.case_sensitive else re.IGNORECASE
        patterns = []
        for template in templates:
            # Escape regex characters except our placeholders
            escaped = re.escape(template)

            # Replace escaped placeholder with capture group
            escaped = escaped.replace(r"<N>", r"(\d+)")

            # Allow flexible whitespace
            escaped = escaped.replace(r'\ ', r'\s+')
            patterns.append(re.compile(escaped, flags))

        return patterns

    def add_child(self, rule: "Rule"):
        self.children.append(rule)

    def __str__(self) -> str:
        parent_str = f'"{self.parent.tag_template}"' if self.parent else None
        return f"Rule[{self.name}|{self.tag_template}](\n\tpath={self.path}, \n\taliases={self.aliases}, \n\tparent={parent_str}, \n\tchildren={[child.tag for child in self.children]}, \n)"

    __repr__ = __str__

    def resolve_template(self, template: str) -> str:

        def repl(match: re.Match[str]) -> str:
            key = match.group(1)
            return self.captures.get(key, match.group(0))

        return PLACEHOLDER_RE.sub(repl, template)

    def resolve_structural_placeholders(self) -> str:
        # Start with own path
        path = self.path

        # Recursively resolve parent placeholders
        if self.parent:
            parent_resolved = self.parent.resolve_structural_placeholders()
            path = path.replace(PARENT_PATH, parent_resolved)
            path = path.replace(PARENT_TAG, self.parent.tag_template)

        # Replace own tag placeholder
        path = path.replace(SELF_TAG, self.tag_template)

        return path

    def matches(self, file: str) -> bool:
        # Resolve structural placeholders just-in-time
        resolved_templates = []
        for template in self.tag_templates:
            t = template
            if self.parent:
                t = t.replace(PARENT_TAG, self.parent.tag_template)
            t = t.replace(SELF_TAG, self.tag_template)
            resolved_templates.append(t)

        # Compile regexes from resolved templates
        patterns = self.tag_templates_to_regex(resolved_templates)

        for pattern, template in zip(patterns, resolved_templates):
            match = pattern.search(file)
            if match:
                placeholders = PLACEHOLDER_RE.findall(template)
                for key, value in zip(placeholders, match.groups()):
                    self.captures[key] = value
                return True

        return False

    def get_path(self, file: str) -> str | None:

        if not self.matches(file):
            return None

        for child in self.children:
            child.captures = {**self.captures}
            child_path = child.get_path(file)
            if child_path is not None:
                self.captures.update(child.captures)
                return child_path   # deeper match found

        resolved_path = self.resolve_structural_placeholders()
        resolved_path = self.resolve_template(resolved_path)

        print("CAPTURES:", self.captures)
        print("PATH TEMPLATE:", self.path)
        print(resolved_path)
        return resolved_path
