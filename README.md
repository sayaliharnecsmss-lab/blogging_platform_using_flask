# The Marginalia — Blogging Platform Using Flask

A beginner-friendly blogging website built with Python, Flask, Flask-SQLAlchemy, Flask-Login, SQLite, Bootstrap, HTML, CSS, and JavaScript.

## What you can do

- Register, log in, and log out. Passwords are stored as secure hashes.
- Publish, edit, and delete your own stories; posts belong to their author.
- Browse and search stories, or filter by category.
- Leave comments while signed in.
- Manage your posts from a personal dashboard.
- Use CSRF protection on forms and confirmation prompts before deleting.

## Project structure

```text
blogging-platform-flask/
├── blog/
│   ├── __init__.py       # App factory, extensions, database setup, CLI commands
│   ├── auth.py           # Registration, login, and logout
│   ├── models.py         # User, Post, Category, and Comment tables
│   └── posts.py          # Homepage, dashboard, stories, and comments
├── instance/             # Created automatically; SQLite database lives here
├── static/
│   ├── css/style.css     # Responsive visual design
│   └── js/main.js        # Delete confirmation
├── templates/            # Jinja HTML pages
├── tests/                # Automated feature and access-control tests
├── .vscode/settings.json # Selects this project's virtual environment
├── .env.example          # Example local configuration
├── .gitignore
├── requirements.txt
├── run.py                # Development server entry point
└── README.md
```

## 1. Open the project in VS Code

Choose **File → Open Folder...**, then select `C:\Users\DELL\.copilot\blogging-platform-flask`. Open the integrated terminal with **Terminal → New Terminal**.

## 2. Create and activate a virtual environment

Run these commands in the VS Code terminal from the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell says script execution is disabled, use this command for the current terminal only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

For Command Prompt, activate with:

```bat
.venv\Scripts\activate.bat
```

The project includes a VS Code setting for the `.venv` interpreter. If VS Code does not select it automatically, press **Ctrl+Shift+P**, choose **Python: Select Interpreter**, then choose the interpreter inside this project's `.venv` folder.

## 3. Install packages

With the environment activated:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` lists Flask, Flask-Login, Flask-SQLAlchemy, Flask-WTF, email-validator, python-dotenv, and pytest.

## 4. Configure and initialize

The app runs locally without an environment file: it creates an SQLite database at `instance/blog.db` and adds the default categories on startup. To set a private signing key, copy the example and edit `.env`:

```powershell
Copy-Item .env.example .env
```

Change `SECRET_KEY` in `.env` to a long, random value. Keep `.env` private; it is ignored by Git. The included fallback secret is only for local practice and must not be used for a public deployment.

The database and starter categories are initialized automatically. You may also run:

```powershell
flask --app run.py init-db
```

## 5. Create sample login credentials

To add the local demo account and two example stories, run:

```powershell
flask --app run.py seed-demo
```

Demo login:

- **Email:** `demo@example.com`
- **Password:** `Demo1234!`

The command is safe to repeat and will not replace an existing account's password. These public sample credentials are for local learning only. You can also register your own account from the website.

## 6. Run the website

Start the development server from the project folder:

```powershell
python run.py
```

Open the address printed in the terminal (usually `http://127.0.0.1:5000`). Stop the server with **Ctrl+C**. Flask's debug server is for local development, not public hosting.

## 7. Run the tests

```powershell
python -m pytest
```

The tests cover password hashing and login, creating/searching/filtering posts, comments, edit/delete ownership, and login redirect safety.

## Troubleshooting

- **`python` is not recognized:** install Python from python.org, enable the option to add Python to PATH, restart VS Code, and try `python --version`.
- **`Activate.ps1` is blocked:** use the process-scoped execution-policy command above; it applies only to the current terminal.
- **`ModuleNotFoundError`:** activate `.venv` and run `python -m pip install -r requirements.txt` again.
- **Port 5000 is already in use:** stop the other local server, or temporarily change the `app.run(...)` call in `run.py` to `app.run(port=5001, ...)`.
- **Starting over:** stop the server, close the app, and remove only `instance\blog.db` if you want to erase local posts and accounts. The next launch recreates an empty database with default categories.

## Learning map

Start with `run.py` and `blog/__init__.py` to see how Flask starts. Read `blog/models.py` for database tables, `blog/auth.py` for account handling, and `blog/posts.py` for blog routes. Templates are in `templates/`, and the visual design is in `static/css/style.css`.
