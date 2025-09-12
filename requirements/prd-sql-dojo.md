# PRD: SQL Dojo

Created: Sep 8, 2025  
Last Updated: Sep 10, 2025

# Overview

This is the Product Requirements Document (PRD) for a web application that helps Product Managers practice writing SQL queries with exercises of varying difficulty.

## Business Model

The app will have a freemium business model. A few exercises will be available for free, while the remainder will be behind a paywall.

# Features

## Summary

* Minimum 100 SQL exercises of varying difficulty  
* Gemini LLM API validation for user’s answers for each exercise (no stored solutions or SQL engine or rendering needed)  
* Exercise listing table with filtering capabilities (filter by difficulty, category, completion status) and real-time search capabilities  
* Individual progress tracking of the user’s status for each exercise (Not Started, Solved, Error)  
* Live interview practice generator (5 random exercises of varying difficulty)  
  * Query unsolved exercises for user \- if not enough unsolved exercises are available, select from solved ones  
  * Stratify by difficulty (2 beginner, 2 intermediate, 1 advanced)    
  * Randomize within difficulty tiers  
  * Present sequentially

## Exercise Pages

* We will have a templated Exercise page that will support all of our SQL exercises  
* Every exercise page will have a two column view  
  * The left column will have the Exercise title, question, and 1-5 tables from the **Chinook database** containing 5-10 rows of sample data  
  * The right column will have an Input Answer box and a Submit button for the user to submit their SQL query answer  
* When the user submits their query, the application will send the SQL query to the Gemini LLM API in order to validate if the SQL syntax is valid for the exercise or not.  
* The application will receive the input from the LLM, and provide the user with feedback on the page on if the user’s query syntax is correct or incorrect

# Technical Details

## Tech Stack

* Frontend: HTML, CSS  
* Backend: Python Flask  
* APIs  
  * Data storage: Supabase  
  * Billing: Stripe  
  * LLM: Gemini 1.5 Flash

## Code Values

* Production ready code that is lighting fast, secure, and easy to maintain  
* Separation of concerns \- HTML/CSS/JS/Python cleanly separated  
* DRY principle \- No duplicate data maintenance  
* Less code \- Fewer lines to maintain  
* Scalable & Maintainable \- Reusable table definitions eliminate duplication. Template-based validation makes adding exercises easy and straightforward.  
* Extensibility: Modular design supports future features like difficulty progression, exercise recommendations, and analytics.

## Architecture Considerations

* Easily supports a minimum of 100+ exercises and 1000+ concurrent users through normalized data structure and efficient caching strategies
* Scalable exercises data structure and metadata  
* Reusable data tables (avoid duplication across exercises)  
* Generic \+ exercise-specific validation prompts  
* Some exercises will use the same exact tables, so it probably doesn’t make sense for each exercise to duplicate those table values  
* The validation prompt (on the exercises page) will always have generic prompt text that will be shared for every exercise, but it will also have exercise specific text. so it would probably make sense to have a generic prompt template that applies to all exercises combined with exercise specific prompt text.

