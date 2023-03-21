import signal
import sys

from colorama import Fore

from sparrot.config import settings
from sparrot.logger import Logger
from sparrot.utils import color_number
from sparrot.whoxy import WhoxyAPI

logger = Logger()


class ResolverError(Exception):
    """Custom exception for Resolver errors."""


class Resolver:
    # Common whois privacy strings
    blocklist = (
        "withheldforprivacy",
        "tieredaccess",
        "redacted",
        "privacy",
        "not disclosed",
    )

    def __init__(self):
        # Keeps track of objects that have already been checked
        self._seen_companies = set()
        self._seen_emails = set()

        # Keeps track of the domains that were resolved
        self._resolved_domains = []

        # Keeps track of interesting objects
        self.domains = set()
        self.companies = set()
        self.emails = set()

        try:
            whoxy_url = settings.config["whoxy"]["url"]
            self.whoxy = WhoxyAPI(whoxy_url, settings.api_key)

            # Get and print the current account balance
            balance = self.whoxy.get_balance()

            live = color_number(balance["live"])
            history = color_number(balance["history"])
            reverse = color_number(balance["reverse"])

            logger.info(f"Balance: Live {live}, History {history}, Reverse {reverse}")

        except KeyError as e:
            if "url" in str(e):
                raise ResolverError("URL is missing in the config file")
            raise e

        signal.signal(signal.SIGINT, self._sigint_handler)

    def _sigint_handler(self, signum, frame):
        logger.error("Detected SIGINT, stopping")

        self.write_files()
        self.print_stats()

        sys.exit(1)

    def check_company(self, company):
        if company in self._seen_companies:
            return False
        logger.debug(f'Checking company "{company}"')
        self._seen_companies.add(company)

        _company = company.lower()

        # Check if the company contains words from the blocklist
        if any(s in _company for s in self.blocklist):
            logger.debug("Looks protected, skipping")
            return False

        # Check if the company is a registrar
        for registrar in settings.registrars:
            if registrar in _company:
                logger.debug("Looks to be a registrar, skipping")
                return False

        return True

    def check_email(self, email):
        if email in self._seen_emails:
            return False
        logger.debug(f"Checking email {email}")
        self._seen_emails.add(email)

        _email = email.lower()

        if "@" not in _email or "*" in _email:
            logger.debug("Doesn't look like a valid email")
            return False

        if any(s in _email for s in self.blocklist):
            logger.debug("Seems protected, skipping")
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
        logger.success(f"New domain {domain}")

        history = self.whoxy.whois_history(domain)
        if history.get("whois_records"):
            for record in history["whois_records"]:
                self.parse_record(record)

    def resolve_company(self, company):
        decision = logger.ask(f'New company "{company}", follow?')
        if not decision:
            return

        self.companies.add(company)

        data = self.whoxy.reverse_whois_company(company)
        if data.get("search_result"):
            for record in data["search_result"]:
                self.parse_record(record)

    def resolve_email(self, email):
        decision = logger.ask(f'New email "{email}", follow?')
        if not decision:
            return

        self.emails.add(email)

        data = self.whoxy.reverse_whois_email(email)
        if data.get("search_result"):
            for record in data["search_result"]:
                self.parse_record(record)

    def resolve(self, domain):
        logger.info("Starting discovery...")
        self._resolved_domains.append(domain)
        self.resolve_domain(domain)
        logger.success("All done")

        self.write_files()
        self.print_stats()

    def print_stats(self):
        print("\n")
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

    def write_files(self):
        logger.info("Writing output files")

        basename = "-".join(self._resolved_domains)

        for var in ("domains", "companies", "emails"):
            filename = f"{basename}-{var}.txt"
            logger.debug(f"Writing {filename}")

            if data := getattr(self, var):
                with open(filename, "w") as fp:
                    fp.write("\n".join(data))
