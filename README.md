[![CI](https://github.com/mdg-iitr/github-slack-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/mdg-iitr/github-slack-bot/actions/workflows/ci.yml)
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

# GitHubBot

A Slack bot that informs users of updates in a GitHub org.

### Features

This bot has

- More specific events, and
- Less verbose messages

than the official GitHub-Slack integration.

### Setup for development

#### 0. Requirements:

 - Python 3.9 or above.
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

#### 5. Get the environment variables from another contributor
#### 6. [Download and configure ngrok](https://betterprogramming.pub/ngrok-make-your-localhost-accessible-to-anyone-333b99e44b07)
#### 7. Send your generated URL to MDG org admins
#### 8. Run the bot

```
$ python main.py
```

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/Sickaada"><img src="https://avatars.githubusercontent.com/u/61564567?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Madhur Rao</b></sub></a><br /><a href="#mentoring-Sickaada" title="Mentoring">🧑‍🏫</a> <a href="https://github.com/mdgspace/github-slack-bot/pulls?q=is%3Apr+reviewed-by%3ASickaada" title="Reviewed Pull Requests">👀</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
