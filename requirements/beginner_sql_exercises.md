# SQL Dojo - Beginner Exercise Template

## **BEGINNER LEVEL (60 exercises)**

### Basic SELECT Operations (10 exercises)
1. SELECT single column from artist table (artist name)
2. SELECT 2 columns from album table (title, artist_id)
3. SELECT 3 columns from track table (name, milliseconds, unit_price)
4. SELECT 4 columns from customer table (first_name, last_name, city, country)
5. SELECT all columns from genre table (SELECT *)
6. SELECT all columns from media_type table (SELECT *)
7. SELECT with column aliases (artist.name AS artist_name)
8. SELECT with string concatenation (first_name || ' ' || last_name AS full_name)
9. SELECT DISTINCT values from country column
10. SELECT DISTINCT values from genre names

### Basic WHERE Filtering (15 exercises)
11. WHERE with single text condition (country = 'USA')
12. WHERE with single numeric condition (customer_id = 5)
13. WHERE with equality operator (genre_id = 1)
14. WHERE with inequality operators (unit_price > 0.99)
15. WHERE with less than condition (milliseconds < 200000)
16. WHERE with greater than or equal (unit_price >= 1.00)
17. WHERE with less than or equal (milliseconds <= 300000)
18. WHERE with not equals (country != 'USA' or country <> 'USA')
19. WHERE with IS NULL (company IS NULL)
20. WHERE with IS NOT NULL (fax IS NOT NULL)
21. WHERE with text comparison (city = 'New York')
22. WHERE filtering dates (hire_date = '2002-08-14')
23. WHERE with multiple conditions preview (country = 'Canada' AND city = 'Calgary')
24. WHERE filtering on calculated fields (unit_price * 100 > 150)
25. WHERE with case sensitivity (name = 'AC/DC')

### Logical Operators: AND, OR, NOT (10 exercises)
26. WHERE with AND - two conditions (country = 'USA' AND state = 'CA')
27. WHERE with AND - three conditions (genre_id = 1 AND unit_price > 0.99 AND milliseconds > 200000)
28. WHERE with OR - two conditions (country = 'USA' OR country = 'Canada')
29. WHERE with OR - three conditions (genre_id = 1 OR genre_id = 2 OR genre_id = 3)
30. WHERE with mixed AND/OR (country = 'USA' AND (state = 'CA' OR state = 'NY'))
31. WHERE with NOT operator (NOT country = 'USA')
32. WHERE with NOT NULL (NOT company IS NULL)
33. WHERE with parentheses for complex logic ((country = 'USA' OR country = 'Canada') AND unit_price > 0.99)
34. WHERE combining all operators (NOT (country = 'USA' AND state = 'CA') OR unit_price < 1.00)
35. WHERE with nested conditions (country = 'USA' AND (city = 'New York' OR city = 'Los Angeles'))

### BETWEEN and IN Operators (8 exercises)
36. WHERE with BETWEEN for numbers (unit_price BETWEEN 0.99 AND 1.99)
37. WHERE with BETWEEN for dates (hire_date BETWEEN '2002-01-01' AND '2003-12-31')
38. WHERE with BETWEEN inclusive range (customer_id BETWEEN 1 AND 10)
39. WHERE with NOT BETWEEN (unit_price NOT BETWEEN 0.50 AND 1.00)
40. WHERE with IN operator (country IN ('USA', 'Canada', 'France'))
41. WHERE with IN for numbers (genre_id IN (1, 2, 3))
42. WHERE with NOT IN operator (country NOT IN ('USA', 'Canada'))
43. WHERE combining BETWEEN and IN (unit_price BETWEEN 0.99 AND 1.99 AND genre_id IN (1, 2))

### LIKE Pattern Matching (7 exercises)
44. LIKE with starts with pattern (name LIKE 'A%')
45. LIKE with ends with pattern (email LIKE '%@gmail.com')
46. LIKE with contains pattern (name LIKE '%rock%')
47. LIKE with single character wildcard (name LIKE 'A_C')
48. LIKE with multiple patterns (name LIKE 'A%' OR name LIKE 'B%')
49. LIKE with case variations (city LIKE '%york%' - assuming case insensitive)
50. NOT LIKE pattern (name NOT LIKE '%Inc%')

### ORDER BY Sorting (10 exercises)
51. ORDER BY single column ascending (artist name ASC)
52. ORDER BY single column descending (unit_price DESC)
53. ORDER BY text column alphabetically (album title)
54. ORDER BY numeric column (milliseconds DESC)
55. ORDER BY date column (hire_date ASC)
56. ORDER BY multiple columns (last_name ASC, first_name ASC)
57. ORDER BY with WHERE condition (WHERE country = 'USA' ORDER BY city)
58. ORDER BY with LIMIT (top 5 most expensive tracks)
59. ORDER BY using column numbers (ORDER BY 1, 2)
60. ORDER BY mixed ASC/DESC (last_name ASC, hire_date DESC)

---

## **Exercise Categories:**
- **Basic Queries** (SELECT fundamentals)
- **Filtering** (WHERE clause variations)
- **Logical Operations** (AND, OR, NOT)
- **Range & List Filtering** (BETWEEN, IN)
- **Pattern Matching** (LIKE wildcards)
- **Sorting** (ORDER BY variations)

## **Learning Progression:**
1. **Exercises 1-10**: Master basic data retrieval
2. **Exercises 11-25**: Learn filtering fundamentals
3. **Exercises 26-35**: Complex logical conditions
4. **Exercises 36-43**: Range and list operations
5. **Exercises 44-50**: String pattern matching
6. **Exercises 51-60**: Data sorting and presentation

## **Business Context:**
Each exercise uses realistic Product Manager scenarios:
- Customer analysis and segmentation
- Product catalog exploration
- Sales data filtering
- Employee directory searches
- Music library management
- Revenue and performance analysis