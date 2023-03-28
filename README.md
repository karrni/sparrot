<h1 align="center">
  🔮 Sparrot
</h1>

<p align="center">
  Uses the <a href="https://www.whoxy.com">Whoxy</a> API to interactively discover related domains, companies, and e-mails.
  <br>
  Automatically detects Whois Privacy and filters <a href="https://www.iana.org/assignments/registrar-ids/registrar-ids.xhtml">official registrars</a>.
</p>

## Installation

You can install it from source using Poetry:

```
git clone https://github.com/karrni/sparrot
cd sparrot
poetry install
poetry run sparrot
```

Alternatively, you can install using pip (or even better, [pipx](https://github.com/pypa/pipx)):

```
pip install git+https://github.com/karrni/sparrot
```

After that, the `sparrot` command should be available from your command line.

## Whoxy

__The Whoxy Whois API is not free__ - you need to create an account and buy credits to use it.

After you've done that, get your API key from the "Account Manager" page.

## Usage

Pretty straightforward. Specify your API key and the domain from which you want to start:

```
sparrot -k [YOUR_KEY] target.com
```

__NOTE:__ If you want you can store the API key in the config file `~/.config/sparrot.toml`. It will be created when running sparrot for the first time.irst time.
