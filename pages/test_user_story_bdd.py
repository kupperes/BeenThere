from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.test import Client, TestCase
from django.urls import reverse

from .models import HistoricSite


class UserStoryBDDTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = HistoricSite.objects.create(
            name='Lincoln Home National Historic Site',
            summary='Abraham Lincoln lived here before becoming president.',
            description='A preserved Springfield home tied to Lincoln and his family.',
            latitude=39.797800,
            longitude=-89.644600,
            city='Springfield',
            state='Illinois',
            category='landmark',
            designation='National Historic Site',
            era='19th century',
            source_name='National Park Service',
            source_id='nps-liho',
            wikipedia_url='https://en.wikipedia.org/wiki/Lincoln_Home_National_Historic_Site',
            reference_url='https://www.nps.gov/liho/index.htm',
            is_verified=True,
        )
        cls.far_site = HistoricSite.objects.create(
            name='Cahokia Mounds State Historic Site',
            summary='A major pre-Columbian Native American city site.',
            description='An archaeological site near Collinsville, Illinois.',
            latitude=38.655400,
            longitude=-90.061800,
            city='Collinsville',
            state='Illinois',
            category='landmark',
            designation='State Historic Site',
            era='Pre-Columbian',
            source_name='State of Illinois',
            source_id='il-cahokia',
            reference_url='https://cahokiamounds.org/',
            is_verified=True,
        )

    def setUp(self):
        self.client = Client()
        self.readme_text = Path(settings.BASE_DIR, 'README.md').read_text()
        self.env_example_text = Path(settings.BASE_DIR, '.env.example').read_text()
        self.architecture_text = Path(settings.BASE_DIR, 'docs', 'architecture.md').read_text()

    def assert_pending(self, story_id, title):
        self.fail(f'{story_id} pending: {title}')

    def check_us_1_1(self):
        self.assertIn('DJANGO_SECRET_KEY', self.env_example_text)
        self.assertTrue(settings.SECRET_KEY)

    def check_us_1_2(self):
        self.assertIn('python3 manage.py runserver', self.readme_text)
        self.assertIn('pip install -r requirements.txt', self.readme_text)

    def check_us_1_3(self):
        self.assertIn('rest_framework', settings.INSTALLED_APPS)
        self.assertEqual(
            settings.REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'],
            ['rest_framework.renderers.JSONRenderer'],
        )

    def check_us_1_4(self):
        field_names = {field.name for field in HistoricSite._meta.fields}
        self.assertTrue({'name', 'summary', 'latitude', 'longitude', 'category'}.issubset(field_names))

    def check_us_1_5(self):
        self.assertIn('DJANGO_DB_BACKEND=sqlite', self.env_example_text)
        self.assertIn('postgis', Path(settings.BASE_DIR, 'BeenThere', 'settings.py').read_text())

    def check_us_1_6(self):
        self.assertIn(HistoricSite, admin.site._registry)

    def check_us_3_2(self):
        response = self.client.get(reverse('site-nearby'), {'lat': 39.80, 'lng': -89.64, 'radius': 10})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json()['count'], 1)

    def check_us_3_3(self):
        response = self.client.get(reverse('site-nearby'), {'lat': 39.80, 'lng': -89.64, 'radius': 20})
        self.assertEqual(response.status_code, 200)
        payload = response.json()['results']
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['name'], self.site.name)

    def check_us_3_4(self):
        response = self.client.get(reverse('site-detail', args=[self.site.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['summary'], self.site.summary)

    def check_us_3_5(self):
        response = self.client.get(reverse('site-detail', args=[self.site.id]))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['wikipedia_url'] or payload['reference_url'])

    def check_us_3_6(self):
        response = self.client.get(
            reverse('site-nearby'),
            {'lat': 39.80, 'lng': -89.64, 'radius': 200, 'category': 'landmark'},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 2)
        self.assertTrue(all(item['category'] == 'landmark' for item in payload['results']))

    def check_us_s3(self):
        gitignore_text = Path(settings.BASE_DIR, '.gitignore').read_text()
        self.assertIn('.env', gitignore_text)
        self.assertIn('DJANGO_SECRET_KEY', self.env_example_text)

    def check_us_s4(self):
        self.assertIn('Security priorities', self.architecture_text)
        self.assertIn('security', self.readme_text.lower())


STORY_CASES = [
    ('US-1.1', 'configure env-based secrets', 'Given environment-based settings', 'When the app loads configuration', 'Then real secrets are not committed', 'check_us_1_1'),
    ('US-1.2', 'run backend with documented local configuration', 'Given a fresh local checkout', 'When a developer reads the setup guide', 'Then the backend launch steps are documented', 'check_us_1_2'),
    ('US-1.3', 'configure Django REST Framework', 'Given the Django project', 'When API settings are loaded', 'Then DRF is installed and JSON-oriented', 'check_us_1_3'),
    ('US-1.4', 'create HistoricSite model', 'Given the domain model layer', 'When site data is represented', 'Then HistoricSite supports core historical-place fields', 'check_us_1_4'),
    ('US-1.5', 'support SQLite to PostgreSQL/PostGIS evolution', 'Given database configuration', 'When deployment needs change', 'Then the backend can switch engines by environment settings', 'check_us_1_5'),
    ('US-1.6', 'manage sites in admin', 'Given an administrator in Django admin', 'When site records need review', 'Then HistoricSite can be managed there', 'check_us_1_6'),
    ('US-2.1', 'import one national dataset', 'Given a national historical dataset', 'When an import runs', 'Then HistoricSite records are created automatically', None),
    ('US-2.2', 'import one state or local dataset', 'Given a state or local dataset', 'When an import runs', 'Then the same normalized model is populated', None),
    ('US-2.3', 'retain source attribution', 'Given imported place data', 'When a record is stored', 'Then source attribution is preserved', None),
    ('US-2.4', 'attach summaries and links', 'Given imported or enriched place data', 'When a place is serialized', 'Then summary text and external links are present when available', None),
    ('US-2.5', 'track import runs and failures', 'Given an importer execution', 'When the run completes or fails', 'Then operational results are recorded for review', None),
    ('US-2.6', 'show trustworthy sourced places', 'Given a user viewing a place', 'When place details are shown', 'Then source attribution supports trust in the record', None),
    ('US-3.1', 'allow location access', 'Given the iPhone app', 'When a user opens nearby discovery', 'Then the app can request foreground location permission', None),
    ('US-3.2', 'request nearby historical places', 'Given a user location', 'When the nearby endpoint is called', 'Then matching historical places are returned', 'check_us_3_2'),
    ('US-3.3', 'see closest places within a radius', 'Given multiple places at different distances', 'When nearby results are requested with a radius', 'Then only places inside the radius are returned in distance order', 'check_us_3_3'),
    ('US-3.4', 'read a short summary of what happened there', 'Given a selected place', 'When the detail endpoint is called', 'Then a short summary is returned', 'check_us_3_4'),
    ('US-3.5', 'open a source link for deeper reading', 'Given a selected place', 'When the detail endpoint is called', 'Then a reference link such as Wikipedia is returned', 'check_us_3_5'),
    ('US-3.6', 'filter nearby results by category', 'Given nearby discovery results', 'When a category filter is provided', 'Then only matching categories are returned', 'check_us_3_6'),
    ('US-4.1', 'create an account securely', 'Given an unauthenticated user', 'When account creation is submitted', 'Then a secure account is created', None),
    ('US-4.2', 'sign in and sign out securely', 'Given an existing account', 'When the user signs in and signs out', 'Then authenticated access is controlled securely', None),
    ('US-4.3', 'mark a place as visited', 'Given an authenticated user', 'When the user marks a place as visited', 'Then a visit record is created', None),
    ('US-4.4', 'remove a mistaken visit check-off', 'Given a visited place', 'When the user undoes the visit', 'Then the visit record is removed', None),
    ('US-4.5', 'tell whether a place is already visited', 'Given an authenticated user', 'When a place is viewed', 'Then visited state is included', None),
    ('US-4.6', 'view a running visit count', 'Given an authenticated user', 'When profile or collection data is requested', 'Then the current visit total is returned', None),
    ('US-5.1', 'earn category badges', 'Given category badge rules', 'When a user reaches a category threshold', 'Then a badge is awarded', None),
    ('US-5.2', 'earn region badges', 'Given geography badge rules', 'When a user reaches a regional threshold', 'Then a badge is awarded', None),
    ('US-5.3', 'view earned badges', 'Given an authenticated user', 'When badge data is requested', 'Then earned badges are returned', None),
    ('US-5.4', 'see progress toward the next badge', 'Given an authenticated user', 'When badge progress is requested', 'Then progress values are returned', None),
    ('US-5.5', 'browse curated collections', 'Given curated collections exist', 'When collection data is requested', 'Then themed place sets are returned', None),
    ('US-6.1', 'see nearby places on a mobile map', 'Given the iPhone app map screen', 'When nearby data loads', 'Then map pins are rendered', None),
    ('US-6.2', 'open a place detail card', 'Given a selected map pin', 'When the user taps it', 'Then a detail card shows summary, sources, and visited state', None),
    ('US-6.3', 'mark a place as visited from the detail card', 'Given an authenticated iPhone user', 'When the user taps the visited action', 'Then the detail card updates to visited', None),
    ('US-6.4', 'review collection and badges on iPhone', 'Given an authenticated iPhone user', 'When the collection screen opens', 'Then visits and badges are shown', None),
    ('US-6.5', 'avoid excessive battery drain', 'Given the mobile app location features', 'When nearby discovery is used', 'Then background tracking stays constrained for MVP', None),
    ('US-6.6', 'consume stable JSON endpoints in Xcode', 'Given the iPhone app networking layer', 'When it calls the backend', 'Then mobile-facing routes return structured JSON', None),
    ('US-6.7', 'map backend responses into Swift models', 'Given the iPhone app data layer', 'When it decodes backend responses', 'Then response shapes fit Swift models with minimal transformation', None),
    ('US-6.8', 'prioritize iPhone usage over desktop compatibility', 'Given roadmap and API decisions', 'When backend changes are planned', 'Then iPhone-first requirements drive the decision', None),
    ('US-S1', 'handle account credentials securely', 'Given account auth flows', 'When credentials are processed', 'Then they are protected appropriately', None),
    ('US-S2', 'keep visit history private by default', 'Given user visit-history data', 'When another user attempts access', 'Then the data remains private by default', None),
    ('US-S3', 'operate without exposing secrets in source control', 'Given operational setup', 'When developers configure the app', 'Then secrets stay outside committed source', 'check_us_s3'),
    ('US-S4', 'review security posture during planning', 'Given architecture and planning docs', 'When maintainers review future work', 'Then security expectations are documented', 'check_us_s4'),
]


def _make_story_test(story_id, title, given, when, then, check_name):
    def test_method(self):
        """
        Scenario:
            Given {given}
            When {when}
            Then {then}
        """.strip()
        if check_name is None:
            self.assert_pending(story_id, title)
        getattr(self, check_name)()

    test_method.__name__ = f"test_{story_id.lower().replace('-', '_').replace('.', '_')}"
    test_method.__doc__ = f"Scenario {story_id}: Given {given}, When {when}, Then {then}."
    return test_method


for case in STORY_CASES:
    setattr(UserStoryBDDTests, _make_story_test(*case).__name__, _make_story_test(*case))
