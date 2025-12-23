import unittest

from Rule import Rule
from RuleManager import RuleManager
from RuleParser import RuleParser


class TestRule(unittest.TestCase):
    def test_rule_init(self):
        rule: Rule = Rule("name", "tag", "./path", ["alias1", "alias2"], None)
        self.assertEqual("name", rule.name)
        self.assertEqual("tag", rule.tag_template)
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

    def test_get_path_with_space(self):
        parser: RuleParser = RuleParser("test_rules.json")
        ruleManager: RuleManager = parser.parse()

        file = "SYSC 2004 Assignment 1.pdf"

        self.assertEqual(ruleManager.get_path(file), "./path/Assignment/Assignment 1")

    def test_get_path_with_underscore(self):
        parser: RuleParser = RuleParser("test_rules.json")
        ruleManager: RuleManager = parser.parse()

        file = "SYSC_2004 Assignment 1.pdf"

        self.assertEqual(ruleManager.get_path(file), "./path/Assignment/Assignment 1")

    def test_get_path_with_no_space(self):
        parser: RuleParser = RuleParser("test_rules.json")
        ruleManager: RuleManager = parser.parse()

        file = "SYSC2004 Assignment 1.pdf"

        self.assertEqual(ruleManager.get_path(file), "./path/Assignment/Assignment 1")

    def test_resolve_self_tag(self):
        parent = Rule("parent", "SYSC 2004", "./path", [])
        child = Rule("child", "Lab", "$PARENT_PATH/$TAG/test", [], parent=parent)
        parent.add_child(child)
        ruleManager: RuleManager = RuleManager()
        ruleManager.add(parent)
        file = "SYSC 2004 Lab 1.pdf"
        self.assertEqual(ruleManager.get_path(file), "./path/Lab/test")

    def test_resolve_parent_tag(self):
        parent = Rule("parent", "SYSC 2004", "./path", [])
        child = Rule("child", "Lab", "$PARENT_PATH/$PARENT_TAG/test", [], parent=parent)
        parent.add_child(child)
        ruleManager: RuleManager = RuleManager()
        ruleManager.add(parent)
        file = "SYSC 2004 Lab 1.pdf"
        self.assertEqual(ruleManager.get_path(file), "./path/SYSC 2004/test")

    def test_resolve_parent_path(self):
        parent = Rule("parent", "SYSC 2004", "./path", [])
        child = Rule("child", "Lab", "$PARENT_PATH/test", [], parent=parent)
        parent.add_child(child)
        ruleManager: RuleManager = RuleManager()
        ruleManager.add(parent)
        file = "SYSC 2004 Lab 1.pdf"
        self.assertEqual(ruleManager.get_path(file), "./path/test")


class TestRulesJSON2(unittest.TestCase):
    def test_rule_parse(self):
        parser: RuleParser = RuleParser("test_rules2.json")
        ruleManager: RuleManager = parser.parse()
        self.assertEqual(len(ruleManager.rules), 2)

        programming_rule: Rule = ruleManager.rules[0]
        self.assertEqual(len(programming_rule.children), 2)
        self.assertEqual(programming_rule.tag_template, "SYSC 2004")
        self.assertEqual(programming_rule.tag_template, "SYSC 2004")
        self.assertEqual(programming_rule.path, "./Programming")
        self.assertEqual(programming_rule.name, "Programming")
        self.assertEqual(programming_rule.parent, None)
        self.assertEqual(programming_rule.case_sensitive, False)
        self.assertEqual(programming_rule.aliases, ["SYSC2004", "SYSC_2004"])

        programming_assignment_rule: Rule = programming_rule.children[0]
        self.assertEqual(programming_assignment_rule.name, "Assignments")
        self.assertEqual(len(programming_assignment_rule.children), 1)
        self.assertEqual(programming_assignment_rule.tag_template, "Assignment")
        self.assertEqual(programming_assignment_rule.path, "$PARENT_PATH/$TAG")
        self.assertEqual(programming_assignment_rule.parent, programming_rule)
        self.assertEqual(programming_assignment_rule.case_sensitive, False)
        self.assertEqual(programming_assignment_rule.aliases, [])

        programming_assignment_number_rule: Rule = programming_assignment_rule.children[0]
        self.assertEqual(programming_assignment_number_rule.name, "Assignment Numbers")
        self.assertEqual(len(programming_assignment_number_rule.children), 0)
        self.assertEqual(programming_assignment_number_rule.tag_template, "$PARENT_TAG <N>")
        self.assertEqual(programming_assignment_number_rule.path, "$PARENT_PATH/$PARENT_TAG <N>")
        self.assertEqual(programming_assignment_number_rule.parent, programming_assignment_rule)
        self.assertEqual(programming_assignment_number_rule.case_sensitive, False)
        self.assertEqual(programming_assignment_number_rule.aliases, [])

        programming_lab_rule: Rule = programming_rule.children[1]
        self.assertEqual(len(programming_lab_rule.children), 1)
        self.assertEqual(programming_lab_rule.tag_template, "Lab")
        self.assertEqual(programming_lab_rule.name, "Lab Files")
        self.assertEqual(programming_lab_rule.path, "$PARENT_PATH/$TAG")
        self.assertEqual(programming_lab_rule.parent, programming_rule)
        self.assertEqual(programming_lab_rule.case_sensitive, False)
        self.assertEqual(programming_lab_rule.aliases, [])

        programming_lab_number_rule: Rule = programming_lab_rule.children[0]
        self.assertEqual(len(programming_lab_number_rule.children), 0)
        self.assertEqual(programming_lab_number_rule.name, "Lab Number")
        self.assertEqual(programming_lab_number_rule.tag_template, "$PARENT_TAG <N>")
        self.assertEqual(programming_lab_number_rule.path, "$PARENT_PATH/$PARENT_TAG <N>")
        self.assertEqual(programming_lab_number_rule.parent, programming_lab_rule)
        self.assertEqual(programming_lab_number_rule.case_sensitive, False)
        self.assertEqual(programming_lab_number_rule.aliases, [])

        math_rule: Rule = ruleManager.rules[1]
        self.assertEqual(len(math_rule.children), 2)
        self.assertEqual(math_rule.tag_template, "MATH_1005")
        self.assertEqual(math_rule.path, "./Math")
        self.assertEqual(math_rule.parent, None)
        self.assertEqual(programming_rule.case_sensitive, False)
        self.assertEqual(math_rule.aliases, [])

        math_test_rule: Rule = math_rule.children[0]
        self.assertEqual(len(math_test_rule.children), 1)
        self.assertEqual(math_test_rule.tag_template, "Test")
        self.assertEqual(math_test_rule.path, "$PARENT_PATH/$TAG")
        self.assertEqual(math_test_rule.parent, math_rule)
        self.assertEqual(math_test_rule.case_sensitive, False)
        self.assertEqual(math_test_rule.aliases, [])

    def test_rule_apply_sysc_2004_assignments(self):
        parser: RuleParser = RuleParser("test_rules2.json")
        ruleManager: RuleManager = parser.parse()

        file1 = "SYSC 2004 Assignment Grading Scheme.pdf"
        file2 = "SYSC 2004 Assignment 1.pdf"
        file3 = "SYSC 2004 Assignment 3 Grading Scheme.pdf"
        file4 = "SYSC 2004 3 Assignment Grading Scheme.pdf"

        self.assertEqual(ruleManager.get_path(file1), "./Programming/Assignment")
        self.assertEqual(ruleManager.get_path(file2), "./Programming/Assignment/Assignment 1")
        self.assertEqual(ruleManager.get_path(file3), "./Programming/Assignment/Assignment 3")
        self.assertEqual(ruleManager.get_path(file4), "./Programming/Assignment")

    def test_rule_apply_sysc_2004_labs(self):
        parser: RuleParser = RuleParser("test_rules2.json")
        ruleManager: RuleManager = parser.parse()

        file1 = "SYSC 2004 Lab Grading Scheme.pdf"
        file2 = "SYSC 2004 Lab 1.pdf"
        file3 = "SYSC 2004 Lab 3 Grading Scheme.pdf"
        file4 = "SYSC 2004 3 Lab Grading Scheme.pdf"

        self.assertEqual(ruleManager.get_path(file1), "./Programming/Lab")
        self.assertEqual(ruleManager.get_path(file2), "./Programming/Lab/Lab 1")
        self.assertEqual(ruleManager.get_path(file3), "./Programming/Lab/Lab 3")
        self.assertEqual(ruleManager.get_path(file4), "./Programming/Lab")

    def test_rule_apply_sysc_2004_aliases_labs(self):
        parser: RuleParser = RuleParser("test_rules2.json")
        ruleManager: RuleManager = parser.parse()

        file1 = "SYSC_2004 Lab Grading Scheme.pdf"
        file2 = "SYSC_2004 Lab 1.pdf"
        file3 = "SYSC_2004 Lab 3 Grading Scheme.pdf"
        file4 = "SYSC_2004 3 Lab Grading Scheme.pdf"

        self.assertEqual(ruleManager.get_path(file1), "./Programming/Lab")
        self.assertEqual(ruleManager.get_path(file2), "./Programming/Lab/Lab 1")
        self.assertEqual(ruleManager.get_path(file3), "./Programming/Lab/Lab 3")
        self.assertEqual(ruleManager.get_path(file4), "./Programming/Lab")

        file1 = "SYSC2004 Lab Grading Scheme.pdf"
        file2 = "SYSC2004 Lab 1.pdf"
        file3 = "SYSC2004 Lab 3 Grading Scheme.pdf"
        file4 = "SYSC2004 3 Lab Grading Scheme.pdf"

        self.assertEqual(ruleManager.get_path(file1), "./Programming/Lab")
        self.assertEqual(ruleManager.get_path(file2), "./Programming/Lab/Lab 1")
        self.assertEqual(ruleManager.get_path(file3), "./Programming/Lab/Lab 3")
        self.assertEqual(ruleManager.get_path(file4), "./Programming/Lab")

    def test_rule_apply_MATH_1005_tests(self):
        parser: RuleParser = RuleParser("test_rules2.json")
        ruleManager: RuleManager = parser.parse()

        file1 = "MATH_1005 Test Grading Scheme.pdf"
        file2 = "MATH_1005 Test 1.pdf"
        file3 = "MATH_1005 Test 3 Grading Scheme.pdf"
        file4 = "MATH_1005 3 Test Grading Scheme.pdf"

        self.assertEqual(ruleManager.get_path(file1), "./Math/Test")
        self.assertEqual(ruleManager.get_path(file2), "./Math/Test/Test 1")
        self.assertEqual(ruleManager.get_path(file3), "./Math/Test/Test 3")
        self.assertEqual(ruleManager.get_path(file4), "./Math/Test")

    def test_rule_apply_sysc_2004_aliases_tests(self):
        parser: RuleParser = RuleParser("test_rules2.json")
        ruleManager: RuleManager = parser.parse()

        # With underscore
        file1 = "SYSC_2004 Assignment Grading Scheme.pdf"
        file2 = "SYSC_2004 Assignment 1.pdf"
        file3 = "SYSC_2004 Assignment 3 Grading Scheme.pdf"
        file4 = "SYSC_2004 3 Assignment Grading Scheme.pdf"

        self.assertEqual(ruleManager.get_path(file1), "./Programming/Assignment")
        self.assertEqual(ruleManager.get_path(file2), "./Programming/Assignment/Assignment 1")
        self.assertEqual(ruleManager.get_path(file3), "./Programming/Assignment/Assignment 3")
        self.assertEqual(ruleManager.get_path(file4), "./Programming/Assignment")

        # With no space
        file1 = "SYSC2004 Assignment Grading Scheme.pdf"
        file2 = "SYSC2004 Assignment 1.pdf"
        file3 = "SYSC2004 Assignment 3 Grading Scheme.pdf"
        file4 = "SYSC2004 3 Assignment Grading Scheme.pdf"

        self.assertEqual(ruleManager.get_path(file1), "./Programming/Assignment")
        self.assertEqual(ruleManager.get_path(file2), "./Programming/Assignment/Assignment 1")
        self.assertEqual(ruleManager.get_path(file3), "./Programming/Assignment/Assignment 3")
        self.assertEqual(ruleManager.get_path(file4), "./Programming/Assignment")

    def test_rule_apply_MATH_1005_review(self):
        parser: RuleParser = RuleParser("test_rules2.json")
        ruleManager: RuleManager = parser.parse()

        file1 = "MATH_1005 REVIEW doc.pdf"
        file2 = "MATH_1005 Review doc.pdf"
        file3 = "MATH_1005 review doc.pdf"
        file4 = "MATH_1005 REVIEW Lecture 2.pdf"
        file5 = "MATH_1005 Review Lecture 2.pdf"
        file6 = "MATH_1005 review Lecture 2.pdf"

        self.assertEqual(ruleManager.get_path(file1), "./Math/REVIEW")
        self.assertEqual(ruleManager.get_path(file2), "./Math/REVIEW")
        self.assertEqual(ruleManager.get_path(file3), "./Math/REVIEW")
        self.assertEqual(ruleManager.get_path(file4), "./Math/REVIEW")
        self.assertEqual(ruleManager.get_path(file5), "./Math/REVIEW")
        self.assertEqual(ruleManager.get_path(file6), "./Math/REVIEW")


if __name__ == "__main__":
    unittest.main()
