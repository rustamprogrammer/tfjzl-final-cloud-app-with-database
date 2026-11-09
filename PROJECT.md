# Course assessment extension

The online course application now supports questions with multiple correct choices, enrollment-linked submissions, weighted scores, and a detailed exam results page. A question earns its points only when the selected choices exactly match its correct answers. A result is visible only to the learner who submitted it.

The Django admin includes inline questions and choices and all seven required models. Authenticated learners enroll, open **Start Exam**, select answers, and submit. Scores above 80% pass; unsuccessful attempts include a **Re-test** link.

## Run locally

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-course.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

On Windows, activate `.venv\Scripts\Activate.ps1` instead.

## Skills Network

When the lab image does not provide `ensurepip`, keep dependencies in the project:

```sh
python3 -m pip install --target .course-deps -r requirements-course.txt
PYTHONPATH=.course-deps python3 manage.py migrate
PYTHONPATH=.course-deps python3 manage.py createsuperuser
PYTHONPATH=.course-deps python3 manage.py runserver 0.0.0.0:8000
```

Open `/admin/` to add an instructor, course, lessons, questions, and choices. Open `/onlinecourse/` to enroll and take the exam.

## Validation

```sh
python manage.py test onlinecourse
```

Six integration tests cover successful multi-select submission, partial and incorrect choices, result ownership, invalid and foreign-course answer rejection, authentication/enrollment requirements, and the exam template.
