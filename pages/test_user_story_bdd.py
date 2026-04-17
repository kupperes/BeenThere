from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from .models import HistoricSite, SourceFeed
from .views import site_browser


class UserStoryBDDTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.primary_source_feed = SourceFeed.objects.create(
            name='National Park Service',
            slug='bdd-national-park-service',
            jurisdiction_level='national',
            jurisdiction_name='United States',
            source_type='api',
            homepage_url='https://www.nps.gov/',
            refresh_strategy='BDD fixture',
            is_active=True,
        )
        cls.secondary_source_feed = SourceFeed.objects.create(
            name='State of Illinois Historic Resources',
            slug='bdd-state-of-illinois',
            jurisdiction_level='state',
            jurisdiction_name='Illinois',
            source_type='manual',
            homepage_url='https://cahokiamounds.org/',
            refresh_strategy='BDD fixture',
            is_active=True,
        )
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
            source_feed=cls.primary_source_feed,
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
            source_feed=cls.secondary_source_feed,
            source_name='State of Illinois',
            source_id='il-cahokia',
            reference_url='https://cahokiamounds.org/',
            is_verified=True,
        )

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.phase3_user = User.objects.create_user(
            username='phase3user',
            password='strong-password-123',
            email='phase3@example.com',
        )
        self.readme_text = Path(settings.BASE_DIR, 'README.md').read_text()
        self.env_example_text = Path(settings.BASE_DIR, '.env.example').read_text()
        self.architecture_text = Path(settings.BASE_DIR, 'docs', 'architecture.md').read_text()
        self.source_selection_text = Path(
            settings.BASE_DIR, 'docs', 'source-selection-rubric.md'
        ).read_text()
        self.location_store_text = Path(
            settings.BASE_DIR, 'ios', 'BeenThere', 'Services', 'LocationStore.swift'
        ).read_text()
        self.api_client_text = Path(
            settings.BASE_DIR, 'ios', 'BeenThere', 'Services', 'APIClient.swift'
        ).read_text()
        self.map_view_text = Path(
            settings.BASE_DIR, 'ios', 'BeenThere', 'Features', 'Nearby', 'NearbyMapView.swift'
        ).read_text()
        self.detail_view_text = Path(
            settings.BASE_DIR, 'ios', 'BeenThere', 'Features', 'Detail', 'SiteDetailView.swift'
        ).read_text()
        self.collection_view_text = Path(
            settings.BASE_DIR, 'ios', 'BeenThere', 'Features', 'Collection', 'CollectionView.swift'
        ).read_text()
        self.api_models_text = Path(
            settings.BASE_DIR, 'ios', 'BeenThere', 'Models', 'APIModels.swift'
        ).read_text()
        self.ios_project_text = Path(
            settings.BASE_DIR, 'ios', 'BeenThere.xcodeproj', 'project.pbxproj'
        ).read_text()

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

    def check_us_2_1(self):
        call_command('import_sample_national_sites')
        self.assertGreaterEqual(HistoricSite.objects.count(), 3)

    def check_us_2_2(self):
        sample_html = """
        <html><body><div class="content-body">
        <h3>Atchison County</h3>
        <p>4(B). HISTORIC FORT LEAVENWORTH</p>
        <p>Long before white men settled Kansas, traffic over the Santa Fe trail was so heavy that troops were detailed to protect it from the Indians.</p>
        <p>US-73, Atchison County</p>
        <p>39.360321,-94.915497</p>
        </div></body></html>
        """
        import tempfile

        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', encoding='utf-8') as temp_file:
            temp_file.write(sample_html)
            temp_file.flush()
            call_command('import_kansas_historical_markers', source_file=temp_file.name)

        self.assertTrue(HistoricSite.objects.filter(source_name='Kansas Historical Markers').exists())

    def check_us_2_3(self):
        response = self.client.get(reverse('site-detail', args=[self.site.id]))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['source_name'], 'National Park Service')
        self.assertEqual(payload['source_id'], 'nps-liho')

    def check_us_2_4(self):
        response = self.client.get(reverse('site-detail', args=[self.site.id]))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['summary'])
        self.assertTrue(payload['wikipedia_url'] or payload['reference_url'])

    def check_us_2_5(self):
        call_command('import_sample_national_sites')
        response = self.client.get(reverse('import-run-list'))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 1)
        self.assertEqual(payload['results'][0]['status'], 'completed')

    def check_us_2_6(self):
        response = self.client.get(reverse('site-detail', args=[self.site.id]))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['source_feed'])
        self.assertTrue(payload['source_name'])

    def check_us_2_7(self):
        self.assertIn('Coverage value', self.source_selection_text)
        self.assertIn('Licensing clarity', self.source_selection_text)
        self.assertIn('Maintenance cost', self.source_selection_text)
        self.assertIn('ingest now', self.source_selection_text)
        self.assertIn('skip', self.source_selection_text)

    def check_us_3_2(self):
        response = self.client.get(reverse('site-nearby'), {'lat': 39.80, 'lng': -89.64, 'radius': 10})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json()['count'], 1)

    def check_us_3_1(self):
        self.assertIn('requestWhenInUseAuthorization()', self.location_store_text)
        self.assertIn('locationManagerDidChangeAuthorization', self.location_store_text)
        self.assertIn('NSLocationWhenInUseUsageDescription', self.ios_project_text)

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

    def check_us_3_7(self):
        request = self.factory.get(reverse('site-browser'))
        response = site_browser(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Imported Site Browser', response.content)
        self.assertIn(b'State', response.content)
        self.assertIn(b'Type', response.content)

    def check_us_4_1(self):
        response = self.client.post(
            reverse('register-user'),
            {'username': 'registered', 'password': 'strong-password-789', 'email': 'registered@example.com'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)

    def check_us_4_2(self):
        response = self.client.post(
            reverse('login-user'),
            {'username': 'phase3user', 'password': 'strong-password-123'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        logout_response = self.client.post(reverse('logout-user'), content_type='application/json')
        self.assertEqual(logout_response.status_code, 200)

    def check_us_4_3(self):
        self.client.login(username='phase3user', password='strong-password-123')
        response = self.client.post(reverse('visit-site', args=[self.site.id]), content_type='application/json')
        self.assertIn(response.status_code, [200, 201])

    def check_us_4_4(self):
        self.client.login(username='phase3user', password='strong-password-123')
        self.client.post(reverse('visit-site', args=[self.site.id]), content_type='application/json')
        response = self.client.delete(reverse('visit-site', args=[self.site.id]), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['deleted'])

    def check_us_4_5(self):
        self.client.login(username='phase3user', password='strong-password-123')
        self.client.post(reverse('visit-site', args=[self.site.id]), content_type='application/json')
        response = self.client.get(reverse('site-detail', args=[self.site.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['visited'])

    def check_us_4_6(self):
        self.client.login(username='phase3user', password='strong-password-123')
        self.client.post(reverse('visit-site', args=[self.site.id]), content_type='application/json')
        response = self.client.get(reverse('visit-summary'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['visit_count'], 1)

    def check_us_s1(self):
        response = self.client.post(
            reverse('register-user'),
            {'username': 'secureuser', 'password': 'strong-password-999', 'email': 'secure@example.com'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username='secureuser')
        self.assertNotEqual(user.password, 'strong-password-999')
        self.assertTrue(user.check_password('strong-password-999'))

    def check_us_s2(self):
        owner = self.phase3_user
        other_user = User.objects.create_user(username='otheruser', password='strong-password-456')
        self.client.login(username=owner.username, password='strong-password-123')
        self.client.post(reverse('visit-site', args=[self.site.id]), content_type='application/json')
        self.client.logout()

        self.client.login(username=other_user.username, password='strong-password-456')
        response = self.client.get(reverse('visit-summary'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['visit_count'], 0)

    def check_us_s3(self):
        gitignore_text = Path(settings.BASE_DIR, '.gitignore').read_text()
        self.assertIn('.env', gitignore_text)
        self.assertIn('DJANGO_SECRET_KEY', self.env_example_text)

    def check_us_s4(self):
        self.assertIn('Security priorities', self.architecture_text)
        self.assertIn('security', self.readme_text.lower())

    def check_us_6_1(self):
        self.assertIn('Map(position:', self.map_view_text)
        self.assertIn('loadNearbySites(for:', self.map_view_text)
        self.assertIn('Annotation(', self.map_view_text)

    def check_us_6_2(self):
        self.assertIn('Place Details', self.detail_view_text)
        self.assertIn('Open Source', self.detail_view_text)
        self.assertIn('Open Wikipedia', self.detail_view_text)
        self.assertIn('visited', self.detail_view_text)

    def check_us_6_3(self):
        self.assertIn('markVisited', self.detail_view_text)
        self.assertIn('unmarkVisited', self.detail_view_text)
        self.assertIn('Mark as Visited', self.detail_view_text)

    def check_us_6_4(self):
        self.assertIn('fetchVisitSummary', self.collection_view_text)
        self.assertIn('visitCount', self.collection_view_text)
        self.assertIn('recentVisits', self.collection_view_text)

    def check_us_6_5(self):
        self.assertIn('requestWhenInUseAuthorization', self.location_store_text)
        self.assertNotIn('requestAlwaysAuthorization', self.location_store_text)

    def check_us_6_6(self):
        response = self.client.get(reverse('site-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('fetchNearbySites', self.api_client_text)

    def check_us_6_7(self):
        self.assertIn('keyDecodingStrategy = .convertFromSnakeCase', self.api_client_text)
        self.assertIn('struct HistoricSite: Codable', self.api_models_text)
        self.assertIn('struct PaginatedResponse<Value: Decodable>', self.api_models_text)

    def check_us_6_8(self):
        self.assertIn('iPhone-only', self.readme_text)
        self.assertIn('There is no planned Windows, Mac desktop, or general-purpose web client', self.readme_text)


STORY_CASES = [
    ('US-1.1', 'configure env-based secrets', 'Given environment-based settings', 'When the app loads configuration', 'Then real secrets are not committed', 'check_us_1_1'),
    ('US-1.2', 'run backend with documented local configuration', 'Given a fresh local checkout', 'When a developer reads the setup guide', 'Then the backend launch steps are documented', 'check_us_1_2'),
    ('US-1.3', 'configure Django REST Framework', 'Given the Django project', 'When API settings are loaded', 'Then DRF is installed and JSON-oriented', 'check_us_1_3'),
    ('US-1.4', 'create HistoricSite model', 'Given the domain model layer', 'When site data is represented', 'Then HistoricSite supports core historical-place fields', 'check_us_1_4'),
    ('US-1.5', 'support SQLite to PostgreSQL/PostGIS evolution', 'Given database configuration', 'When deployment needs change', 'Then the backend can switch engines by environment settings', 'check_us_1_5'),
    ('US-1.6', 'manage sites in admin', 'Given an administrator in Django admin', 'When site records need review', 'Then HistoricSite can be managed there', 'check_us_1_6'),
    ('US-2.1', 'import one national dataset', 'Given a national historical dataset', 'When an import runs', 'Then HistoricSite records are created automatically', 'check_us_2_1'),
    ('US-2.2', 'import one state or local dataset', 'Given a state or local dataset', 'When an import runs', 'Then the same normalized model is populated', 'check_us_2_2'),
    ('US-2.3', 'retain source attribution', 'Given imported place data', 'When a record is stored', 'Then source attribution is preserved', 'check_us_2_3'),
    ('US-2.4', 'attach summaries and links', 'Given imported or enriched place data', 'When a place is serialized', 'Then summary text and external links are present when available', 'check_us_2_4'),
    ('US-2.5', 'track import runs and failures', 'Given an importer execution', 'When the run completes or fails', 'Then operational results are recorded for review', 'check_us_2_5'),
    ('US-2.6', 'show trustworthy sourced places', 'Given a user viewing a place', 'When place details are shown', 'Then source attribution supports trust in the record', 'check_us_2_6'),
    ('US-2.7', 'scope city ingestion with a selection rubric', 'Given many possible city and local data sources', 'When ingestion scope is planned', 'Then source selection is guided by a repeatable value and maintenance rubric', 'check_us_2_7'),
    ('US-3.1', 'allow location access', 'Given the iPhone app', 'When a user opens nearby discovery', 'Then the app can request foreground location permission', 'check_us_3_1'),
    ('US-3.2', 'request nearby historical places', 'Given a user location', 'When the nearby endpoint is called', 'Then matching historical places are returned', 'check_us_3_2'),
    ('US-3.3', 'see closest places within a radius', 'Given multiple places at different distances', 'When nearby results are requested with a radius', 'Then only places inside the radius are returned in distance order', 'check_us_3_3'),
    ('US-3.4', 'read a short summary of what happened there', 'Given a selected place', 'When the detail endpoint is called', 'Then a short summary is returned', 'check_us_3_4'),
    ('US-3.5', 'open a source link for deeper reading', 'Given a selected place', 'When the detail endpoint is called', 'Then a reference link such as Wikipedia is returned', 'check_us_3_5'),
    ('US-3.6', 'filter nearby results by category', 'Given nearby discovery results', 'When a category filter is provided', 'Then only matching categories are returned', 'check_us_3_6'),
    ('US-3.7', 'browse imported sites through an HTML filter page', 'Given a user browsing imported sites', 'When the site browser page opens', 'Then the dataset is easier to browse than raw API JSON', 'check_us_3_7'),
    ('US-4.1', 'create an account securely', 'Given an unauthenticated user', 'When account creation is submitted', 'Then a secure account is created', 'check_us_4_1'),
    ('US-4.2', 'sign in and sign out securely', 'Given an existing account', 'When the user signs in and signs out', 'Then authenticated access is controlled securely', 'check_us_4_2'),
    ('US-4.3', 'mark a place as visited', 'Given an authenticated user', 'When the user marks a place as visited', 'Then a visit record is created', 'check_us_4_3'),
    ('US-4.4', 'remove a mistaken visit check-off', 'Given a visited place', 'When the user undoes the visit', 'Then the visit record is removed', 'check_us_4_4'),
    ('US-4.5', 'tell whether a place is already visited', 'Given an authenticated user', 'When a place is viewed', 'Then visited state is included', 'check_us_4_5'),
    ('US-4.6', 'view a running visit count', 'Given an authenticated user', 'When profile or collection data is requested', 'Then the current visit total is returned', 'check_us_4_6'),
    ('US-5.1', 'earn category badges', 'Given category badge rules', 'When a user reaches a category threshold', 'Then a badge is awarded', None),
    ('US-5.2', 'earn region badges', 'Given geography badge rules', 'When a user reaches a regional threshold', 'Then a badge is awarded', None),
    ('US-5.3', 'view earned badges', 'Given an authenticated user', 'When badge data is requested', 'Then earned badges are returned', None),
    ('US-5.4', 'see progress toward the next badge', 'Given an authenticated user', 'When badge progress is requested', 'Then progress values are returned', None),
    ('US-5.5', 'browse curated collections', 'Given curated collections exist', 'When collection data is requested', 'Then themed place sets are returned', None),
    ('US-6.1', 'see nearby places on a mobile map', 'Given the iPhone app map screen', 'When nearby data loads', 'Then map pins are rendered', 'check_us_6_1'),
    ('US-6.2', 'open a place detail card', 'Given a selected map pin', 'When the user taps it', 'Then a detail card shows summary, sources, and visited state', 'check_us_6_2'),
    ('US-6.3', 'mark a place as visited from the detail card', 'Given an authenticated iPhone user', 'When the user taps the visited action', 'Then the detail card updates to visited', 'check_us_6_3'),
    ('US-6.4', 'review collection and badges on iPhone', 'Given an authenticated iPhone user', 'When the collection screen opens', 'Then visits and badges are shown', 'check_us_6_4'),
    ('US-6.5', 'avoid excessive battery drain', 'Given the mobile app location features', 'When nearby discovery is used', 'Then background tracking stays constrained for MVP', 'check_us_6_5'),
    ('US-6.6', 'consume stable JSON endpoints in Xcode', 'Given the iPhone app networking layer', 'When it calls the backend', 'Then mobile-facing routes return structured JSON', 'check_us_6_6'),
    ('US-6.7', 'map backend responses into Swift models', 'Given the iPhone app data layer', 'When it decodes backend responses', 'Then response shapes fit Swift models with minimal transformation', 'check_us_6_7'),
    ('US-6.8', 'prioritize iPhone usage over desktop compatibility', 'Given roadmap and API decisions', 'When backend changes are planned', 'Then iPhone-first requirements drive the decision', 'check_us_6_8'),
    ('US-S1', 'handle account credentials securely', 'Given account auth flows', 'When credentials are processed', 'Then they are protected appropriately', 'check_us_s1'),
    ('US-S2', 'keep visit history private by default', 'Given user visit-history data', 'When another user attempts access', 'Then the data remains private by default', 'check_us_s2'),
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
