import sys

import requests
from colorama import Fore

from sparrot.logger import Logger

logger = Logger()


class WhoxyAPI:
    def __init__(self, url, api_key):
        self.url = url
        self.params = {"key": api_key}
        self.balance()

    def request(self, params: dict):
        params = self.params | params
        response = requests.get(self.url, params)

        data = response.json()
        # logger.debug(data)

        # status = 0 indicates an error
        if data["status"] == 0:
            logger.error(data["status_reason"])
            sys.exit(1)

        return data

    def balance(self):
        """Return the account balance."""

        def _color(num):
            n = int(num)
            if num <= 10:
                return f"{Fore.RED}{n}{Fore.RESET}"
            elif num <= 100:
                return f"{Fore.YELLOW}{n}{Fore.RESET}"
            else:
                return f"{Fore.GREEN}{n}{Fore.RESET}"

        logger.debug("Requesting account balance")
        data = self.request({"account": "balance"})

        _live = _color(data["live_whois_balance"])
        _history = _color(data["whois_history_balance"])
        _reverse = _color(data["reverse_whois_balance"])

        logger.info(f"Balance: Live {_live}, History {_history}, Reverse {_reverse}")

    def whois(self, domain):
        logger.debug(f"Requesting Whois data for {domain}")
        return self.request({"whois": domain})

    def whois_history(self, domain):
        logger.debug(f"Requesting historical Whois data for {domain}")
        return self.request({"history": domain})

    def _reverse_whois(self, **params):
        params["reverse"] = "whois"
        # params["mode"] = "mini"
        data = self.request(params)

        total_pages = data["total_pages"]

        # Inform the user if the lookup would result in a lot of queries
        if total_pages > 5:
            decision = logger.ask(f"The current lookup would result in {total_pages-1} API queries, continue?")
            if not decision:
                return data

        # Iterate over all pages and combine data
        for i in range(2, total_pages + 1):
            params["page"] = i
            page_data = self.request(params)

            data["search_result"].extend(
                page_data["search_result"],
            )

        return data

    def reverse_whois_name(self, name):
        logger.debug(f'Requesting Reverse Whois data for "{name}"')
        return self._reverse_whois(name=name)

    def reverse_whois_company(self, company):
        logger.debug(f'Requesting Reverse Whois data for company "{company}"')
        return self._reverse_whois(company=company)

    def reverse_whois_email(self, email):
        logger.debug(f'Requesting Reverse Whois data for email "{email}"')
        return self._reverse_whois(email=email)
