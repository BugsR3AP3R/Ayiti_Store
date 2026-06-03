from django.db import models
from django.contrib.auth.models import User


HAITI_DEPARTMENTS = [
    ('artibonite', 'Artibonite'),
    ('centre', 'Centre'),
    ('grand_anse', "Grand'Anse"),
    ('nippes', 'Nippes'),
    ('nord', 'Nord'),
    ('nord_est', 'Nord-Est'),
    ('nord_ouest', 'Nord-Ouest'),
    ('ouest', 'Ouest'),
    ('sud', 'Sud'),
    ('sud_est', 'Sud-Est'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=50, choices=HAITI_DEPARTMENTS, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profil - {self.user.username}"
