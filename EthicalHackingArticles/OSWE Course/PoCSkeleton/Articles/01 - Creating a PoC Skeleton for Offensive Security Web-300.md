
During the start of one's journey taking [Offensive Security's Advanced Web Attacks and Exploitation ](https://www.offsec.com/courses/web-300/) course, you learn that the exam will require the creation of Proof of Concept (PoC) code that, when executed, will exploit a web application and ultimately end with a shell on the machine. While student's are free to choose what programming language they might use to create a PoC, Python seems to be the dominate language used by the students and the course mentors. 

The course consists of many case studies of vulnerable applications and how each one had multiple points of exploitation the when chained together would allow complete compromise and remote code execution. After these case studies are completed, there are lab environments that are configured for white box testing. A debug machine with all the source code is provided and then a victim machine where student's are expected to find exploit paths and practice writing PoCs that will allow the students to retrieve a series of proof flags on the victim machine and the last flag for each machine requires command execution on the machine.

When I started on the first "challenge lab", I realized that I didn't have a game plan for writing the code. I stepped back after starting the first challenge and looked at the big overall picture. What are some commonalities going to exist between all of these machines on the labs that would allow me to optimize my code writing so that I could have a baseline or skeleton script that I could always use as I went from challenge to challenge. 

When I started programming small scripts for the case studies, I didn't have much Python experience. I did have experience with Perl, Java, Bash, and some other languages to a lesser extent. Maybe I could have done this in Perl, but from the Discord channel, most if not all were using Python, I dived right in. The course doesn't require a lot of technical acumen with Python and I'd say if you have slightly intermediate level skills in Python, you should be absolutely fine. There are the standard web requests, parsing JSON, reading web pages, etc... that would be expected when analyzing web code. So I spent a week or two before jumping into the challenge labs working on the beginnings of a PoC skeleton for the course. What I'd like to do over the next 5-10 articles is to outline and provide examples of the decisions I made and some of the code I used to create what would become my skeleton. Part of the reason for creating the skeleton was for the learning experience and to save time as I went from lab to lab.

What I set out to accomplish was to create a scaffold that relied on Python standard libraries or well known libraries. I wanted external dependencies kept to a minimum as well as having an audit trail while the script was running. Sure you can insert print statements galore, but with a little work, one can create their own logging system that can be called like other libraries.

To that end, I always used [uv](https://docs.astral.sh/uv/) to initialize my challenge labs base directoryt. `uv` currently isn't a package one can install with `apt install`. Installation is fairly straightforward though. From a terminal, run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
This will install uv in `$HOME/.local/bin/uv`. Let's say I configured a top level directory for my challenge labs like `$HOME/OSWE/ChallengeLabs`. I can `cd` to `ChallengeLabs` and then start my first lab project. For the sake of this and the rest of the articles, we'll be using the fictitious web application `Authrise` as the lab environment. Let's set this up so that by the end of this series we'll have a mostly or totally complete PoC skeleton written in Python. We use `uv` as a replacement for `pip + venv + poetry-style behavior`. `uv` keeps the skeleton reproducible across all labs. `uv` will allow us to install various 3rd part dependencies in the virtual environment it creates.

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

Given some thought to other pieces to start with, I created a few directories for storing logs,  any items that might be saved from the exploit into archives, and a place to store screenshots. For notes, I created `Notes.md` in the root directory.

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

This will be the directory structure for every lab and for the exam. We'll extend this in later articles by adding custom modules and building the PoC skeleton. I used `Notes.md` to save  any information I thought might be relevant to understanding the web application presented. This would include POST request bodies along with responses, database table descriptions, etc... For the exam, copying code from the Offsec machines to your machine is strictly forbidden, so having screenshots is a good way to remind yourself where a certain vulnerability lies.

Up until now, I haven't made mention of any Python code. What you name your script is up to you. I tended to favor naming the script either exploit.py or using the web application name. For this example, I'm going to just use poc.py.  Below is a very barebones starting point.

```python
def main():
	print("Starting PoC")
	
if __name__ == "__main__":
    main()
```

The code is very uninteresting, but it's a first step to building a reusable code will contain context handling, logging, payload serving, concurrency, and stage management. Each program will have a list of configuration options that are required to run the code against the target. To that end, we’ll make this project interactive by wiring up a flexible CLI with _argparse_ . We’ll also briefly look at using an environment file for configuration. It keeps commands short, but it comes with trade-offs. In the next part I'll present how to configure both and decide which one I choose  for the best balance of clarity and operator flexibility. Doing so will allow us and any other user's of our code to change the target's IP address, the attacker's address, and many other options that allows the operator flexibility when interacting with the PoC.  

My plan for this series is to build the code base to show you how to I built up my PoC over the course of a few months with the goal of having you develop your own. I'm planning on proceeding from single topics that progress to testing  the poc against a fictitious server with an sql flaw that will allow us to extract a token and showing the difference between a linear and binary search. 

2. Argument Parsing with argparse with a brief mention of using dotenv
3. Creating a dataclass to store and read in various information about the target and attacker
4. Structured Logging
5. Custom web server for hosting or receiving payloads
6. Concurrency Concepts (async)
7. Control Flow and Stage Management
8. Fictitious blind sqli example (async vs linear and binary vs linear and maybe async binary vs async linear) 