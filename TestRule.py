import unittest

from Rule import Rule
from RuleManager import RuleManager
from RuleParser import RuleParser


class TestRule(unittest.TestCase):
    def test_rule_init(self):
        rule: Rule = Rule("name", "tag", "./path", ["alias1", "alias2"], None)
        self.assertEqual("name", rule.name)
        self.assertEqual("tag", rule.tag_template)
        # self.assertEqual("type", rule.type)
        self.assertEqual("./path", rule.path)
        self.assertEqual(["alias1", "alias2"], rule.aliases)
        self.assertEqual(None, rule.parent)

    def test_rule_parse(self):
        parser: RuleParser = RuleParser("test_rules.json")
        ruleManager: RuleManager = parser.parse()
        self.assertEqual(len(ruleManager.rules), 1)

        rule: Rule = ruleManager.rules[0]
        self.assertEqual(len(rule.children), 1)
        self.assertEqual(rule.tag_template, "SYSC 2004")
        self.assertEqual(rule.path, "./path")
        self.assertEqual(rule.parent, None)
        self.assertEqual(rule.aliases, ["SYSC2004", "SYSC_2004"])

    def test_get_path(self):
        parser: RuleParser = RuleParser("test_rules.json")
        ruleManager: RuleManager = parser.parse()

        fileA = "SYSC 2004 Assignment 1.pdf"
        fileB = "SYSC_2004 Assignment 1.pdf"
        fileC = "SYSC2004 Assignment 1.pdf"

        self.assertEqual(ruleManager.get_path(fileA), "./path/Assignment/Assignment 1")
        self.assertEqual(ruleManager.get_path(fileB), "./path/Assignment/Assignment 1")
        self.assertEqual(ruleManager.get_path(fileC), "./path/Assignment/Assignment 1")


if __name__ == "__main__":
    unittest.main()
