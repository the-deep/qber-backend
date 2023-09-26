from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models

from .managers import CustomUserManager


class EmailNotificationType(models.IntegerChoices):
    ACCOUNT_ACTIVATION = 1, 'Account Activation'
    PASSWORD_RESET = 2, 'Password Reset'
    PASSWORD_CHANGED = 3, 'Password Changed'
    NEWS_AND_OFFERS = 4, 'News And Offers'

    @classmethod
    def get_opt_emails(cls):
        always_send = [
            cls.ACCOUNT_ACTIVATION,
            cls.PASSWORD_RESET,
        ]
        return {
            enum.name: (enum.value, enum.label)
            for enum in cls
            if enum.value not in always_send
        }


class User(AbstractUser):
    class OptEmailNotificationType(models.IntegerChoices):
        NEWS_AND_OFFERS = EmailNotificationType.NEWS_AND_OFFERS

    OPT_EMAIL_NOTIFICATION_TYPES = [value for value, _ in OptEmailNotificationType.choices]

    EMAIL_FIELD = USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    username = None
    email = models.EmailField(unique=True)
    invalid_email = models.BooleanField(default=False)

    email_opt_outs = ArrayField(
        models.IntegerField(
            choices=OptEmailNotificationType.choices,
        ),
        default=list,
        blank=True,
    )

    objects = CustomUserManager()

    pk: int

    def save(self, *args, **kwargs):
        # Make sure email/username are same and lowercase
        self.email = self.email.lower()
        return super().save(*args, **kwargs)

    def unsubscribe_email(self, email_type, save=False):
        self.email_opt_outs = list(set([
            *self.email_opt_outs,
            email_type,
        ]))
        if save:
            self.save(update_fields=('email_opt_outs',))

    def is_email_subscribed_for(self, email_type):
        if (
            email_type in self.email_opt_outs and
            email_type in self.OPT_EMAIL_NOTIFICATION_TYPES
        ):
            return False
        return True
