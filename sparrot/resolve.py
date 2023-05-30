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
    """A class used to discover related domains from a root domain.

    The discovery process follows the following process:

    0. Request historical Whois records for root domain
    1. Iterate over historical Whois records for domain
    2. Iterate over contacts for Historical Whois record
    3. Ask user if email/company of contact is relevant
        3a. Request reverse Whois records for email/company
        3b. Iterate over domains in reverse Whois record
        3c. Repeat from step 1. with new domain

    During all of this, emails and companies are checked for known Whois
    privacy strings or known registrars. If they match, they are skipped to
    reduce the noise and to avoid resolving unrelated domains.
    """

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
        self._root_domains = []

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
                raise ResolverError("URL is missing in the config file") from e
            raise e

        signal.signal(signal.SIGINT, self._sigint_handler)

    def _sigint_handler(self, signum, frame):
        """
        SIGINT handler so we can print the results even if the user forcefully
        (Ctrl+C) stops the execution.
        """

        logger.error("Detected SIGINT, stopping")

        self.write_file()
        self.print_stats()

        sys.exit(1)

    # --- Verification, Sanity Checking ---

    def check_company(self, company):
        """
        Checks if a company has been seen, contains any known privacy strings,
        or is a known registrar.
        """

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
        if _company in settings.registrars:
            logger.info("Looks to be a registrar, skipping")
            return False

        return True

    def check_email(self, email):
        """
        Checks if an email address has been seen, is formatted correctly, or
        contains known privacy strings.
        """

        if email in self._seen_emails:
            return False
        logger.debug(f"Checking email {email}")
        self._seen_emails.add(email)

        _email = email.lower()

        if "@" not in _email or "*" in _email:
            logger.debug("Doesn't look like a valid email")
            return False

        if any(s in _email for s in self.blocklist):
            logger.debug("Looks protected, skipping")
            return False

        return True

    # --- Record Parsing ---

    def parse_contact(self, contact):
        """
        Parses a contact dictionary, checking and potentially resolving the
        company and email.
        """

        if company := contact.get("company_name"):
            if self.check_company(company):
                self.resolve_company(company)

        if email := contact.get("email_address"):
            if self.check_email(email):
                self.resolve_email(email)

    def parse_record(self, record):
        """
        Parses a Whois record dictionary, resolving the domain and parsing each
        contact.
        """

        if domain := record.get("domain_name"):
            self.resolve_domain(domain)

        for role in ("registrant", "administrative", "technical", "billing"):
            if contact := record.get(f"{role}_contact"):
                self.parse_contact(contact)

    # --- API Requests ---

    def resolve_domain(self, domain):
        """
        Resolves a domain name, adding it to the set of seen domains and parsing
        its Whois history records.
        """

        if domain in self.domains:
            return

        self.domains.add(domain)
        logger.success(f"New domain {domain}")

        history = self.whoxy.whois_history(domain)
        if history.get("whois_records"):
            for record in history["whois_records"]:
                self.parse_record(record)

    def resolve_company(self, company):
        """
        Resolves a company name, asking the user if they wish to.
        """

        decision = logger.ask(f'New company "{company}", follow?')
        if not decision:
            return

        self.companies.add(company)

        data = self.whoxy.reverse_whois_company(company)
        if data.get("search_result"):
            for record in data["search_result"]:
                self.parse_record(record)

    def resolve_email(self, email):
        """
        Resolves an email address, asking the user if they wish to.
        """

        decision = logger.ask(f'New email "{email}", follow?')
        if not decision:
            return

        self.emails.add(email)

        data = self.whoxy.reverse_whois_email(email)
        if data.get("search_result"):
            for record in data["search_result"]:
                self.parse_record(record)

    # --- Main Methods ---

    def resolve(self, domain):
        """
        Initiates the discovery process from the root domain, resolving it
        and printing the stats and writing the output files.
        """

        logger.info("Starting discovery...")
        self._root_domains.append(domain)
        self.resolve_domain(domain)
        logger.success("All done")

        self.write_file()
        self.print_stats()

    def print_stats(self):
        """
        Prints the discovered companies, emails, and domains to the console.
        """

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

    def write_file(self):
        """
        Writes the discovered domains to a file.
        """

        logger.info("Writing output file")

        basename = "-".join(self._root_domains)
        filename = f"{basename}-sparrot.txt"
        logger.debug(f"Writing {filename}")

        with open(filename, "w") as fp:
            fp.write("\n".join(self.domains))
