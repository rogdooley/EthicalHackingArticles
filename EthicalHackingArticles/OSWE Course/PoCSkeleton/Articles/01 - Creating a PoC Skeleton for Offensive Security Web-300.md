## Rewrite Flow Notes (Part 1: Project Setup)

- [ ] Strengthen the opening paragraph to explain the goal of the series—creating a reusable PoC skeleton for OSWE labs
- [ ] Clarify that each lab will live in its own directory and follow a consistent naming/layout pattern
- [ ] Introduce `uv` earlier as a tool choice, and briefly explain why it was picked (speed, reproducibility, modern Python)
- [ ] Explain why `.env` files are preferred over hardcoded values or inline arguments—more maintainable across labs
- [ ] Consider inserting a sample tree view *after* the directory is created with `uv init`
- [ ] Mention the purpose of each folder (`Archives/`, `Logs/`, `Screenshots/`) with one line of intent per directory
- [ ] Explicitly state the philosophy: low external deps, auditability, portability
- [ ] Add a sentence previewing that CLI wiring and `argparse` will come next
- [ ] Tighten grammar and remove repeated phrases (e.g., repeated "when I started" blocks)
- [ ] Optional: include `.gitignore` suggestions to hide compiled files, logs, env files, etc.


During the start of one's journey taking [Offensive Security's Advanced Web Attacks and Exploitation ](https://www.offsec.com/courses/web-300/) course, you learn that the exam will require the creation of Proof of Concept (PoC) code that, when executed, will exploit a web application and ultimately end with a shell on the machine. While student's are free to choose what programming language they might use to create a PoC, Python seems to be the dominate language used by the students and the course mentors. 

The course consists of many case studies of vulnerable applications and how each one had multiple points of exploitation the when chained together would allow complete compromise and remote code execution. After these case studies are completed, there are lab environments that are configured for white box testing. A debug machine with all the source code is provided and then a victim machine where student's are expected to find exploit paths and practice writing PoCs that will allow the students to retrieve a series of proof flags on the victim machine and the last flag for each machine requires command execution on the machine.

When I started on the first "challenge lab", I realized that I didn't have a game plan for writing the code. I stepped back after starting the first challenge and looked at the big overall picture. What are some commonalities going to exist between all of these machines on the labs that would allow me to optimize my code writing so that I could have a baseline or skeleton script that I could always use as I went from challenge to challenge. 

When I started programming small scripts for the case studies, I didn't have much Python experience. I did have experience with Perl, Java, Bash, and some other languages to a lesser extent. Maybe I could have done this in Perl, but from the Discord channel, most if not all were using Python, I dived right in. The course doesn't require a lot of technical acumen with Python and I'd say if you have slightly intermediate level skills in Python, you should be absolutely fine. There are the standard web requests, parsing JSON, reading web pages, etc... that would be expected when analyzing web code. So I spent a week or two before jumping into the challenge labs working on the beginnings of a PoC skeleton for the course. What I'd like to do over the next 5-10 articles is to outline and provide examples of the decisions I made and some of the code I used to create what would become my skeleton. Part of the reason for creating the skeleton was for the learning experience and to save time as I went from lab to lab.

What I set out to accomplish was to create a scaffold that relied on Python standard libraries or well known libraries. I wanted external dependencies kept to a minimum as well as having an audit trail while the script was running. Sure you can insert print statements galore, but with a little work, one can create their own logging system that can be called like other libraries.

To that end, I always used [uv](https://docs.astral.sh/uv/) to initialize my challenge labs base diretory. `uv` currently isn't a package one can install with `apt install`. Installation is fairly straightforward though. From a terminal, run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
This will install uv in `$HOME/.local/bin/uv`. Let's say I configured a top level directory for my challenge labs like `$HOME/OSWE/ChallengeLabs`. I can `cd` to `ChallengeLabs` and then start my first lab project. For the sake of this and the rest of the articles, we'll be using the fictitious web application `Authrise` as the lab environment. Let's set this up so that by the end of this series we'll have a mostly or totally complete PoC skeleton written in Python.

To create the base of the project, from `$HOME/OSWE/ChallengeLabs`, execute (remove `--vcs git` if you don't want version control):
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

At this point, I would add a couple of directories and a file, `Notes.md` to round off the initial layout.

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

Next, we’ll make this project interactive by wiring up a flexible CLI with _argparse_ _and env-based configuration.

2. Argument Parsing with argparse
3. Making http requests with httpx instead of requests
4. Creating a dataclass to store and read in various information about the target and attacker
5. Creating a layout and using uv
6. Structured Logging
7. Custom web server for hosting or receiving payloads
8. Concurrency Concepts (async)
9. Control Flow and Stage Management
10. Fictitious blind sqli example (async vs linear and binary vs linear and maybe async binary vs async linear) 