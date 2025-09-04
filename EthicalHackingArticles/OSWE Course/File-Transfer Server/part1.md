---

title: "Building a Minimal File-Transfer Server: Part 1 – Why and Where to Begin"

description: "Starting a guided series to understand Flask, threading, and design choices by building a file-transfer microservice step by step."

tags: [oswe, web-300, poc, flask, python]

---
# Part 1: Building a Minimal File-Transfer Server

### **Why and Where to Begin**

This series will walk through the process of **building a minimal file-transfer server** in Python. The end goal is to understand the **full `[FileTransferServer](https://github.com/rogdooley/OSWE/blob/main/Utilities/file_transfer_server.py)` class** I have been using for OSWE/WEB-300 style exploit development.

Rather than just drop the code or a link with minimal explanation, I’m going to walk through what went into creating this. If you’re aware of the OSWE course, you’ll know that for the exam one is required to write a complete exploit script such that, when run, it results in remote code execution and a shell on the machine where the web application runs. Standing up a web server alongside your code is easy enough (e.g., `python3 -m http.server`), but what if you only want that server running for the portion of the exploit where it is needed? Having a single terminal window running the exploit without needing to manually start a server, drop in the payload, or configure a listener, is far smoother.


---

## Why Build This at All?


My initial thought when I started creating this was to have an easy to use one-shot web server that would either allow for a simulated user to interact with a hosted file or have the ability to upload a file from the "victim's" machine to mine. I wanted control over these interaction or interactions so that once these were complete, the server could shut itself down rather than remain running. I imagined that if I were using this for an engagement, if any interaction was logged, the server would be unreachable after delivery, making forensics  harder. 

For the WEB-300 course, students must build exploit scripts that handle everything from initial access to achieving RCE without manual steps once the script begins. While I could have invoked a basic Python webserver (`python3 -m http.server`), that felt clumsy. As I developed this class, I started imagining scenarios where extra functionality would be useful: handling base64-encoded data, saving exfiltrated content, or shutting the server down with a localhost-only REST call. Some of those features I haven’t used yet, but they’re available if needed.


---

We'll use [Flask](https://flask.palletsprojects.com/en/stable/) as the web server since it's lightweight and easy to work with.  Flask will need to be installed via `pip` or  some other method. I recommend creating a virtual environment first.

## Step 1 – The Simplest Flask Server

  
Before we think about uploads, downloads, or exfiltration, we need the **most basic Flask server** that can respond to a request. The program below imports the Flask class, creates an instance, and maps the `/` route to the `index` function. Save this as `server.py`.

Flask uses the term _route_ for a URL path that maps to a function. In the example below,  `/` is the route and `index()` is the function that responds to it.


```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
	return "File Transfer Server is running!"

if __name__ == "__main__":
	app.run(port=8888)
```


Run this file from a terminal:
```python
python server.py
```

You should see output like the following if you visit `http://127.0.0.1:8888/` in a web browser:
```bash
❯ python3 server.py
 * Serving Flask app 'server'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:8888
Press CTRL+C to quit
127.0.0.1 - - [03/Sep/2025 21:43:23] "GET / HTTP/1.1" 200 -
```
If you see an error, you might need to make sure the line starting with `return` or `app.run` are indented with a tab or 4 spaces.

And the browser will display something like this:
![Web Browser View][Images/Part1/01-webbrowser.png]

Now, change the route to:
```python
@app.route("/new-location")
```
Restart the server and visit http://127.0.0.1:8888/. You’ll get an error page like this:

![Not Found][Images/Part1/03-browser-response.png]

Change the URL to http://127.0.0.1:8888/new-location and the return value will be displayed:

![New URL][Images/Part1/04-new-location.png]

We could even add multiple routes:
```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
	return "File Transfer Server is running!"
	
@app.route("/new-route")
def index():
	return "This is a new route location!"

if __name__ == "__main__":
	app.run(port=8888)
```

If you name or label routes with gibberish, discovering the exact URLs by directory busting becomes harder for defenders. By configuring specific routes, we can define endpoints for downloads, uploads, or both — while keeping them obscure. Another aspect we’ll develop later is that, after a payload is transferred (once or a few times), the server can automatically shut itself down.

For further explorations, take a look at the [Flask Documentation](https://flask.palletsprojects.com/en/stable/)and make some changes to above code, or write your own. Change the listening port to something other than `8888`. Map a route to a directory. There's plenty to experiment with, even in this simple example.