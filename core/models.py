import os
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


def default_date():
    return timezone.now() + timezone.timedelta(days=30)


class Site(models.Model):
    url = models.URLField(verbose_name="Site URL", blank=False)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="categories"
    )
    image_path = models.CharField(max_length=300)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(default=default_date, blank=True)
    expired = models.BooleanField(default=False)

    @property
    def is_deadline_expired(self):
        return self.deadline < timezone.localtime(timezone.now())

    @property
    def image_path_modified(self):
        if os.path.isfile(
            os.path.join(
                settings.MEDIA_ROOT, os.path.join(self.user.username, self.image_path)
            )
        ):
            return os.path.join(self.user.username, self.image_path)
        return "default_image.jpg"

    class Meta:
        ordering = ("-modified_at",)
        unique_together = ("user", "url")

    def save(self, *args, **kwargs):
        if self.deadline < timezone.localtime(timezone.now()):
            raise ValidationError("Not a valid deadline.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.url


@receiver(post_delete, sender=Site)
def remove_file(sender, instance, *args, **kwargs):
    file_path = os.path.join(
        settings.MEDIA_ROOT, os.path.join(instance.user.username, instance.image_path)
    )
    if os.path.exists(file_path):
        os.remove(file_path)
