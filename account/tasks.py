from django.core.mail import send_mail

from forum._celery import app


@app.task
def send_activation_code(email, activation_code):
    activation_url = f'http://localhost:8000/api/v1/activate/{activation_code}'
    message = f"""
        Thank you for signing up.
        Please, activate your account.
        Activation link: {activation_url}
    """
    send_mail(
        'Activate your account',
        message,
        'test@test.com',
        [email, ],
        fail_silently=False
    )

