---
title: 04 - Control Flow and Stage Management in OSWE PoCs
description: |
  How exploit proof-of-concepts evolve beyond linear scripts. This article introduces control-flow thinking, stage-based execution, and resilience patterns for OSWE-style exploit development.
author: Roger Dooley
series: Building Robust OSWE PoCs
part: 4
topics:
  - exploit development
  - control flow
  - stage-based execution
  - oswe
  - poc design
prerequisites:
  - argparse
  - python functions
  - basic exploit chaining
related:
  - 02 - Argument Parsing for OSWE PoCs - argparse vs dotenv
  - 03 - Context Management with Dataclasses
next: 05 - Structured Logging for Exploit Development
---
## Why Control Flow Matters in Exploit Code

We're going to build a more conceptual mindset here which will allow us to think about how to sequence the actions we will need to chain tasks together and build the exploit. This section might seem out of place. My goal is to think about control flow and have you decide on a philosophy of how you'd like to build your PoC. Will `main()` be relatively clean and filled with mostly function calls and logic or will `main()` contain the whole exploit. Most snippets of PoCs that I've come across in the OSWE Discord Channel are of the former. 

At this stage, it's important to think about flow control. You will have seen at least snippets of code that explore how to get from an unauthenticated state to remote code execution on the victim's machine. Execution here is usually a linear series of steps. However, we will want to check the status of each step and possibly retry or recover from any errors or failures. It may be enough to just plow through from initial access to full control without considering any possible errors in your code. While we're not trying to be a software engineer here, it is wise to consider there may be unforeseen errors from the web server, for example, that could be retried if conditions warrant.

From a traditional software engineering point of view, `main()` should be kept as small as possible. It is meant for parsing arguments, initializing resources, and handling the setup and teardown of database connections, etc... 

## When Linear Scripts Break Down

At this point, there’s a disconnect between how exploit code is often presented and how it actually evolves during a lab or exam. You may start with the hard coding of user registration in your script.  A user object could be represented as a global JSON object and PoC may be ready to test user 

```python
USER = {
    "email": "john.doe@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
}


def create_user(ctx: ExploitContext, user: Dict[str, str]) -> None:
    endpoint = f"{ctx.target_url()}/registration"

    response = requests.post(endpoint, json=user)
    if response.status_code != 200:
        logger.error(f"Failed to create user: {response.status_code} : {response.text}")
        raise Exception(f"Failed to create user: {response.status_code}")

    return None

```

creation. Once run, this fictional application returns a status code of 200 if the user was created successfully. Further examination of the application's source code indicates an endpoint is vulnerable to SQL injection for authenticated users. Another function or functions are created to probe that endpoint and extract results. With the current code, the user would attempted to be recreated again and we'd encounter our first failure. For OSWE, the time honored solution for this is to restart the lab, or if you're clever enough, restart the web application in a fresh state. If this was a client's server, for example, there would be no luxury of resetting the system to baseline. 

Where do you go from here? One "out", would be to use [Faker](https://faker.readthedocs.io/en/master/) and rewrite the `create_user`function. At this point, many PoCs begin accumulating one-off fixes: random identities, sleeps, retries, or manual resets. You could also refactor code to check if a user is already registered instead of continuously creating new users because each new user should be logged or saved in some file as a record of what was done. There are a multitude of spur of the moment design decisions that may end up being the wrong call long-term. 

Decisions like this manage the control flow of the PoC. I'm not sure there is a best decision here because in the end, there are a few things that matter:
1. For the exam, the PoC works given the exam objectives
2. Experience is making design decisions based on the application code flaws
3. Proficiency in spotting flaws in the execution of web apps 
4. Library of code and code snippets that provide quality of life improvements

Almost every control-flow decision in a PoC reduces to one of a few patterns:
- *Retry*
- *Checking state*
- *Persist artifacts*
- *Branching*
- *Aborting*

## Thinking in Stages instead of Lines

Once a step succeeds, the exploit now has memory. Assuming that a chain of events or actions are found that will likely result in a full takeover of the web application and these actions are in some notes, the first choice for crafting the exploit code would likely result in a linear login chain. This might be mapped out in notes something like:

```text
parse args
load config
register user
login
acquire token
login with elevated privileges
remote code execution
```

In the implicit control model, the code runs top to bottom. There is no consideration for unexpected errors or other conditions that could cause the code to stall, need a retry, or even start anew. The code is somewhat brittle and any unexpected issue could result in the code crashing or maybe having some unexpected side effect on the hosted web application. You really want to think about this more for future clients than contrived labs. With a little tweaking, this linear progression can be converted to code that is more error tolerant and robust.

Let's say we think about the steps as stages. Where each part makes an assumption and the produces something. Each part is encapsulated such that there are preconditions for each stage and a stage will produce something that will guarantee the next step. This could be logging into a site to get a cookie, and then using the login privilege to take advantage of some logic error or misconfiguration to extract a token or some account information. Almost every PoC has some rough structure: ParseArgs → BuildRequest → Send → ParseResponse → Report. 


```text
┌────────────────────┐
│   Initial State    │
│ (no auth, no data) │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Stage 1           │
│  Acquire State     │
│  (account, token)  │
└─────────┬──────────┘
          │ success
          │
          ▼
┌────────────────────┐
│  Stage 2           │
│  Use State         │
│  (access feature)  │
└─────────┬──────────┘
          │ success
          │
          ▼
┌────────────────────┐
│  Stage 3           │
│  Escalate / Extract│
│  (data, exec)      │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Terminal State    │
│  (flag, shell)     │
└────────────────────┘
```

Fictitious function definitions for a staged architecture:

```python
def parse_args(argv) -> Args:
    ...

def probe_target(ctx: ExploitContext) -> ProbeResult:
    ...

def exploit(ctx: ExploitContext, probe: ProbeResult) -> ExploitResult:
    ...

def report(result: ExploitResult) -> None:
    ...

```

By staging your PoC, you will have something easier to debug and easier to reuse. This allows one to organize their code based on the current goals for each step. This could be a single line or a multitude of function calls. A stage is about assumptions and not structure. A stage answers two questions: _what must already be true_, and _what will be true if this step succeeds_.

## Making Stages Resilient

In the case of user creation, instead of `create_user()`, a function could be made that checks if the user has been created, if not, then create the user. This `ensure_user` function is safe to call repeatedly. Then in the code, checkpoints can be added. The important property here is idempotence: calling the function multiple times should not make things worse.

```python
def main():
    user = ensure_user(USER)
    if not user:
	    raise Exception("Failed to create user or login an existing user")
	else:
		save_user(user)
	
	token_extraction_try = 0
	while (token_extraction_try < 5):
		token = get_token(user)
		if token:
			save_token(token)
			break
		else:
			token_extraction_try += 1
	...
```

At each stage, when a certain asset is acquired, it's good practice to save the result in order to possibly resume from a last known good state if needed or desired. Moving the mental model from a linear flow to stages increases the complexity of the code, but also makes the PoC less brittle and can recover from failures.

These small additions move a PoC from “a script that runs” to a process that can advance, recover, and continue. We are taking small, but needed decisions regarding the state at each stage in the process and reducing chances for failure and when there is failure, that failure is being caught and documented. Each stage influences the next until a full integrated process is born. You can decide where the stages are coded. They could all be in `main()`, grouped in functions, etc... 

## There is No One Right Structure

There is no right or wrong way here. Yes, there a best practices and coding philosophy, but this is uniquely your own. There is nothing wrong with making a decision about how something should be done and then changing it for your workflow later on. As an example, I found myself writing something like the following many times in a PoC. I eventually built a function to check response 

```python
response = client.get(endpoint)
if response.status_code != 200:
	raise Exception(f"Failed <insert reason or objective>: {response.status_code})
```

codes so I could log and raise an exception if needed. This kind of refactoring isn’t about cleanliness, it’s about making failures explicit and consistent across stages. 

```python
def check_response(
    response: httpx.Response,
    logger,
    status_code: int,
    action: str,
    exc_type: Type[Exception] = ValueError,
) -> None:
    """
    Validate response status == 200. Otherwise log and raise.

    Parameters:
        response: httpx.Response
        logger: OffsecLogger
        action: str - description of the action, e.g. "register user"
        exc_type: Exception class to raise on failure
    """
    if response.status_code != status_code:
        logger.error(f"Unable to {action}: {response.text}")
        raise exc_type(f"{action.capitalize()} failed: {response.status_code}")

```

that I could call after most requests to endpoints. I could have made a class or another module for

```python
response = httpx.post("https://api.example.com/register", json=payload)
check_response(
    response, 
    logger, 
    status_code=201, 
    action="register user"
)
```

dealing with status code checks. I decided to keep this one compact and in the PoC. All of this is up to you. What is readable for you and your target audience. What if some stage fails, can you recover? Do you want to have ready code to deal with possible failures on the exam which can back-off and recover? It's up to you.

At this point, we have a way to reason about exploit execution as a sequence of stages rather than a fragile, linear script. Once retries, branching, and persistence enter the picture, the next problem becomes visibility: understanding what happened during a run, which stage produced which result, and why the exploit made certain decisions. Print statements quickly become noise in this model. In the next article, we’ll introduce a lightweight, exploit-focused logging utility, OffsecLogger, and show how structured, stage-aware logging complements this control-flow mindset without turning a PoC into an overengineered application.


