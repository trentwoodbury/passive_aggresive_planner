# Passive Aggressive Planner

A "premium" To-Do list application that judges you while you work. It uses an LLM to parse your tasks and adds a touch of passive-aggression to your day.

## Features
- **Smart Parsing**: Type natural language (e.g., "Do the dishes by tonight") and it extracts the summary and due date.
- **Passive Aggressive Flair**: The AI provides a snarky comment on your task.
- **Premium UI**: Glassmorphism design with soothing (yet mocking) background animations.

## Prerequisites
- Python 3.8+
- A Google Cloud API Key for Gemini

## Setup

1.  **Clone the repository** (if you haven't already).

2.  **Create a Virtual Environment** (recommended):
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables**:
    Create a `.env` file in the root directory and add your Google API key:
    ```env
    GOOGLE_API_KEY=your-google-api-key-here
    ```

## Running the Application

1.  **Start the Server**:
    ```bash
    python main.py
    ```
    OR
    ```bash
    uvicorn main:app --reload
    ```

2.  **Open the App**:
    Visit `http://localhost:8000` in your web browser.

## Usage
Type your task into the input field and press Enter or click "Add Task". Prepare to be judged.