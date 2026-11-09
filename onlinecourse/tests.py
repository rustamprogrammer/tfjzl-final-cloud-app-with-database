from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Course, Question, Choice, Enrollment, Submission


class ExamFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('learner', password='test-only-password')
        cls.other = User.objects.create_user('other')
        cls.course = Course.objects.create(name='Learning Django', description='Demo')
        cls.enrollment = Enrollment.objects.create(user=cls.user, course=cls.course)
        cls.question = Question.objects.create(course=cls.course, question_text='Select both', grade=100)
        cls.a = Choice.objects.create(question=cls.question, choice_text='A', is_correct=True)
        cls.b = Choice.objects.create(question=cls.question, choice_text='B', is_correct=True)
        cls.wrong = Choice.objects.create(question=cls.question, choice_text='Wrong')

    def setUp(self):
        self.client.force_login(self.user)
        self.submit_url = reverse('onlinecourse:submit', args=[self.course.pk])

    def test_all_correct_choices_pass_and_render_results(self):
        response = self.client.post(self.submit_url, {'choice_1': [self.a.pk, self.b.pk]}, follow=True)
        self.assertContains(response, 'Congratulations')
        self.assertEqual(response.context['grade'], 100)
        self.assertEqual(Submission.objects.get().choices.count(), 2)

    def test_partial_or_extra_wrong_choice_does_not_pass(self):
        for answers in ([self.a.pk], [self.a.pk, self.b.pk, self.wrong.pk], []):
            response = self.client.post(self.submit_url, {'choice_1': answers}, follow=True)
            self.assertEqual(response.context['grade'], 0)
            self.assertContains(response, 'Re-test')

    def test_other_users_cannot_read_submission(self):
        submission = Submission.objects.create(enrollment=self.enrollment)
        self.client.force_login(self.other)
        response = self.client.get(reverse('onlinecourse:show_exam_result', args=[self.course.pk, submission.pk]))
        self.assertEqual(response.status_code, 404)

    def test_cross_course_and_malformed_answers_rejected_without_submission(self):
        other_course = Course.objects.create(name='Other', description='Other')
        question = Question.objects.create(course=other_course, question_text='Other')
        foreign = Choice.objects.create(question=question, choice_text='Foreign', is_correct=True)
        for value in (str(foreign.pk), 'not-a-number'):
            self.assertEqual(self.client.post(self.submit_url, {'choice_1': value}).status_code, 400)
        self.assertEqual(Submission.objects.count(), 0)

    def test_authentication_enrollment_and_post_are_required(self):
        self.assertEqual(self.client.get(self.submit_url).status_code, 405)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(self.submit_url).status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.post(self.submit_url).status_code, 302)
        self.assertEqual(Submission.objects.count(), 0)

    def test_course_details_show_exam_for_enrolled_user(self):
        response = self.client.get(reverse('onlinecourse:course_details', args=[self.course.pk]))
        self.assertContains(response, 'Start Exam')
        self.assertContains(response, 'Select both')
        self.client.logout()
        response = self.client.get(reverse('onlinecourse:course_details', args=[self.course.pk]))
        self.assertNotContains(response, 'Start Exam')
