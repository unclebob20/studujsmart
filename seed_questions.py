"""
Run this to add sample question templates to the database

Usage: python seed_questions.py
"""

from app import create_app, db
from app.models.question import QuestionTemplate
from app.models.subject import Subject, Topic


def add_math_questions():
    """Add sample math questions"""

    # Get topics
    quadratic_topic = Topic.query.filter_by(slug='kvadraticke-rovnice').first()
    linear_topic = Topic.query.filter_by(slug='linearne-rovnice').first()
    pythagorean_topic = Topic.query.filter_by(slug='pythagorova-veta').first()

    if not quadratic_topic:
        print("⚠️  Topics not found. Run seed_data.py first!")
        return

    questions = [
        # Quadratic equations
        {
            'topic_id': quadratic_topic.id,
            'question_type': 'single_choice',
            'difficulty': 'medium',
            'question_template': 'Vypočítaj korene rovnice: {a}x² + {b}x + {c} = 0',
            'variables': {
                'a': {'min': 1, 'max': 3},
                'b': {'min': -10, 'max': 10},
                'c': {'min': -10, 'max': 10}
            },
            'correct_answer_template': 'Calculate using quadratic formula',
            'explanation_template': 'Použijeme vzorec: x = (-b ± √(b²-4ac)) / 2a'
        },
        {
            'topic_id': quadratic_topic.id,
            'question_type': 'single_choice',
            'difficulty': 'easy',
            'question_template': 'Vyriešte rovnicu: x² - {sum}x + {product} = 0',
            'variables': {
                'sum': {'min': 3, 'max': 10},
                'product': {'min': 2, 'max': 20}
            },
            'correct_answer_template': 'Factorize',
            'explanation_template': 'Rozložíme na súčin: (x - r₁)(x - r₂) = 0'
        },

        # Linear equations
        {
            'topic_id': linear_topic.id,
            'question_type': 'numeric',
            'difficulty': 'easy',
            'question_template': 'Vyriešte rovnicu: {a}x + {b} = {c}',
            'variables': {
                'a': {'min': 2, 'max': 10},
                'b': {'min': 1, 'max': 20},
                'c': {'min': 10, 'max': 50}
            },
            'correct_answer_template': 'x = ({c} - {b}) / {a}',
            'explanation_template': 'Prenesieme {b} na pravú stranu a delíme {a}'
        },
        {
            'topic_id': linear_topic.id,
            'question_type': 'numeric',
            'difficulty': 'easy',
            'question_template': '{a}x = {result}',
            'variables': {
                'a': {'min': 2, 'max': 12},
                'result': {'min': 10, 'max': 100}
            },
            'correct_answer_template': 'x = {result} / {a}',
            'explanation_template': 'Delíme obe strany číslom {a}'
        },

        # Pythagorean theorem
        {
            'topic_id': pythagorean_topic.id,
            'question_type': 'numeric',
            'difficulty': 'medium',
            'question_template': 'V pravouhlom trojuholníku je odvesna a = {a} cm a odvesna b = {b} cm. Vypočítaj preponu c.',
            'variables': {
                'a': {'min': 3, 'max': 12},
                'b': {'min': 4, 'max': 16}
            },
            'correct_answer_template': 'c = √({a}² + {b}²)',
            'explanation_template': 'Použijeme Pytagorovu vetu: c² = a² + b²'
        }
    ]

    for q in questions:
        template = QuestionTemplate(**q)
        db.session.add(template)

    print(f"✅ Added {len(questions)} math question templates")


def add_slovak_questions():
    """Add sample Slovak language questions"""

    # Get topics
    declension_topic = Topic.query.filter_by(slug='sklenovanie-podstatnych-mien').first()
    conjugation_topic = Topic.query.filter_by(slug='casovanie-slovies').first()

    if not declension_topic:
        print("⚠️  Slovak topics not found")
        return

    questions = [
        {
            'topic_id': declension_topic.id,
            'question_type': 'fill_blank',
            'difficulty': 'easy',
            'question_template': 'Doplň správny tvar slova "dom" v 2. páde: Vidím strechu _____',
            'variables': {},
            'correct_answer_template': 'domu',
            'explanation_template': '2. pád (genitív) od slova "dom" je "domu"'
        },
        {
            'topic_id': declension_topic.id,
            'question_type': 'single_choice',
            'difficulty': 'medium',
            'question_template': 'Aký je 4. pád slova "žena"?',
            'variables': {},
            'correct_answer_template': 'ženu',
            'explanation_template': '4. pád (akuzatív) od slova "žena" je "ženu"'
        },
        {
            'topic_id': conjugation_topic.id,
            'question_type': 'fill_blank',
            'difficulty': 'easy',
            'question_template': 'Časuj sloveso "písať" v 1. osobe jednotného čísla prítomného času: Ja _____',
            'variables': {},
            'correct_answer_template': 'píšem',
            'explanation_template': 'Sloveso "písať" v 1. osobe j.č. je "píšem"'
        }
    ]

    for q in questions:
        template = QuestionTemplate(**q)
        db.session.add(template)

    print(f"✅ Added {len(questions)} Slovak question templates")


def add_english_questions():
    """Add sample English language questions"""

    # Get topics
    present_topic = Topic.query.filter_by(slug='present-tenses').first()
    past_topic = Topic.query.filter_by(slug='past-tenses').first()

    if not present_topic:
        print("⚠️  English topics not found")
        return

    questions = [
        {
            'topic_id': present_topic.id,
            'question_type': 'single_choice',
            'difficulty': 'easy',
            'question_template': 'Choose the correct form: She _____ to school every day.',
            'variables': {},
            'correct_answer_template': 'goes',
            'explanation_template': 'V Present Simple použijeme "goes" pre 3. osobu jednotného čísla'
        },
        {
            'topic_id': present_topic.id,
            'question_type': 'fill_blank',
            'difficulty': 'easy',
            'question_template': 'Complete: I _____ (study) English.',
            'variables': {},
            'correct_answer_template': 'study',
            'explanation_template': 'V Present Simple použijeme základný tvar slovesa'
        },
        {
            'topic_id': past_topic.id,
            'question_type': 'single_choice',
            'difficulty': 'medium',
            'question_template': 'Choose the correct past tense: Yesterday, I _____ to the cinema.',
            'variables': {},
            'correct_answer_template': 'went',
            'explanation_template': '"Go" má nepravidelný tvar minulého času "went"'
        }
    ]

    for q in questions:
        template = QuestionTemplate(**q)
        db.session.add(template)

    print(f"✅ Added {len(questions)} English question templates")


def main():
    """Run all seed functions"""
    app = create_app('development')

    with app.app_context():
        print("Starting question template seeding...")

        # Check if already seeded
        count = QuestionTemplate.query.count()
        if count > 0:
            print(f"⚠️  Database already contains {count} question templates.")
            response = input("Do you want to add more? (yes/no): ")
            if response.lower() != 'yes':
                return

        add_math_questions()
        add_slovak_questions()
        add_english_questions()

        db.session.commit()
        print("\n🎉 Question template seeding completed!")
        print(f"\nTotal templates: {QuestionTemplate.query.count()}")


if __name__ == '__main__':
    main()
