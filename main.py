# import sys
# from enum import StrEnum, auto
# from cli import CLIApp
# from gui import GUIApp

# EXPECTED_NUM_ARGS = 2

# if len(sys.argv) != 2:
#     print(f"Error: expected {EXPECTED_NUM_ARGS} arguements, received {len(sys.argv)}")
#     print("Usage: <tool_name> <option>\n")
#     exit(1)


# if (sys.argv[1] not in ["--gui", "--cli", "-g", "-c"]):
#     print(f"Error: expected {EXPECTED_NUM_ARGS} arguements, received {len(sys.argv)}")
#     print("Usage: <tool_name> <option>")
#     print("\t<option>: \"--gui\" or \"--cli\"")
#     exit(1)


# class Command(StrEnum):
#     GUI = auto()
#     CLI = auto()
#     INVALID = auto()

#     @staticmethod
#     def from_string(string: str):
#         if (string == "--gui" or string == "-g"):
#             return Command.GUI
#         elif (string == "--cli" or string == "-c"):
#             return Command.CLI
#         return Command.INVALID


# command: Command = Command.from_string(sys.argv[1])
# print(command)

# if (command == Command.CLI):
#     app = CLIApp()
# elif (command == Command.GUI):
#     app = GUIApp()
# else:
#     app = None
#     print(f"Error: Invalid Command")
#     exit(1)

# if (app):
#     app.start()

from RuleParser import RuleParser
from RuleManager import RuleManager

fileA = "SYSC 2004 Assignment 1.pdf"
fileB = "SYSC_2004 Assignment 1.pdf"
fileC = "SYSC2004 Assignment 1.pdf"

parser = RuleParser("test_rules.json")


rule_manager: RuleManager = parser.parse()
rule_manager.get_path(fileB)
