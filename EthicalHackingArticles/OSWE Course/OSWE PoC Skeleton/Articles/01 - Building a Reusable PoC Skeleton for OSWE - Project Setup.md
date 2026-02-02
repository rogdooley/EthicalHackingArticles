---
title: 01 - Building a Reusable OSWE PoC Skeleton - Project Setup
series: OSWE PoC Skeleton
series_order: 1
tags:
  - oswe
  - web-300
  - exploit-development
  - poc
  - python
  - offensive-security
description: A practical foundation for repeatable exploit development in OSWE labs.
---

# 01 - Building a Reusable OSWE PoC Skeleton - Project Setup

One of the exam requirements for [Offensive Security's Advanced Web Attacks and Exploitation ](https://www.offsec.com/courses/web-300/)course is the creation of Proof of Concept (PoC) code that, when executed, exploits a web application to obtain a shell or retrieving the required proof.txt file. While students are free to choose what programming language they might use to create a PoC, Python is the dominant choice among both students and course mentors.

The course consists of many case studies of vulnerable applications and how each one had multiple points of exploitation that, when chained together, would allow complete compromise and remote code execution. After these case studies are completed, there are lab environments that are configured for white box testing. A debug machine with all the source code is provided and then a victim machine where students are expected to find exploit paths and practice writing PoCs that will allow the students to retrieve a series of proof flags on the victim machine and the last flag for each machine requires command execution on the machine.

When I started on the first "challenge lab", I realized that I didn't have a game plan for writing the code. I stepped back after starting the first challenge and looked at the big overall picture. What are some commonalities going to exist between all of these machines on the labs that would allow me to optimize my code writing so that I could have a baseline or skeleton script that I could always use as I went from challenge to challenge.

I started this course with experience programming in Perl, Java, along with a handful of other languages where my grasp was tenuous. Perl could have been an OK choice for creating the PoCs, but Python is really the language de jour just glancing at the course and the Discord channel. Given what I know now, one's Python skill by the end of the course should be at an intermediate level. Standard Python knowledge of making and parsing HTTP requests, reading and writing files, along with dealing with HTML. Full disclaimer: I didn't finish all the course modules due to having also gone through the HTB CWEE course material. I felt that certain sections of the course would be repeating knowledge I already had acquired. After the first challenge lab, I began working on the beginnings of a PoC skeleton which I continued to refine or even rebuild over the next few labs. By the time I had finished the fourth lab, my code base was pretty stable.

What I set out to accomplish was to create a scaffold that relied on Python standard libraries or well known libraries. I wanted external dependencies kept to a minimum as well as having an audit trail while the script was running. Sure you can insert print statements galore, but with a little work, one can create their own logging system that can be called like other libraries.

To that end, I always used [uv](https://docs.astral.sh/uv/) to initialize my challenge labs base directory. `uv` currently isn't a package one can install with `apt install`. Installation is fairly straightforward though. From a terminal, run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

This will install `uv` in `$HOME/.local/bin/uv`. Let's say I configured a top level directory for my challenge labs like `$HOME/OSWE/ChallengeLabs`. I can `cd` to `ChallengeLabs` and then start the first lab project. For the sake of this and the rest of the articles, I'll be using the fictitious web application `Authrise` as the lab environment. Let's set this up so that by the end of this series we'll have a mostly or totally complete PoC skeleton written in Python. I use `uv` as a replacement for `pip + venv + poetry-style behavior`. `uv` keeps the skeleton reproducible across all labs. and will allow us to install various third-party dependencies in the virtual environment it creates.

The base of the project, from `$HOME/OSWE/ChallengeLabs`, is created by executing (remove `--vcs git` if you don't want version control):

```bash
❯ uv init --bare --no-readme --vcs git authrise
Initialized project `authrise` at `$HOME/OSWE/ChallengeLabs/authrise`
```

So the layout should be like this.

```bash
❯ tree -a authrise
authrise
├── .git
│   ├── HEAD
│   ├── config
│   ├── description
│   ├── hooks
│   │   ├── applypatch-msg.sample
│   │   ├── commit-msg.sample
│   │   ├── fsmonitor-watchman.sample
│   │   ├── post-update.sample
│   │   ├── pre-applypatch.sample
│   │   ├── pre-commit.sample
│   │   ├── pre-merge-commit.sample
│   │   ├── pre-push.sample
│   │   ├── pre-rebase.sample
│   │   ├── pre-receive.sample
│   │   ├── prepare-commit-msg.sample
│   │   ├── push-to-checkout.sample
│   │   ├── sendemail-validate.sample
│   │   └── update.sample
│   ├── info
│   │   └── exclude
│   ├── objects
│   │   ├── info
│   │   └── pack
│   └── refs
│       ├── heads
│       └── tags
├── .gitignore
└── pyproject.toml

```

`pyproject.toml` will currently contain a very basic structure which we'll fill in by editing or managing with `uv` over the course of these articles.

```bash
❯ cat pyproject.toml
[project]
name = "authrise"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = []
```

Keeping generated artifacts out of version control reduces noise and makes reviewing changes to your PoC much easier.

If you decide to use version control with git, now is a good time to configure `.gitignore` so that various artifacts won't end up in version control. I found this configuration a good starting off point. I'm using [VS Codium](https://vscodium.com/)for my IDE with various plugins. Your .gitignore might look significantly different.

```bash
# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv

# Environments
.env
env/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# vscode
.vscode/
```

Given some thought to other pieces to start with, I created a few directories for storing logs, any items that might be saved from the exploit into archives, and a place to store screenshots. For notes, I created `Notes.md` in the root directory.

```bash
❯ touch Notes.md
❯ mkdir {Archives,Screenshots,Logs}
❯ tree
.
├── Archives
├── Logs
├── Notes.md
├── Screenshots
└── pyproject.toml

4 directories, 2 files

```

* Archives/ — saved artifacts from exploitation (responses, dumps, tokens)
* Logs/ — structured runtime logs for debugging and auditability
* Screenshots/ — exam-safe references when copying files is prohibited

This will be the directory structure for every lab and for the exam. We'll extend this in later articles by adding custom modules and building the PoC skeleton. I used `Notes.md` to save any information I thought might be relevant to understanding the web application presented. This would include POST request bodies along with responses, database table descriptions, etc... For the exam, copying code from the Offsec machines to your machine is strictly forbidden, so having screenshots is a good way to remind yourself where a certain vulnerability lies.

Up until now, I haven’t made mention of any Python code. What you name your script is largely a matter of preference. I tended to favor either `exploit.py` or the name of the target application. For this example, I’ll simply use `poc.py`.

Below is a deliberately minimal starting point:

```python
def main():
	print("Starting PoC")
	
if __name__ == "__main__":
    main()
```

This code does nothing interesting by design. Its purpose is simply to establish a consistent entry point that we will extend over time. As the series progresses, this file will grow to include context handling, structured logging, payload hosting, concurrency, and stage-based control flow. Each PoC requires configuration in order to run against a target. At a minimum, this includes details such as the target address, listening interfaces, and various feature or stage toggles. To support this, the next step is to make the project interactive by wiring up a flexible command-line interface using `argparse`.

We’ll also briefly look at using an environment file for configuration. While this can keep commands short, it comes with trade-offs. In the next article, I’ll show how to configure both approaches and explain why I ultimately prefer explicit command-line arguments for clarity, discoverability, and operator control.

My plan for this series is to build the code base to show you how to I built up my PoC over the course of a few months with the goal of having you develop your own. I'm planning on proceeding from single topics that progress to testing the PoC against a fictitious server with an SQL flaw that will allow us to extract a token and showing the difference between a linear and binary search.

## Series Roadmap

This article establishes the foundation for the PoC skeleton. Each subsequent part builds on this structure incrementally.

2. [Argument Parsing for OSWE PoCs - argparse vs dotenv](<02 -  Argument Parsing for OSWE PoCs - argparse vs dotenv.md>)
3. [Context Management with Dataclasses](<03 - Context Management with Dataclasses.md>)
4. [Control Flow and Stage Management](<04 - Control Flow and Stage Management.md>)
5. [Structured Logging for Exploit Development](<05 - Structured Logging for Exploit Development.md>)
6. [One-Shot Web Servers for Payload Delivery and Callbacks](<06 - One-Shot Web Servers for Payload Delivery and Callbacks.md>)
7. [Asynchronous Execution for Request-Heavy Exploit Stages](<07 - Asynchronous Execution for Request-Heavy Exploit Stages.md>)
8. A fictitious blind SQL injection example (linear vs binary and async variants)

By the end of this series, you should have a reusable PoC skeleton that you can adapt to each lab or exam target with minimal rewrites.



