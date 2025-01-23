# Digital Fridge App

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**
- [Digital Fridge App](#digital-fridge-app)
    - [Problem Statement](#problem-statement)
    - [Project Overview](#project-overview)
    - [Learning Objectives](#learning-objectives)
    - [Setup](#setup)
        - [Install Git](#install-git)
        - [Downloading Repository](#downloading-repository)
        - [Go to Project Folder](#go-to-project-folder)
    - [Create Virtual Environment](#create-virtual-environment)
    - [Brief Overview of Flask Project Structure](#brief-overview-of-flask-project-structure)
    - [Project Features](#project-features)
        - [Inventory Management](#inventory-management)
        - [Recipe Suggestions](#recipe-suggestions)
        - [Notification System](#notification-system)
    - [How to Use the App](#how-to-use-the-app)
        - [Initial Setup](#initial-setup)
        - [Running the App](#running-the-app)
    - [Expected Output](#expected-output)
    - [Troubleshooting](#troubleshooting)
    - [References](#references)
    - [Link to Devpost](#link-to-devpost)
<!-- markdown-toc end -->

## Problem Statement

How might we reduce household food waste by utilizing existing technology to help families track the contents of their fridge, receive notifications about expiring items, and ensure that food is used before spoiling, thus minimizing waste and reducing the risk of foodborne illness?

### Problem 1: Food Waste
**The Issue:** People frequently throw away food that has passed its expiry date. This contributes to significant financial loss and environmental waste.

**Impact:**
- Households often discard food simply because they forget about it or don’t realize it has expired.
- This leads to unnecessary spending and resource waste.
- Food waste also strains the environment, as food production requires vast amounts of energy, water, and land.

### Problem 2: Foodborne Illness
**The Issue:** Consuming expired food, often due to poor storage or inventory management, increases the risk of foodborne illnesses.

**Impact:**
- Spoiled or improperly stored food can lead to health risks, such as food poisoning.
- Poor fridge organization and unnoticed expired food can result in unintentional consumption of unsafe products.

## Project Overview

The Digital Fridge App is a web-based application designed to tackle household food waste and the risk of foodborne illness. It utilizes a simple interface and AI-powered features to help users manage their fridge contents, receive reminders about expiring items, and access recipes that prioritize ingredients close to their expiration dates.

## Learning Objectives

By the end of this project, you should be able to:
- Create a web application using the Flask web framework.
- Integrate with the Gemini API for conversational AI.
- Use a SQLite database to manage users, chat history, and pantry items.
- Build a user interface with HTML and CSS.
- Handle data through forms.

## Setup

### Install Git

You need to have Git to clone the project. Download and install the software according to your OS:
- Windows: [Git for Windows](https://git-scm.com/download/win)
- Mac OS: [Git for MacOS](https://git-scm.com/download/mac)

### Downloading Repository

Clone the project repository from GitHub. On your terminal or Git Bash, type the following:

```shell
git clone <YOUR_REPOSITORY_URL>
```

### Go to Project Folder

Navigate to the project folder:

```shell
cd <YOUR_PROJECT_FOLDER>
```

The last command should output the following, among other files:
- `app/`
- `application.py`
- `requirements.txt`

### Create Virtual Environment

Open your terminal and follow these steps:

1. Go to the root folder of your project:
   ```shell
   cd <YOUR_PROJECT_FOLDER>
   ```
2. Install the `pipenv` package if not already installed:
   ```shell
   python -m pip install --user pipenv
   ```
3. Install the required packages:
   ```shell
   python -m pipenv install
   ```
4. Activate the virtual environment:
   ```shell
   python -m pipenv shell
   ```
   You should see the name of your project in the prompt (e.g., `(YOUR_PROJECT_FOLDER)`).

To exit the virtual environment at the end of the project, type:
```shell
exit
```

## Brief Overview of Flask Project Structure

The project structure follows Flask conventions:

```
<YOUR_PROJECT_FOLDER>/
  app/
    __init__.py
    forms.py
    models.py
    routes.py
    utils.py
    static/
      css/
    templates/
      base.html
      chat.html
      login.html
      register.html
  application.py
  requirements.txt
```

### Key Files and Folders
- `application.py`: Main entry point for the application.
- `app/__init__.py`: Initializes the Flask app, SQLAlchemy, and Flask-Migrate.
- `app/forms.py`: Form classes for user input.
- `app/models.py`: SQLAlchemy models for database tables.
- `app/routes.py`: Application URLs and their logic.
- `app/utils.py`: Helper functions for the application.
- `app/static/css/`: CSS files for styling.
- `app/templates/`: HTML templates for the web app.

## Project Features

### Inventory Management
Allows users to add ingredients to their pantry, including:
- Name
- Category
- Weight
- Expiration Date
- Calories

### Recipe Suggestions
- Integrates with the Gemini API.
- Suggests recipes based on pantry items and history.
- Prioritizes ingredients nearing expiration to reduce food waste.

### Notification System
Users receive notifications about products nearing their expiration dates.

## How to Use the App

### Initial Setup

Before running the application for the first time, set up the database:

1. Ensure you are in your virtual environment.
2. Navigate to your root folder in the terminal.
3. Run the following commands:
   ```shell
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
4. Add your Google Gemini API Key to the `GOOGLE_API_KEY` variable in `app/llm.py`.
5. Create the agent JSON file inside the `agents` folder.

### Running the App

1. Make sure you are inside your virtual environment and in your root folder.
2. Run the command:
   ```shell
   flask run
   ```
3. Access the app at the address shown in the output, usually `http://127.0.0.1:5000/`.

### App Walkthrough

- **Login/Register**: Create a new account or log in with existing credentials.
- **Add Pantry Items**: Use the "Inventory" page to add ingredients, including details like name, category, weight, expiration date, and calories.
- **Get Recipe Suggestions**: Select ingredients on the "Recipes" page to receive recipe ideas.
- **Chat with MasterChef**: Use the chatbot to get recipe assistance based on your pantry items.

## Expected Output

The application should provide:
- A functional user interface.
- Features for inventory management, recipe suggestions, and notifications.
- A chatbot for recipe assistance.

## Troubleshooting

- **ModuleNotFoundError:** Ensure the virtual environment is activated using `python -m pipenv shell`.
- **App doesn’t update:** Save all files and do a hard refresh (CTRL+Shift+R or CMD+Shift+R).
- **UndefinedError in Jinja2:** Verify all variables passed to `render_template` are correctly referenced in HTML.

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Google Gemini API Documentation](https://cloud.google.com/ai-platform/)

## Link to Devpost
- https://devpost.com/software/833070/joins/xCF0Vtmq8NORwo7xLBjcpg