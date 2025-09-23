# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SQL DOJO is a Flask-based web application for practicing SQL queries. Users work through exercises with the Chinook database schema, submitting SQL queries that are validated using Google's Gemini AI model.

## Development Commands

### Running the Application
```bash
uv run app.py
```
The app runs on port 5000 with debug mode enabled.

### Environment Setup
1. Install dependencies: `uv sync` (uses pyproject.toml and creates virtual environment automatically)
2. Create `.env` file with `GEMINI_API_KEY=your_api_key_here`
3. The app requires a valid Google Gemini API key to function

### Production Environment Variables
- `GEMINI_API_KEY` - Required: Google Gemini API key for SQL validation
- `FLASK_ENV=development` - Optional: Enable debug mode and pretty-printed logs

### Development Tool Usage
- Always use `uv` to manage dependencies instead of `pip`
- Use `uv run` to execute Python files instead of `python` directly
- Use `uv sync` to install dependencies and sync the virtual environment
- Use `uv add <package>` to add new dependencies instead of `pip install`
- Use `uv remove <package>` to remove dependencies

## Architecture

### Core Components

**app.py** - Main Flask application with three routes:
- `/` - Exercise list page (renders index.html with all exercises)
- `/exercise/<int:exercise_id>` - Individual exercise page
- `/check-sql` - POST endpoint that validates user SQL queries using Gemini AI

**exercises.py** - Exercise data and configuration:
- `EXERCISES` dict contains exercise definitions with validation prompts
- `CHINOOK_TABLES` contains sample data from Chinook database (10 rows per table)
- `get_exercise()` resolves table references and returns exercise data
- `get_all_exercises()` returns all available exercises

### Frontend Structure

**Templates** (Jinja2):
- `templates/index.html` - Exercise listing table
- `templates/exercise.html` - Exercise interface with question, sample data tables, and SQL input
- `templates/header.html` - Shared header component

**Static Assets**:
- `static/styles.css` - All application styling

### Exercise Validation Flow

1. User submits SQL query via JavaScript fetch to `/check-sql`
2. Backend retrieves exercise validation prompt from `exercises.py`
3. Prompt is formatted with user's query and sent to Gemini AI
4. Gemini responds with "CORRECT:" or "INCORRECT:" prefix + explanation
5. Response parsed and returned as JSON to frontend

### Database Schema

Uses Chinook database tables: artist, album, track, genre, media_type, customer, employee. Each table has sample data (10 rows) stored in `CHINOOK_TABLES` dict for display to users.

## Key Implementation Details

- Exercise validation prompts are stored as formatted strings in `exercises.py`
- Table references in exercises are resolved by `get_exercise()` to include actual sample data
- Frontend uses vanilla JavaScript for AJAX submissions
- Error handling covers missing exercises, empty queries, and API failures
- CORS is enabled for potential future API usage
