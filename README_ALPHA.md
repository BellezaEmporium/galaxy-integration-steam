<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Pre-Alpha Testing](#pre-alpha-testing)
  - [Setup (Windows)](#setup-windows)
  - [Setup (MacOS)](#setup-macos)
  - [The Logs](#the-logs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Pre-Alpha Testing

If you're here, you know things could be (and likely will be) broken. You are here because we are few, but you are many. It's easier to find bugs and such by making you do it.

## Setup (Windows)

- Download Python 3.7.9, 32-bit (64-bit also works). It is the only version that will work, and is the one GOG Galaxy uses.
- Install it with the defaults
- Set up your working directory. this will be the place you download or clone this repo to.
- Create a new virtual env:
  - If you only have python 3.7.9, run:
    `python.exe -m venv .venv -p "%localappdata%\Programs\Python\Python37-32\python.exe" --pip 22.2.0`
  - If you have multiple python versions installed (assumes you have `py` as well)
    `py.exe -3.7 -m venv .venv -p "%localappdata%\Programs\Python\Python37-32\python.exe" --pip 22.2.0`
- Activate the virtual env:
  `.\.venv\Scripts\activate.ps1`
- Install the dev dependencies (optional). This will let you potentially help us debug, but isn't really necessary if you don't feel comfortable monkeying around the code.
  `pip install -r requirements/dev.txt`
- Install `invoke`* Only necessary if you didn't install the dev dependencies. This IS required
  `pip install invoke==2.2.0`
- Backup the current installation of steam (optional) we will overwrite this in the next command.
- Install the plugin in it's buggy glory:
  `inv install`

## Setup (MacOS)

- Download Python 3.7.9, 32-bit (64-bit also works). It is the only version that will work, and is the one GOG Galaxy uses.
- Install it with the defaults
- Set up your working directory. this will be the place you download or clone this repo to.
- Create a new virtual env:
  `python -m virtualenv .venv --pip 22.2.0`
- Activate the virtual env:
  `./.venv/Scripts/activate`
- Install the dev dependencies (optional). This will let you potentially help us debug, but isn't really necessary if you don't feel comfortable monkeying around the code.
  `pip install -r requirements/dev.txt`
- Backup the current installation of steam (optional) we will overwrite this in the next command.
- Install the plugin in it's buggy glory:
  `inv install`

## The Logs

 We need them. We will ask for them when something breaks. For windows, they are located at `C:\ProgramData\GOG.com\Galaxy\logs`. For MacOS, they are located at `/Users/Shared/GOG.com/Galaxy/Logs`
 When you first install the plugin, make sure to delete `plugin-steam-<whatever gibberish is here>.log`. It makes it easier to start with a fresh log than read through old stuff.
