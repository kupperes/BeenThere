from django.db import models


class HistoricSite(models.Model):
    CATEGORY_CHOICES = [
        ('landmark', 'Landmark'),
        ('marker', 'Historical Marker'),
        ('museum', 'Museum'),
        ('battlefield', 'Battlefield'),
        ('memorial', 'Memorial'),
        ('district', 'Historic District'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    summary = models.TextField()
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120, blank=True)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default='other')
    designation = models.CharField(max_length=255, blank=True)
    era = models.CharField(max_length=255, blank=True)
    source_name = models.CharField(max_length=255, blank=True)
    source_id = models.CharField(max_length=255, blank=True)
    wikipedia_url = models.URLField(blank=True)
    reference_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
