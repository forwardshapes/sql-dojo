from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
from exercises import get_exercise, get_all_exercises

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def index():
    exercises = get_all_exercises()
    return render_template('index.html', exercises=exercises)

@app.route('/exercise/<int:exercise_id>')
def exercise(exercise_id):
    exercise_data = get_exercise(exercise_id)
    if not exercise_data:
        return "Exercise not found", 404
    
    return render_template('exercise.html', exercise=exercise_data, exercise_id=exercise_id)

@app.route('/check-sql', methods=['POST'])
def check_sql():
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        exercise_id = data.get('exercise_id', 1)
        
        if not user_query:
            return jsonify({
                'success': False,
                'message': 'Please enter a SQL query.'
            })
        
        # Get exercise data
        exercise_data = get_exercise(exercise_id)
        if not exercise_data:
            return jsonify({
                'success': False,
                'message': 'Exercise not found.'
            })
        
        # Create validation prompt from exercise data
        prompt = exercise_data['validation_prompt'].format(user_query=user_query)
        
        # Send to Gemini
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Parse the response
        is_correct = result_text.startswith('CORRECT:')
        message = result_text.split(':', 1)[1].strip() if ':' in result_text else result_text
        
        return jsonify({
            'success': True,
            'correct': is_correct,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error validating query: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)