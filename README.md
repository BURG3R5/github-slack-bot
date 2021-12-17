# GitHubBot

A Slack bot that informs users of updates in a GitHub org.

### Features

This bot has

- More specific events, and
- Less verbose messages

than the official GitHub-Slack integration.

### Setup for development

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

#### 5. Enable Git hooks

```
$ git config --local --add core.hooksPath .githooks 
```

#### 6. Get the environment variables from another contributor
#### 7. [Download and configure ngrok](https://betterprogramming.pub/ngrok-make-your-localhost-accessible-to-anyone-333b99e44b07)
#### 8. Send your generated URL to MDG org admins
