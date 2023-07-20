import typing
from datetime import date

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


class DefaultTokenGenerator(PasswordResetTokenGenerator):
    """
    Strategy object used to generate and check tokens for the internal models
    mechanism.
    """
    reset_timeout_days = settings.TOKEN_DEFAULT_RESET_TIMEOUT_DAYS
    secret = settings.SECRET_KEY

    class Meta:
        abstract = True

    def check_token(self, model, token):
        """
        Check that a model token is correct for a given model
        """
        if not (model and token):
            return False
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(
                self._make_token_with_timestamp(model, ts),
                token
        ):
            return False

        # Check TIMEOUT
        if (self._num_days(self._today()) - ts) > self.reset_timeout_days:
            return False

        return True

    def _make_hash_value(self, model, timestamp):
        raise Exception(
            "No _make_hash_value defined for Class: " + type(self).__name__
        )

    def _num_days(self, dt):
        return (dt - date(2001, 1, 1)).days

    def _today(self):
        return date.today()


def _generate_generator(name: str, _make_hash_value: None | typing.Callable = None, **kwargs):
    def _default_make_hash_func(_, user, timestamp):
        return str(user.pk) + str(timestamp)

    _name = f'{name}TokenGenerator'
    if _make_hash_value is None:
        _make_hash_value = _default_make_hash_func

    return type(
        _name,
        (DefaultTokenGenerator,),
        dict(
            key_salt=_name,
            _make_hash_value=_make_hash_value,
            **kwargs
        ),
    )()


class TokenManager():
    password_reset_token_generator = PasswordResetTokenGenerator()
    unsubscribe_email_token_generator = _generate_generator('UnsubscribeEmailToken', reset_timeout_days=30)
