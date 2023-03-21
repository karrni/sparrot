from colorama import Fore

from sparrot.logger import Logger

logger = Logger()


def color_number(num: int) -> str:
    if num <= 10:
        return f"{Fore.RED}{num}{Fore.RESET}"
    elif num <= 100:
        return f"{Fore.YELLOW}{num}{Fore.RESET}"
    else:
        return f"{Fore.GREEN}{num}{Fore.RESET}"
