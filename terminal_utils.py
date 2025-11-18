from colorama import Fore


def user_choice_bool(prompt: str) -> bool:
    """
    Prompts the user if they want to prompt. Accepts Y/y or N/n
    """
    while True:
        try:
            choice = input(f"\n{prompt}").strip().lower()

            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("Invalid Input")

        except KeyboardInterrupt:
            raise KeyboardInterrupt


def pretty_substring(str: str, substr: str, start: str = "", end="", color_a=Fore.RED, color_b=Fore.YELLOW):
    str_len = len(str)
    substr_len = len(substr)

    index = str.lower().find(substr.lower())

    string = color_a + start + str[0: index] + color_b + str[index: index +
                                                             substr_len] + color_a + str[index + substr_len: str_len] + end + Fore.RESET
    return string
