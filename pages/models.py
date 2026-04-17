from django.conf import settings
from django.db import models


class SourceFeed(models.Model):
    JURISDICTION_LEVEL_CHOICES = [
        ('national', 'National'),
        ('state', 'State'),
        ('local', 'Local'),
    ]

    SOURCE_TYPE_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('xlsx', 'XLSX'),
        ('geojson', 'GeoJSON'),
        ('api', 'API'),
        ('html', 'HTML'),
        ('manual', 'Manual'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    jurisdiction_level = models.CharField(max_length=32, choices=JURISDICTION_LEVEL_CHOICES)
    jurisdiction_name = models.CharField(max_length=255, blank=True)
    source_type = models.CharField(max_length=32, choices=SOURCE_TYPE_CHOICES)
    homepage_url = models.URLField(blank=True)
    download_url = models.URLField(blank=True)
    license = models.CharField(max_length=255, blank=True)
    refresh_strategy = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['jurisdiction_level', 'name']

    def __str__(self):
        return self.name


class ImportRun(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    source_feed = models.ForeignKey(SourceFeed, on_delete=models.CASCADE, related_name='import_runs')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='running')
    imported_count = models.PositiveIntegerField(default=0)
    created_count = models.PositiveIntegerField(default=0)
    updated_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    error_log = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.source_feed.name} import on {self.started_at:%Y-%m-%d %H:%M:%S}'


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
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120, blank=True)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default='other')
    designation = models.CharField(max_length=255, blank=True)
    era = models.CharField(max_length=255, blank=True)
    source_feed = models.ForeignKey(
        SourceFeed,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sites',
    )
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


class UserVisit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='site_visits')
    historic_site = models.ForeignKey(HistoricSite, on_delete=models.CASCADE, related_name='user_visits')
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visited_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'historic_site'], name='unique_user_site_visit'),
        ]

    def __str__(self):
        return f'{self.user} visited {self.historic_site}'
