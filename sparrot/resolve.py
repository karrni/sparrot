import signal
import sys
from configparser import NoOptionError

from colorama import Fore

from sparrot.config import settings
from sparrot.logger import Logger
from sparrot.whoxy import WhoxyAPI

logger = Logger()


class Resolver:
    # keeps track of objects that have already been checked
    _seen_companies = set()
    _seen_emails = set()

    # keeps track of interesting objects
    domains = set()
    companies = set()
    emails = set()

    # common whois privacy strings
    blocklist = (
        "withheldforprivacy",
        "tieredaccess",
        "redacted",
        "privacy",
    )

    def __init__(self):
        try:
            whoxy_url = settings.config.get("whoxy", "url")
            self.whoxy = WhoxyAPI(whoxy_url, settings.api_key)
        except NoOptionError:
            logger.error("For some reason the Whoxy API URL is missing from the config file")
            return

        signal.signal(signal.SIGINT, self._sigint_handler)

    def _sigint_handler(self, signum, frame):
        print(f"{Fore.RED}[!] detected SIGINT, stopping{Fore.RESET}\n\n")
        self.print()
        sys.exit(1)

    @staticmethod
    def query_yes_no():
        choice = input().lower()
        return choice == "y"

    def check_company(self, company):
        if company in self._seen_companies:
            return False
        logger.info(f'[ ] checking company "{company}"')
        self._seen_companies.add(company)

        _company = company.lower()

        if any(s in _company for s in self.blocklist):
            logger.info("[ ] seems protected, skipping")
            return False

        # check if the company is a registrar
        for registrar in settings.registrars:
            if registrar in _company:
                logger.info("[ ] looks to be a registrar, skipping")
                return False

        return True

    def check_email(self, email):
        if email in self._seen_emails:
            return False
        logger.info(f"[ ] checking email {email}")
        self._seen_emails.add(email)

        _email = email.lower()

        if "@" not in _email or "*" in _email:
            logger.info("[ ] doesn't look like a valid email")
            return False

        if any(s in _email for s in self.blocklist):
            logger.info("[ ] seems protected, skipping")
            return False

        return True

    def parse_record(self, record):
        if domain := record.get("domain_name"):
            self.resolve_domain(domain)

        for role in ("registrant", "administrative", "technical", "billing"):
            if contact := record.get(f"{role}_contact"):
                if company := contact.get("company_name"):
                    if self.check_company(company):
                        self.resolve_company(company)

                if email := contact.get("email_address"):
                    if self.check_email(email):
                        self.resolve_email(email)

    def resolve_domain(self, domain):
        if domain in self.domains:
            return

        self.domains.add(domain)
        print(f"{Fore.GREEN}[d] new domain {domain}{Fore.RESET}")

        history = self.whoxy.whois_history(domain)
        if history.get("whois_records"):
            for record in history["whois_records"]:
                self.parse_record(record)

    def resolve_company(self, company):
        print(f'{Fore.YELLOW}[c] new company "{company}", follow? [y/N]{Fore.RESET} ', end="")
        if not self.query_yes_no():
            return

        self.companies.add(company)

        data = self.whoxy.reverse_whois_company(company)
        if data.get("search_result"):
            for record in data["search_result"]:
                self.parse_record(record)

    def resolve_email(self, email):
        print(f"{Fore.YELLOW}[e] new email {email}, follow? [y/N]{Fore.RESET} ", end="")
        if not self.query_yes_no():
            return

        self.emails.add(email)

        data = self.whoxy.reverse_whois_email(email)
        if data.get("search_result"):
            for record in data["search_result"]:
                self.parse_record(record)

    def print(self):
        if self.companies:
            print(f"{Fore.YELLOW}Companies:{Fore.RESET}\n")
            print("\n".join(self.companies))
            print()

        if self.emails:
            print(f"{Fore.YELLOW}Emails:{Fore.RESET}\n")
            print("\n".join(self.emails))
            print()

        print(f"{Fore.GREEN}Domains:{Fore.RESET}\n")
        print("\n".join(self.domains))
        print()

    def resolve(self, domain):
        print("Starting discovery...")
        self.resolve_domain(domain)
        print(f"{Fore.BLUE}[i] all done{Fore.RESET}\n\n")
