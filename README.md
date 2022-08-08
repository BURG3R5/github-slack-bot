[![CI](https://github.com/mdg-iitr/github-slack-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/mdg-iitr/github-slack-bot/actions/workflows/ci.yml)
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-5-orange.svg?style=flat-square)](#contributors)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

# GitHubBot

A Slack bot that informs users of updates in a GitHub org.

### Features

This bot has

- More specific events, and
- Less verbose messages

than the official GitHub-Slack integration.

### Installation

#### 0. Requirements:

- A server with public endpoints
- Python **3.10.2** or above: [Windows](https://www.python.org/downloads/windows/), [MacOS](https://www.python.org/downloads/macos/), [Linux](https://www.linuxcapable.com/how-to-install-python-3-10-on-ubuntu-20-04/)
- Git

#### 1. Clone this repo

```
$ git clone https://github.com/mdg-iitr/github-slack-bot.git
$ cd github-slack-bot
```

#### 2. Connect to GitHub

- Add `<your-url>/github/events` to your organization or repository's webhooks.
- Set "Content type" to `application/json`
- Check the "Send me everything" radio button

#### 3. Connect to Slack

- Find and replace every instance of `<your-url>` in the [provided manifest](https://github.com/BURG3R5/github-slack-bot/blob/master/bot_manifest.yml) with whatever your server's URL is.
- Go to [link](https://api.slack.com/apps) and create a new app using the edited manifest.
- Install the app to your Slack workspace.

#### 4. Environment variables

- Copy `.env.sample` to `.env`.
- Set `DEBUG` to 0 and the other variables to appropriate values.

#### 5. Create a virtual environment

```
$ python -m venv venv
```
Or, if your system contains both Python 2 and Python 3, use `python3`.

#### 6. Activate your virtual environment

MacOS and Linux:
```
$ source venv/bin/activate
```

Windows:
```
> venv\Scripts\activate
```

#### 7. Install dependencies

```
$ pip install -r requirements.txt
```

Or, if your system contains both Python 2 and Python 3, use `pip3`.

#### 8. Run the bot

```
$ python main.py
```

### Setup for development

#### 0. Requirements:

 - Python **3.10.2** or above: [Windows](https://www.python.org/downloads/windows/), [MacOS](https://www.python.org/downloads/macos/), [Linux](https://www.linuxcapable.com/how-to-install-python-3-10-on-ubuntu-20-04/)
 - Git

#### 1. Clone this repo

```
$ git clone https://github.com/mdg-iitr/github-slack-bot.git
$ cd github-slack-bot
```

#### 2. Create a virtual environment

```
$ python -m venv venv
```
Or, if your system contains both Python 2 and Python 3, use `python3`.

#### 3. Activate your virtual environment

MacOS and Linux:
```
$ source venv/bin/activate
```

Windows:
```
> venv\Scripts\activate
```

#### 4. Install dependencies
```
$ pip install -r requirements.txt
```
Or, if your system contains both Python 2 and Python 3, use `pip3`.

#### 5. Enable git hooks
```
$ pip install pre-commit
$ pre-commit install
```

#### 6. Get the environment variables from a maintainer
#### 7. [Download and configure ngrok](https://betterprogramming.pub/ngrok-make-your-localhost-accessible-to-anyone-333b99e44b07)
#### 8. Send your generated URL to a maintainer
#### 9. Run the bot

```
$ python main.py
```

### Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/BURG3R5"><img src="https://avatars.githubusercontent.com/u/77491630?v=4?s=100" width="100px;" alt=""/><br /><sub><b>BURG3R5</b></sub></a><br /><a href="https://github.com/BURG3R5/github-slack-bot/commits?author=BURG3R5" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/Sickaada"><img src="https://avatars.githubusercontent.com/u/61564567?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Madhur Rao</b></sub></a><br /><a href="#mentoring-Sickaada" title="Mentoring">🧑‍🏫</a> <a href="https://github.com/BURG3R5/github-slack-bot/pulls?q=is%3Apr+reviewed-by%3ASickaada" title="Reviewed Pull Requests">👀</a> <a href="#projectManagement-Sickaada" title="Project Management">📆</a></td>
    <td align="center"><a href="https://github.com/Magnesium12"><img src="https://avatars.githubusercontent.com/u/99383854?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Magnesium12</b></sub></a><br /><a href="https://github.com/BURG3R5/github-slack-bot/commits?author=Magnesium12" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/shashank-k-y"><img src="https://avatars.githubusercontent.com/u/74789167?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Shashank</b></sub></a><br /><a href="https://github.com/BURG3R5/github-slack-bot/commits?author=shashank-k-y" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/srinjoyghosh-bot"><img src="https://avatars.githubusercontent.com/u/76196327?v=4?s=100" width="100px;" alt=""/><br /><sub><b>srinjoyghosh-bot</b></sub></a><br /><a href="https://github.com/BURG3R5/github-slack-bot/commits?author=srinjoyghosh-bot" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
