"""
Exercise configuration data structure
Each exercise contains all the data needed to render the page and validate answers
"""

EXERCISES = {
    1: {
        "title": "Users by plan type",
        "question": "Write a query to count users by plan type. The output should be sorted in ascending order based on the plan type.",
        "tables": [
            {
                "name": "users",
                "data": [
                    {"user_id": 1, "email": "alice@email.com", "signup_date": "2024-01-15", "plan_type": "premium"},
                    {"user_id": 2, "email": "bob@email.com", "signup_date": "2024-02-01", "plan_type": "free"},
                    {"user_id": 3, "email": "carol@email.com", "signup_date": "2024-01-20", "plan_type": "enterprise"},
                    {"user_id": 4, "email": "david@email.com", "signup_date": "2024-03-10", "plan_type": "premium"},
                    {"user_id": 5, "email": "eve@email.com", "signup_date": "2024-02-15", "plan_type": "free"}
                ]
            },
            {
                "name": "plans", 
                "data": [
                    {"plan_id": 1, "plan_name": "Free Tier", "plan_type": "free", "plan_created_date": "2023-12-01", "plan_status": "active"},
                    {"plan_id": 2, "plan_name": "Premium Plan", "plan_type": "premium", "plan_created_date": "2023-12-01", "plan_status": "active"},
                    {"plan_id": 3, "plan_name": "Enterprise Solution", "plan_type": "enterprise", "plan_created_date": "2023-12-01", "plan_status": "active"},
                    {"plan_id": 4, "plan_name": "Legacy Basic", "plan_type": "free", "plan_created_date": "2023-06-15", "plan_status": "deprecated"},
                    {"plan_id": 5, "plan_name": "Pro Plus", "plan_type": "premium", "plan_created_date": "2024-01-15", "plan_status": "beta"}
                ]
            }
        ],
        "validation_prompt": """
        You are a SQL validator. A user is trying to solve this exercise:
        
        Exercise: "Write a query to count users by plan type. The output should be sorted in ascending order based on the plan type."
        
        Table schema:
        users table with columns: user_id, email, signup_date, plan_type
        Sample data shows plan_type values: premium, free, enterprise
        
        User's SQL query: {user_query}
        
        Please evaluate if this query correctly solves the exercise. The correct solution should:
        1. Group users by plan_type
        2. Count the number of users in each group
        3. Sort the results in ASCENDING order by plan_type (NOT descending)
        4. Use proper SQL syntax
        
        IMPORTANT: Pay special attention to the sorting requirement. The results MUST be sorted in ascending order by plan_type. If the query uses DESC or descending order, it is INCORRECT.
        
        Respond with exactly one of these formats:
        - If correct: "CORRECT: [brief explanation of why it's correct]"
        - If incorrect: "INCORRECT: [brief explanation of what's wrong and hint for improvement]"
        
        Keep your response concise and educational.
        """
    }
}

def get_exercise(exercise_id):
    """Get exercise data by ID"""
    return EXERCISES.get(exercise_id)

def get_all_exercises():
    """Get all exercises"""
    return EXERCISES