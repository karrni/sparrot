import requests

from sparrot.logger import Logger

logger = Logger()


class WhoxyAPIError(Exception):
    """Custom exception for Whoxy API errors."""


class WhoxyAPI:
    """A wrapper class for the Whoxy API."""

    def __init__(self, url, api_key):
        self.url = url
        self.params = {"key": api_key}

    def request(self, params: dict):
        """Send a request to the Whoxy API with the given parameters."""

        params = self.params | params
        response = requests.get(self.url, params)

        data = response.json()
        # logger.debug(data)

        # status = 0 indicates an error
        if data["status"] == 0:
            raise WhoxyAPIError(f"Whoxy API error: {data['status_reason']}")

        return data

    def get_balance(self):
        """Return the account balance."""

        logger.debug("Requesting account balance")
        data = self.request({"account": "balance"})

        return {
            "live": data["live_whois_balance"],
            "history": data["whois_history_balance"],
            "reverse": data["reverse_whois_balance"],
        }

    def whois(self, domain):
        """Request Whois data for the specified domain."""

        logger.debug(f"Requesting Whois data for {domain}")
        return self.request({"whois": domain})

    def whois_history(self, domain):
        """Request historical Whois data for the specified domain."""

        logger.debug(f"Requesting historical Whois data for {domain}")
        return self.request({"history": domain})

    def _reverse_whois(self, **params):
        """Perform a reverse Whois lookup with the given parameters."""

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
        """Request reverse Whois data by registrant name."""

        logger.debug(f'Requesting Reverse Whois data for "{name}"')
        return self._reverse_whois(name=name)

    def reverse_whois_company(self, company):
        """Request reverse Whois data by company."""

        logger.debug(f'Requesting Reverse Whois data for company "{company}"')
        return self._reverse_whois(company=company)

    def reverse_whois_email(self, email):
        """Request reverse Whois data by registrant email."""

        logger.debug(f'Requesting Reverse Whois data for email "{email}"')
        return self._reverse_whois(email=email)
