"""
AI Service for generating questions and explanations
"""
import os
import json
import random
from typing import Dict, List, Optional
from anthropic import Anthropic
from app import redis_client


class AIService:
    """Service for AI-powered question generation and explanations"""

    def __init__(self):
        try:
            self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            self.model = "claude-haiku-4-20250514"
            self.enabled = True
        except Exception as e:
            print(f"Warning: AI service failed to initialize: {e}")
            print("Falling back to non-AI mode")
            self.client = None
            self.enabled = False

    def generate_question_from_template(self, template) -> Dict:
        """
        Generate a question variation from a template

        Args:
            template: QuestionTemplate object

        Returns:
            Dict with question_text, correct_answer, choices, explanation
        """
        # Generate random values for variables
        variables = {}
        if template.variables:
            for var_name, var_config in template.variables.items():
                variables[var_name] = random.randint(
                    var_config.get('min', 1),
                    var_config.get('max', 10)
                )

        # Check cache first
        cache_key = f"question:{template.id}:{json.dumps(variables, sort_keys=True)}"
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        # Fill in template with variables
        question_text = template.question_template
        for var_name, var_value in variables.items():
            question_text = question_text.replace(f"{{{var_name}}}", str(var_value))

        # For multiple choice questions, generate choices and explanation
        if template.question_type == 'single_choice':
            result = self._generate_choices_and_explanation(
                question_text,
                template,
                variables
            )
        else:
            # For numeric or fill-in-the-blank, calculate correct answer
            correct_answer = self._calculate_answer(template, variables)
            result = {
                'question_text': question_text,
                'correct_answer': correct_answer,
                'choices': None,
                'explanation': template.explanation_template or '',
                'variables_used': variables
            }

        # Cache the result (1 day TTL)
        redis_client.setex(cache_key, 86400, json.dumps(result))

        return result

    def _calculate_answer(self, template, variables: Dict) -> str:
        """Calculate correct answer from template formula"""
        # Simple example for quadratic equations: ax² + bx + c = 0
        # In real implementation, use eval() safely or sympy

        if 'quadratic' in template.question_template.lower():
            a = variables.get('a', 1)
            b = variables.get('b', 0)
            c = variables.get('c', 0)

            # Quadratic formula: x = (-b ± √(b²-4ac)) / 2a
            discriminant = b ** 2 - 4 * a * c
            if discriminant >= 0:
                x1 = (-b + discriminant ** 0.5) / (2 * a)
                x2 = (-b - discriminant ** 0.5) / (2 * a)
                return f"x₁={x1:.1f}, x₂={x2:.1f}"
            else:
                return "No real solutions"

        # Fallback: use template answer
        answer = template.correct_answer_template or ""
        for var_name, var_value in variables.items():
            answer = answer.replace(f"{{{var_name}}}", str(var_value))
        return answer

    def _generate_choices_and_explanation(
            self,
            question_text: str,
            template,
            variables: Dict
    ) -> Dict:
        """Use AI to generate answer choices and explanation"""

        correct_answer = self._calculate_answer(template, variables)

        # If AI not available, use fallback
        if not self.enabled:
            return self._fallback_choices(question_text, correct_answer, template)

        prompt = f"""Generate 4 multiple choice options (A, B, C, D) for this question.
One should be the correct answer: {correct_answer}
The other 3 should be plausible but incorrect answers.

Question: {question_text}
Correct answer: {correct_answer}

Respond with ONLY a JSON object in this format:
{{
  "choices": ["A) option1", "B) option2", "C) option3", "D) option4"],
  "correct_letter": "A",
  "explanation": "Brief explanation in Slovak (max 100 words)"
}}

Make the explanation simple and in Slovak language."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse AI response
            content = response.content[0].text.strip()
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]

            data = json.loads(content)

            return {
                'question_text': question_text,
                'correct_answer': data['correct_letter'],
                'choices': data['choices'],
                'explanation': data['explanation'],
                'variables_used': variables
            }

        except Exception as e:
            print(f"AI generation error: {e}")
            # Fallback to template-based generation
            return self._fallback_choices(question_text, correct_answer, template)

    def _fallback_choices(self, question_text: str, correct_answer: str, template) -> Dict:
        """Fallback when AI is not available"""
        return {
            'question_text': question_text,
            'correct_answer': 'A',
            'choices': [
                f"A) {correct_answer}",
                "B) Wrong answer 1",
                "C) Wrong answer 2",
                "D) Wrong answer 3"
            ],
            'explanation': template.explanation_template or 'No explanation available',
            'variables_used': {}
        }

    def generate_explanation(
            self,
            question_text: str,
            correct_answer: str,
            user_answer: str,
            subject: str = "matematika"
    ) -> str:
        """
        Generate explanation for why answer is correct/incorrect

        Args:
            question_text: The question
            correct_answer: Correct answer
            user_answer: Student's answer
            subject: Subject name

        Returns:
            Explanation text in Slovak
        """
        # Check cache first
        cache_key = f"explanation:{hash(question_text)}:{user_answer}"
        cached = redis_client.get(cache_key)
        if cached:
            return cached.decode('utf-8')

        prompt = f"""Si skúsený učiteľ predmetu {subject}. Vysvetli študentovi jeho chybu.

Otázka: {question_text}
Správna odpoveď: {correct_answer}
Odpoveď študenta: {user_answer}

Vysvetli po slovensky:
1. Prečo je správna odpoveď správna (krok po kroku)
2. Kde sa študent pomýlil
3. Ako sa takýmto chybám vyhnúť

Maximálne 150 slov, jednoduchým jazykom."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )

            explanation = response.content[0].text.strip()

            # Cache for 30 days
            redis_client.setex(cache_key, 2592000, explanation)

            return explanation

        except Exception as e:
            print(f"Explanation generation error: {e}")
            return "Vyhovenie nedostupné. Skús to znova neskôr."
