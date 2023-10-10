from django.db import models

from apps.user.models import User


class UserResource(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        related_name='%(class)s_created',
        on_delete=models.PROTECT,
    )
    modified_by = models.ForeignKey(
        User,
        related_name='%(class)s_modified',
        on_delete=models.PROTECT,
    )

    # Typing
    id: int
    pk: int

    class Meta:
        abstract = True
        ordering = ['-id']


class GlobalPermission(models.Model):
    class Type(models.IntegerChoices):
        UPLOAD_QBANK = 1, 'Upload Question Bank'
        ACTIVATE_QBANK = 2, 'Activate Question Bank'

    type = models.SmallIntegerField(unique=True, choices=Type.choices)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.Type(self.type).label

    def add_user(self, user):
        if self.users.filter(pk=user.id).exists():
            return
        self.users.add(user)
