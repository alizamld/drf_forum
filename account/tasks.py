from django.core.mail import send_mail

from forum._celery import app


@app.task
def send_activation_code(email, activation_code):
    message = f"""
        Hey, crypto enthusiast!
        Thank you for joining our forum. 
        Please, activate your account with this code {activation_code}.
    """
    send_mail(
        'Activate your account',
        message,
        'test@test.com',
        [email, ],
        fail_silently=False
    )


@app.task
def send_activation_code_forgot_pass(email, activation_code):
    message = f"""
        Please, reset your password with this code {activation_code}.
    """
    send_mail(
        'Reset password',
        message,
        'test@test.com',
        [email, ],
        fail_silently=False
    )
