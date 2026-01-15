"""
Test generation and management service
"""
from datetime import datetime
from typing import List, Optional
from app import db
from app.models.test import TestSession, UserAnswer
from app.models.question import Question, QuestionTemplate
from app.models.subject import Topic, UserTopicProgress
from app.services.ai_service import AIService


class TestService:
    """Service for test generation and management"""

    def __init__(self):
        self._ai_service = None

    @property
    def ai_service(self):
        """Lazy load AI service"""
        if self._ai_service is None:
            self._ai_service = AIService()
        return self._ai_service

    def create_quick_test(
            self,
            user_id: int,
            subject_id: int,
            num_questions: int = 10
    ) -> TestSession:
        """
        Create a quick test with AI-recommended topics

        Args:
            user_id: User ID
            subject_id: Subject ID
            num_questions: Number of questions

        Returns:
            TestSession object
        """
        # Find weak topics for this user and subject
        weak_topics = UserTopicProgress.query.join(Topic).filter(
            UserTopicProgress.user_id == user_id,
            Topic.subject_id == subject_id,
            UserTopicProgress.accuracy_rate < 70
        ).order_by(UserTopicProgress.accuracy_rate.asc()).limit(3).all()

        if weak_topics:
            topic_ids = [tp.topic_id for tp in weak_topics]
            print(f"DEBUG: Using weak topics: {topic_ids}")
        else:
            # No progress yet, pick topics that have templates
            topics_with_templates = db.session.query(Topic).join(
                QuestionTemplate,
                Topic.id == QuestionTemplate.topic_id
            ).filter(
                Topic.subject_id == subject_id,
                Topic.is_active == True
            ).distinct().limit(5).all()

            # PRINT GOES HERE, AFTER IT'S DEFINED
            print(f"DEBUG: Topics with templates found: {len(topics_with_templates)}")

            if not topics_with_templates:
                raise ValueError(f"No question templates available for subject {subject_id}")

            topic_ids = [t.id for t in topics_with_templates]
            print(f"DEBUG: Selected topic IDs: {topic_ids}")

        # Create test session
        test_session = TestSession(
            user_id=user_id,
            subject_id=subject_id,
            test_type='quick',
            total_questions=num_questions,
            difficulty='medium',
            topic_ids=topic_ids,
            status='in_progress'
        )
        db.session.add(test_session)
        db.session.commit()

        # Generate questions
        self._generate_questions_for_test(test_session, topic_ids, num_questions)

        return test_session

    def _generate_questions_for_test(
            self,
            test_session: TestSession,
            topic_ids: List[int],
            num_questions: int
    ):
        """Generate and attach questions to test session"""
        print(f"DEBUG: Looking for templates with topic_ids: {topic_ids}")

        # Get templates for these topics
        templates = QuestionTemplate.query.filter(
            QuestionTemplate.topic_id.in_(topic_ids)
        ).all()

        print(f"DEBUG: Found {len(templates)} templates")

        if not templates:
            raise ValueError("No question templates found for these topics")

        # Generate questions
        questions_generated = []
        for i in range(num_questions):
            # Pick a random template
            template = templates[i % len(templates)]

            # Generate question using AI
            question_data = self.ai_service.generate_question_from_template(template)

            # Create Question object
            question = Question(
                template_id=template.id,
                topic_id=template.topic_id,
                question_text=question_data['question_text'],
                question_type=template.question_type,
                difficulty=template.difficulty,
                correct_answer=question_data['correct_answer'],
                choices=question_data.get('choices'),
                explanation=question_data.get('explanation'),
                variables_used=question_data.get('variables_used')
            )
            db.session.add(question)
            questions_generated.append(question)

        db.session.commit()

        return questions_generated

    def submit_answer(
            self,
            session_id: int,
            question_id: int,
            user_id: int,
            user_answer: str,
            time_spent: int = 0
    ) -> UserAnswer:
        """
        Submit an answer to a question

        Args:
            session_id: Test session ID
            question_id: Question ID
            user_id: User ID
            user_answer: User's answer
            time_spent: Time spent in seconds

        Returns:
            UserAnswer object
        """
        question = Question.query.get(question_id)
        if not question:
            raise ValueError("Question not found")

        # Check if correct
        is_correct = self._check_answer(question, user_answer)

        # Create user answer
        answer = UserAnswer(
            session_id=session_id,
            question_id=question_id,
            user_id=user_id,
            user_answer=user_answer,
            is_correct=is_correct,
            time_spent_seconds=time_spent
        )
        db.session.add(answer)
        db.session.commit()

        return answer

    def _check_answer(self, question: Question, user_answer: str) -> bool:
        """Check if user's answer is correct"""
        correct = question.correct_answer.strip().lower().replace(' ', '')
        user = user_answer.strip().lower().replace(' ', '')

        if question.question_type == 'single_choice':
            user_letter = user[0] if len(user) > 0 else ''
            correct_letter = correct[0] if len(correct) > 0 else ''
            return user_letter == correct_letter

        # For numeric and fill_blank, exact string match after normalization
        return user == correct

    def _update_topic_progress(self, test: TestSession):
        """Update user's progress for topics in this test"""
        from sqlalchemy.orm import joinedload

        # Get all answers for this test with questions pre-loaded
        answers = UserAnswer.query.options(
            joinedload(UserAnswer.question)
        ).filter_by(session_id=test.id).all()

        # Group by topic
        topic_stats = {}
        for answer in answers:
            # Safely access question
            if answer.question is None:
                continue

            topic_id = answer.question.topic_id
            if topic_id not in topic_stats:
                topic_stats[topic_id] = {'total': 0, 'correct': 0}

            topic_stats[topic_id]['total'] += 1
            if answer.is_correct:
                topic_stats[topic_id]['correct'] += 1

        # Update progress for each topic
        for topic_id, stats in topic_stats.items():
            progress = UserTopicProgress.query.filter_by(
                user_id=test.user_id,
                topic_id=topic_id
            ).first()

            if not progress:
                progress = UserTopicProgress(
                    user_id=test.user_id,
                    topic_id=topic_id
                )
                db.session.add(progress)

            # Update stats
            for _ in range(stats['correct']):
                progress.update_progress(True)
            for _ in range(stats['total'] - stats['correct']):
                progress.update_progress(False)


    def complete_test(self, session_id: int) -> TestSession:
        """
        Mark test as complete and calculate results

        Args:
            session_id: Test session ID

        Returns:
            Updated TestSession
        """
        test = TestSession.query.get(session_id)
        if not test:
            raise ValueError("Test session not found")

        test.status = 'completed'
        test.completed_at = datetime.utcnow()

        # Get answers for verification
        answers = UserAnswer.query.filter_by(session_id=session_id).all()

        test.calculate_results()

        # Update user progress for topics
        self._update_topic_progress(test)

        db.session.commit()
        return test