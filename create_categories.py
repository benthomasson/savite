import os

import django

from core.models import Category

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_app.settings")

django.setup()


def populate_categories():
    categories = [
        "Back-End",
        "Business",
        "Career",
        "Economy",
        "Education",
        "Front-End",
        "Javascript",
        "Linux",
        "Music",
        "Podcast",
        "Productivity",
        "Python",
        "Start-Up",
    ]
    for category in categories:
        c = Category.objects.get_or_create(name=category)[0]
        c.save()

    for category in Category.objects.all():
        print(category)


if __name__ == "__main__":
    populate_categories()