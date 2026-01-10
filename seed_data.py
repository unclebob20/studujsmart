"""
Run this script to populate the database with initial subjects, topics, and badges.

Usage: python seed_data.py
"""

from app import create_app, db
from app.models.subject import Subject, Topic
from app.models.gamification import Badge


def seed_subjects_and_topics():
    """Create initial subjects and topics"""

    # ==========================================================================
    # MATEMATIKA
    # ==========================================================================
    math = Subject(
        name_sk='Matematika',
        name_en='Mathematics',
        slug='matematika',
        icon='📐',
        color='#3B82F6',
        order_index=1
    )
    db.session.add(math)
    db.session.flush()  # Get ID

    # Math topics
    math_topics = [
        # Algebra
        {
            'name_sk': 'Algebra',
            'name_en': 'Algebra',
            'slug': 'algebra',
            'difficulty': 'medium',
            'order_index': 1,
            'subtopics': [
                {'name_sk': 'Lineárne rovnice', 'slug': 'linearne-rovnice', 'difficulty': 'easy'},
                {'name_sk': 'Kvadratické rovnice', 'slug': 'kvadraticke-rovnice', 'difficulty': 'medium'},
                {'name_sk': 'Sústavy rovníc', 'slug': 'sustavy-rovnic', 'difficulty': 'medium'},
                {'name_sk': 'Exponenciálne funkcie', 'slug': 'exponencialne-funkcie', 'difficulty': 'hard'},
            ]
        },
        # Geometry
        {
            'name_sk': 'Geometria',
            'name_en': 'Geometry',
            'slug': 'geometria',
            'difficulty': 'medium',
            'order_index': 2,
            'subtopics': [
                {'name_sk': 'Pythagorova veta', 'slug': 'pythagorova-veta', 'difficulty': 'easy'},
                {'name_sk': 'Obvod a obsah', 'slug': 'obvod-obsah', 'difficulty': 'easy'},
                {'name_sk': 'Trojuholníky', 'slug': 'trojuholniky', 'difficulty': 'medium'},
                {'name_sk': 'Kružnica a kruh', 'slug': 'kruznica-kruh', 'difficulty': 'medium'},
            ]
        },
        # Functions
        {
            'name_sk': 'Funkcie',
            'name_en': 'Functions',
            'slug': 'funkcie',
            'difficulty': 'hard',
            'order_index': 3,
            'subtopics': [
                {'name_sk': 'Lineárne funkcie', 'slug': 'linearne-funkcie', 'difficulty': 'medium'},
                {'name_sk': 'Kvadratické funkcie', 'slug': 'kvadraticke-funkcie', 'difficulty': 'hard'},
                {'name_sk': 'Derivácie', 'slug': 'derivacie', 'difficulty': 'hard'},
            ]
        }
    ]

    for topic_data in math_topics:
        subtopics = topic_data.pop('subtopics', [])
        parent_topic = Topic(subject_id=math.id, **topic_data)
        db.session.add(parent_topic)
        db.session.flush()

        for i, subtopic_data in enumerate(subtopics):
            subtopic = Topic(
                subject_id=math.id,
                parent_topic_id=parent_topic.id,
                name_en=subtopic_data.get('name_sk'),  # Simple translation
                order_index=i + 1,
                **subtopic_data
            )
            db.session.add(subtopic)

    # ==========================================================================
    # SLOVENSKÝ JAZYK
    # ==========================================================================
    slovak = Subject(
        name_sk='Slovenský jazyk',
        name_en='Slovak Language',
        slug='slovensky-jazyk',
        icon='📚',
        color='#EF4444',
        order_index=2
    )
    db.session.add(slovak)
    db.session.flush()

    slovak_topics = [
        {
            'name_sk': 'Gramatika',
            'name_en': 'Grammar',
            'slug': 'gramatika',
            'difficulty': 'medium',
            'order_index': 1,
            'subtopics': [
                {'name_sk': 'Skloňovanie podstatných mien', 'slug': 'sklenovanie-podstatnych-mien',
                 'difficulty': 'medium'},
                {'name_sk': 'Časovanie slovies', 'slug': 'casovanie-slovies', 'difficulty': 'medium'},
                {'name_sk': 'Prídavné mená', 'slug': 'pridavne-mena', 'difficulty': 'easy'},
                {'name_sk': 'Vetná skladba', 'slug': 'vetna-skladba', 'difficulty': 'hard'},
            ]
        },
        {
            'name_sk': 'Pravopis',
            'name_en': 'Spelling',
            'slug': 'pravopis',
            'difficulty': 'medium',
            'order_index': 2,
            'subtopics': [
                {'name_sk': 'Veľké a malé písmená', 'slug': 'velke-male-pismena', 'difficulty': 'easy'},
                {'name_sk': 'Interpunkcia', 'slug': 'interpunkcia', 'difficulty': 'medium'},
                {'name_sk': 'Zdvojené spoluhlásky', 'slug': 'zdvojene-spoluhasky', 'difficulty': 'medium'},
            ]
        },
        {
            'name_sk': 'Literatúra',
            'name_en': 'Literature',
            'slug': 'literatura',
            'difficulty': 'hard',
            'order_index': 3,
            'subtopics': [
                {'name_sk': 'Literárne druhy a žánre', 'slug': 'literarne-druhy-zanre', 'difficulty': 'medium'},
                {'name_sk': 'Slovenskí autori', 'slug': 'slovenski-autori', 'difficulty': 'medium'},
                {'name_sk': 'Svetová literatúra', 'slug': 'svetova-literatura', 'difficulty': 'hard'},
            ]
        }
    ]

    for topic_data in slovak_topics:
        subtopics = topic_data.pop('subtopics', [])
        parent_topic = Topic(subject_id=slovak.id, **topic_data)
        db.session.add(parent_topic)
        db.session.flush()

        for i, subtopic_data in enumerate(subtopics):
            subtopic = Topic(
                subject_id=slovak.id,
                parent_topic_id=parent_topic.id,
                name_en=subtopic_data.get('name_sk'),
                order_index=i + 1,
                **subtopic_data
            )
            db.session.add(subtopic)

    # ==========================================================================
    # ANGLICKÝ JAZYK
    # ==========================================================================
    english = Subject(
        name_sk='Anglický jazyk',
        name_en='English Language',
        slug='anglicky-jazyk',
        icon='🇬🇧',
        color='#10B981',
        order_index=3
    )
    db.session.add(english)
    db.session.flush()

    english_topics = [
        {
            'name_sk': 'Gramatika',
            'name_en': 'Grammar',
            'slug': 'grammar',
            'difficulty': 'medium',
            'order_index': 1,
            'subtopics': [
                {'name_sk': 'Present Tenses', 'slug': 'present-tenses', 'difficulty': 'easy'},
                {'name_sk': 'Past Tenses', 'slug': 'past-tenses', 'difficulty': 'medium'},
                {'name_sk': 'Future Tenses', 'slug': 'future-tenses', 'difficulty': 'medium'},
                {'name_sk': 'Conditional Sentences', 'slug': 'conditionals', 'difficulty': 'hard'},
            ]
        },
        {
            'name_sk': 'Slovná zásoba',
            'name_en': 'Vocabulary',
            'slug': 'vocabulary',
            'difficulty': 'easy',
            'order_index': 2,
            'subtopics': [
                {'name_sk': 'Daily Routines', 'slug': 'daily-routines', 'difficulty': 'easy'},
                {'name_sk': 'Travel & Tourism', 'slug': 'travel-tourism', 'difficulty': 'medium'},
                {'name_sk': 'Work & Career', 'slug': 'work-career', 'difficulty': 'medium'},
            ]
        },
        {
            'name_sk': 'Čítanie s porozumením',
            'name_en': 'Reading Comprehension',
            'slug': 'reading',
            'difficulty': 'medium',
            'order_index': 3,
            'subtopics': [
                {'name_sk': 'Short Texts', 'slug': 'short-texts', 'difficulty': 'easy'},
                {'name_sk': 'Articles', 'slug': 'articles', 'difficulty': 'medium'},
                {'name_sk': 'Essays', 'slug': 'essays', 'difficulty': 'hard'},
            ]
        }
    ]

    for topic_data in english_topics:
        subtopics = topic_data.pop('subtopics', [])
        parent_topic = Topic(subject_id=english.id, **topic_data)
        db.session.add(parent_topic)
        db.session.flush()

        for i, subtopic_data in enumerate(subtopics):
            subtopic = Topic(
                subject_id=english.id,
                parent_topic_id=parent_topic.id,
                name_en=subtopic_data.get('name_sk'),
                order_index=i + 1,
                **subtopic_data
            )
            db.session.add(subtopic)

    print("✅ Created 3 subjects with topics")


def seed_badges():
    """Create initial badge definitions"""

    badges = [
        {
            'slug': 'first-test',
            'name_sk': 'Prvý test',
            'description_sk': 'Dokončil si svoj prvý test',
            'icon': '🔥',
            'condition_type': 'tests_completed',
            'condition_value': 1,
            'xp_reward': 50
        },
        {
            'slug': 'bookworm',
            'name_sk': 'Knihomoľ',
            'description_sk': 'Dokončil si 10 testov v jednom predmete',
            'icon': '📚',
            'condition_type': 'tests_per_subject',
            'condition_value': 10,
            'xp_reward': 100
        },
        {
            'slug': 'sharpshooter',
            'name_sk': 'Ostrostrelectvo',
            'description_sk': 'Dosiahol si 90% alebo viac v teste',
            'icon': '🎯',
            'condition_type': 'test_accuracy',
            'condition_value': 90,
            'xp_reward': 75
        },
        {
            'slug': 'speed-demon',
            'name_sk': 'Rýchlik',
            'description_sk': 'Dokončil si test za menej ako 5 minút',
            'icon': '⚡',
            'condition_type': 'test_time',
            'condition_value': 300,  # seconds
            'xp_reward': 50
        },
        {
            'slug': 'week-master',
            'name_sk': 'Majster týždňa',
            'description_sk': 'Učil si sa 7 dní v rade',
            'icon': '🏆',
            'condition_type': 'streak_days',
            'condition_value': 7,
            'xp_reward': 200
        },
        {
            'slug': 'perfectionist',
            'name_sk': 'Perfekcionista',
            'description_sk': 'Dosiahol si 100% v teste',
            'icon': '💯',
            'condition_type': 'test_accuracy',
            'condition_value': 100,
            'xp_reward': 150
        },
        {
            'slug': 'dedicated',
            'name_sk': 'Odhodlaný',
            'description_sk': 'Dokončil si 50 testov',
            'icon': '💪',
            'condition_type': 'tests_completed',
            'condition_value': 50,
            'xp_reward': 250
        },
        {
            'slug': 'improver',
            'name_sk': 'Zlepšovač',
            'description_sk': 'Zvýšil si presnosť v téme o 20%',
            'icon': '📈',
            'condition_type': 'accuracy_improvement',
            'condition_value': 20,
            'xp_reward': 100
        }
    ]

    for badge_data in badges:
        badge = Badge(**badge_data)
        db.session.add(badge)

    print("✅ Created 8 badges")


def main():
    """Run all seed functions"""
    app = create_app('development')

    with app.app_context():
        print("Starting database seeding...")

        # Check if already seeded
        if Subject.query.count() > 0:
            print("⚠️  Database already contains subjects. Skipping seed.")
            print("   To re-seed, drop tables and run migrations again.")
            return

        seed_subjects_and_topics()
        seed_badges()

        db.session.commit()
        print("\n🎉 Database seeding completed successfully!")
        print("\nSummary:")
        print(f"   Subjects: {Subject.query.count()}")
        print(f"   Topics: {Topic.query.count()}")
        print(f"   Badges: {Badge.query.count()}")


if __name__ == '__main__':
    main()
