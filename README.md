# Sparrot

It's a tool that uses the  [whoxy.com](https://www.whoxy.com/) API to interactively discover related domains. It also tries its best to automatically detect Whois privacy and filter out contacts that belong to the registrars themselves by using the [list of accredited registrars from the IANA](https://www.iana.org/assignments/registrar-ids/registrar-ids.xhtml). 

## Installation

You can install sparrot directly using pip (or even better, [pipx](https://github.com/pypa/pipx)):

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

__NOTE:__ If you want you can also save the API key in the config file located under `~/.config/sparrot.conf` which will be created when running sparrot for the first time.
