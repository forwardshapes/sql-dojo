# SQL Dojo: Beginner Exercise Implementation Plan

**Date:** September 10, 2025  
**Status:** In Progress (3/60 exercises completed)

## Overview

This document outlines our strategy for implementing 60 beginner-level SQL exercises based on the requirements in `requirements/beginner_sql_exercises.md`. The exercises will follow a logical progression from basic SELECT operations to more complex filtering and sorting.

## Current Architecture Assessment

### Strengths ✅
- **Well-structured data separation**: `CHINOOK_TABLES` and `EXERCISES` cleanly separated
- **Reusable table references**: Exercises reference tables via `table_refs`, avoiding duplication
- **Template-based validation**: Each exercise has custom `validation_prompt` for Gemini AI
- **Scalable resolution**: `get_exercise()` dynamically resolves table references

### Architecture Supports Scaling ✅
The current structure is well-designed for scaling to 60+ exercises without modifications.

## Implementation Strategy

### 1. Batch Generation Approach
Generate exercises in 6 category batches following the progression:

1. **Basic SELECT Operations** (Exercises 1-10) ✅ Started
   - Exercise 1: ✅ Artist Names (SELECT single column)
   - Exercise 2: ✅ Album Details (SELECT 2 columns)  
   - Exercise 3: ✅ Track Information (SELECT 3 columns)
   - Exercises 4-10: 🔄 Pending

2. **Basic WHERE Filtering** (Exercises 11-25) 🔄 Pending
3. **Logical Operators: AND, OR, NOT** (Exercises 26-35) 🔄 Pending  
4. **BETWEEN and IN Operators** (Exercises 36-43) 🔄 Pending
5. **LIKE Pattern Matching** (Exercises 44-50) 🔄 Pending
6. **ORDER BY Sorting** (Exercises 51-60) 🔄 Pending

### 2. Data Structure Requirements

For each exercise, we generate:
- **title**: Descriptive, business-focused titles
- **category**: Mapped from 6 categories in requirements
- **question**: Full question text with realistic Product Manager scenarios
- **table_refs**: Appropriate Chinook tables for each SQL concept
- **validation_prompt**: Exercise-specific validation criteria for Gemini AI

### 3. Template-Based Validation Prompts

Create consistent validation prompt templates for each category while allowing exercise-specific criteria.

### 4. Table Reference Optimization

Most beginner exercises use 1-3 core tables (`artist`, `album`, `track`, `customer`), maximizing our existing `CHINOOK_TABLES` data.

## Progress Tracking

### Completed Exercises (3/60)

| Exercise | Title | Category | Table(s) | Status |
|----------|--------|----------|----------|---------|
| 1 | Artist Names | Basic SELECT Operations | artist | ✅ Complete |
| 2 | Album Details | Basic SELECT Operations | album | ✅ Complete |
| 3 | Track Information | Basic SELECT Operations | track | ✅ Complete |

### Next Steps

1. **Complete Basic SELECT Operations (Exercises 4-10)**
   - Exercise 4: SELECT 4 columns from customer table
   - Exercise 5: SELECT * from genre table  
   - Exercise 6: SELECT * from media_type table
   - Exercise 7: Column aliases
   - Exercise 8: String concatenation
   - Exercise 9: DISTINCT values from country
   - Exercise 10: DISTINCT genre names

2. **Begin WHERE Filtering Category (Exercises 11-25)**

3. **Continue through remaining categories systematically**

## Technical Validation

### Architecture Test Results ✅
- ✅ Current EXERCISES dictionary structure supports new exercises seamlessly
- ✅ `get_exercise()` function resolves table references correctly
- ✅ Template system displays new exercises properly in index.html
- ✅ Validation prompts format correctly for Gemini AI

### Code Quality Adherence ✅
Following PRD code values:
- ✅ **DRY Principle**: Reusing CHINOOK_TABLES data across exercises
- ✅ **Scalable & Maintainable**: Template-based validation, modular structure
- ✅ **Separation of Concerns**: Clean data/logic/template separation
- ✅ **Extensibility**: Easy to add new exercises and categories

## Future Enhancements

### Suggested Additions
- **Difficulty field**: Add optional `difficulty` field for future filtering capabilities
- **Prerequisites**: Consider adding `prerequisites` array for exercise dependencies
- **Hints system**: Add progressive hints for stuck users

### Business Context Integration
Each exercise includes realistic Product Manager scenarios:
- Customer analysis and segmentation
- Product catalog exploration  
- Sales data filtering
- Employee directory searches
- Music library management
- Revenue and performance analysis

## Risk Mitigation

### Tested Approach ✅
- Started with single exercise replacement (Exercise 1)
- Validated architecture compatibility
- Confirmed template system works with new structure
- Established consistent validation prompt patterns

### Quality Assurance
- Each exercise follows established validation prompt template
- Business context scenarios maintain consistency
- Column names and table references match Chinook schema exactly
- Progressive difficulty within each category

---

**Next Action Items:**
1. Complete remaining Basic SELECT Operations exercises (4-10)
2. Begin WHERE Filtering category exercises (11-25)
3. Continue systematic implementation through all 6 categories
4. Test exercises with actual Gemini AI validation
5. Update index.html placeholder ranges as exercises are added