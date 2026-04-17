import tempfile

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from openpyxl import Workbook

from .models import HistoricSite, ImportRun, SourceFeed
from .views import site_browser


class HistoricSiteApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='strong-password-123')
        self.source_feed = SourceFeed.objects.create(
            name='National Park Service',
            slug='national-park-service',
            jurisdiction_level='national',
            jurisdiction_name='United States',
            source_type='api',
            homepage_url='https://www.nps.gov/',
            refresh_strategy='Manual for now',
        )
        self.site = HistoricSite.objects.create(
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
            source_feed=self.source_feed,
            source_name='National Park Service',
            source_id='nps-liho',
            wikipedia_url='https://en.wikipedia.org/wiki/Lincoln_Home_National_Historic_Site',
            reference_url='https://www.nps.gov/liho/index.htm',
            is_verified=True,
        )

    def test_api_root_exposes_endpoints(self):
        response = self.client.get(reverse('api-root'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('sites', response.json()['endpoints'])

    def test_site_list_returns_records(self):
        response = self.client.get(reverse('site-list'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 1)
        self.assertEqual(payload['page'], 1)
        self.assertEqual(payload['page_size'], 50)
        self.assertEqual(payload['results'][0]['name'], self.site.name)
        self.assertEqual(payload['results'][0]['source_feed']['slug'], self.source_feed.slug)

    def test_site_list_can_filter_by_category(self):
        response = self.client.get(reverse('site-list'), {'category': 'landmark'})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 1)

    def test_site_list_can_filter_by_state(self):
        response = self.client.get(reverse('site-list'), {'state': 'Illinois'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_site_list_can_filter_by_type(self):
        response = self.client.get(reverse('site-list'), {'type': 'Historic Site'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_site_list_supports_pagination(self):
        for index in range(60):
            HistoricSite.objects.create(
                name=f'Site {index}',
                summary='Extra site for pagination testing.',
                latitude=39.7 + (index / 1000),
                longitude=-89.6 - (index / 1000),
                city='Springfield',
                state='Illinois',
                category='landmark',
                designation='National Historic Site',
                source_feed=self.source_feed,
                source_name='National Park Service',
                source_id=f'extra-{index}',
                is_verified=True,
            )

        response = self.client.get(reverse('site-list'), {'page': 2, 'page_size': 25})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 61)
        self.assertEqual(payload['page'], 2)
        self.assertEqual(payload['page_size'], 25)
        self.assertEqual(len(payload['results']), 25)

    def test_site_detail_returns_selected_site(self):
        response = self.client.get(reverse('site-detail', args=[self.site.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.site.id)
        self.assertEqual(response.json()['source_id'], 'nps-liho')

    def test_nearby_requires_coordinates(self):
        response = self.client.get(reverse('site-nearby'))

        self.assertEqual(response.status_code, 400)

    def test_nearby_returns_matching_sites(self):
        response = self.client.get(
            reverse('site-nearby'),
            {'lat': 39.80, 'lng': -89.64, 'radius': 5},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 1)
        self.assertIn('distance_miles', payload['results'][0])

    def test_nearby_can_filter_by_category(self):
        response = self.client.get(
            reverse('site-nearby'),
            {'lat': 39.80, 'lng': -89.64, 'radius': 5, 'category': 'landmark'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_nearby_ignores_sites_without_coordinates(self):
        HistoricSite.objects.create(
            name='Coordinate Pending Site',
            summary='A site imported without public coordinates yet.',
            city='Chicago',
            state='Illinois',
            category='landmark',
            source_feed=self.source_feed,
            source_name='National Park Service',
            source_id='nps-pending',
            is_verified=True,
        )

        response = self.client.get(
            reverse('site-nearby'),
            {'lat': 39.80, 'lng': -89.64, 'radius': 50},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 1)
        self.assertEqual(payload['results'][0]['name'], self.site.name)

    def test_source_feed_list_returns_sources(self):
        response = self.client.get(reverse('source-feed-list'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 1)
        self.assertEqual(payload['page'], 1)
        self.assertEqual(payload['results'][0]['slug'], self.source_feed.slug)

    def test_import_run_list_returns_runs(self):
        ImportRun.objects.create(
            source_feed=self.source_feed,
            status='completed',
            imported_count=1,
            created_count=1,
        )

        response = self.client.get(reverse('import-run-list'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 1)
        self.assertEqual(payload['page'], 1)
        self.assertEqual(payload['results'][0]['source_feed']['slug'], self.source_feed.slug)

    def test_filter_options_returns_states_types_and_categories(self):
        response = self.client.get(reverse('filter-options'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('states', payload)
        self.assertIn('types', payload)
        self.assertIn('categories', payload)
        self.assertEqual(payload['states'][0]['state'], 'Illinois')
        self.assertEqual(payload['types'][0]['designation'], 'National Historic Site')

    def test_site_browser_page_renders(self):
        request = self.factory.get(reverse('site-browser'))
        response = site_browser(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Imported Site Browser', response.content)
        self.assertIn(self.site.name.encode('utf-8'), response.content)

    def test_register_user_creates_account(self):
        response = self.client.post(
            reverse('register-user'),
            {
                'username': 'newuser',
                'password': 'strong-password-456',
                'email': 'new@example.com',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_and_logout_user(self):
        login_response = self.client.post(
            reverse('login-user'),
            {'username': 'tester', 'password': 'strong-password-123'},
            content_type='application/json',
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.json()['user']['username'], 'tester')

        logout_response = self.client.post(reverse('logout-user'), content_type='application/json')
        self.assertEqual(logout_response.status_code, 200)
        self.assertTrue(logout_response.json()['success'])

    def test_visit_site_requires_authentication(self):
        response = self.client.post(reverse('visit-site', args=[self.site.id]), content_type='application/json')

        self.assertEqual(response.status_code, 403)

    def test_user_can_mark_and_unmark_site_as_visited(self):
        self.client.login(username='tester', password='strong-password-123')

        create_response = self.client.post(reverse('visit-site', args=[self.site.id]), content_type='application/json')
        self.assertIn(create_response.status_code, [200, 201])
        self.site.refresh_from_db()

        detail_response = self.client.get(reverse('site-detail', args=[self.site.id]))
        self.assertTrue(detail_response.json()['visited'])

        summary_response = self.client.get(reverse('visit-summary'))
        self.assertEqual(summary_response.status_code, 200)
        self.assertEqual(summary_response.json()['visit_count'], 1)

        delete_response = self.client.delete(reverse('visit-site', args=[self.site.id]), content_type='application/json')
        self.assertEqual(delete_response.status_code, 200)

        detail_after_delete = self.client.get(reverse('site-detail', args=[self.site.id]))
        self.assertFalse(detail_after_delete.json()['visited'])


class HistoricSiteImportTests(TestCase):
    KANSAS_MARKERS_SAMPLE_HTML = """
    <html>
      <body>
        <div class="content-body">
          <h3>Atchison County</h3>
          <p>4(B). HISTORIC FORT LEAVENWORTH</p>
          <p>Long before white men settled Kansas, traffic over the Santa Fe trail was so heavy that troops were detailed to protect it from the Indians.</p>
          <p>US-73, Atchison County</p>
          <p>39.360321,-94.915497</p>
          <h3>Cowley County</h3>
          <p>59. THE GAS THAT WOULDN'T BURN</p>
          <p>Natural gas in this locality was first found in 1903 at Dexter, five miles north.</p>
          <p>US-50, Edwards County</p>
          <p>37.92763, -99.36753</p>
        </div>
      </body>
    </html>
    """

    def test_import_sample_national_sites_creates_source_feed_and_records(self):
        call_command('import_sample_national_sites')

        self.assertEqual(SourceFeed.objects.count(), 1)
        self.assertEqual(HistoricSite.objects.count(), 3)

        imported_site = HistoricSite.objects.get(source_id='nps-liho')
        self.assertEqual(imported_site.source_feed.slug, 'national-register-sample')
        self.assertTrue(imported_site.reference_url)

        import_run = ImportRun.objects.get()
        self.assertEqual(import_run.status, 'completed')
        self.assertEqual(import_run.imported_count, 3)
        self.assertEqual(import_run.created_count, 3)
        self.assertEqual(import_run.failed_count, 0)

    def test_import_sample_national_sites_is_repeatable(self):
        call_command('import_sample_national_sites')
        call_command('import_sample_national_sites')

        self.assertEqual(HistoricSite.objects.count(), 3)
        self.assertEqual(ImportRun.objects.count(), 2)
        latest_run = ImportRun.objects.order_by('-started_at').first()
        self.assertEqual(latest_run.updated_count, 3)

    def test_import_nps_nrhp_listed_creates_sites_from_xlsx(self):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append([
            'Ref#',
            'Property Name',
            'State',
            'County',
            'City',
            'Street & Number',
            'Area of Significance',
            'Category of Property',
            'Listed Date',
        ])
        worksheet.append([
            '14000001',
            'Sample Federal Courthouse',
            'Kansas',
            'Shawnee',
            'Topeka',
            '123 Main St',
            'Politics/Government',
            'Building',
            '2014-01-15',
        ])

        with tempfile.NamedTemporaryFile(suffix='.xlsx') as temp_file:
            workbook.save(temp_file.name)
            call_command('import_nps_nrhp_listed', source_file=temp_file.name)

        source_feed = SourceFeed.objects.get(slug='nps-nrhp-listed')
        imported_site = HistoricSite.objects.get(source_id='14000001')
        import_run = ImportRun.objects.get(source_feed=source_feed)

        self.assertEqual(source_feed.source_type, 'xlsx')
        self.assertEqual(imported_site.name, 'Sample Federal Courthouse')
        self.assertEqual(imported_site.state, 'Kansas')
        self.assertIsNone(imported_site.latitude)
        self.assertIsNone(imported_site.longitude)
        self.assertEqual(imported_site.designation, 'National Register of Historic Places')
        self.assertEqual(import_run.status, 'completed')
        self.assertEqual(import_run.imported_count, 1)
        self.assertEqual(import_run.created_count, 1)

    def test_import_nps_nrhp_listed_is_repeatable(self):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append([
            'Ref#',
            'Property Name',
            'State',
            'County',
            'City',
            'Street & Number',
            'Area of Significance',
            'Category of Property',
            'Listed Date',
        ])
        worksheet.append([
            '14000002',
            'Repeatable Register Site',
            'Kansas',
            'Douglas',
            'Lawrence',
            '456 Elm St',
            'Education',
            'District',
            '2014-05-01',
        ])

        with tempfile.NamedTemporaryFile(suffix='.xlsx') as temp_file:
            workbook.save(temp_file.name)
            call_command('import_nps_nrhp_listed', source_file=temp_file.name)
            call_command('import_nps_nrhp_listed', source_file=temp_file.name)

        self.assertEqual(HistoricSite.objects.filter(source_id='14000002').count(), 1)
        self.assertEqual(ImportRun.objects.filter(source_feed__slug='nps-nrhp-listed').count(), 2)
        latest_run = ImportRun.objects.filter(source_feed__slug='nps-nrhp-listed').order_by('-started_at').first()
        self.assertEqual(latest_run.updated_count, 1)

    def test_import_kansas_historical_markers_creates_marker_records(self):
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', encoding='utf-8') as temp_file:
            temp_file.write(self.KANSAS_MARKERS_SAMPLE_HTML)
            temp_file.flush()
            call_command('import_kansas_historical_markers', source_file=temp_file.name)

        source_feed = SourceFeed.objects.get(slug='kansas-historical-markers')
        self.assertEqual(source_feed.source_type, 'html')
        self.assertEqual(HistoricSite.objects.filter(source_feed=source_feed).count(), 2)

        marker = HistoricSite.objects.get(source_id='ks-marker-atchison-county-4b')
        self.assertEqual(marker.state, 'Kansas')
        self.assertEqual(marker.category, 'marker')
        self.assertEqual(marker.designation, 'Kansas Historical Marker')
        self.assertIsNotNone(marker.latitude)
        self.assertTrue(marker.summary)

        import_run = ImportRun.objects.filter(source_feed=source_feed).latest('started_at')
        self.assertEqual(import_run.status, 'completed')
        self.assertEqual(import_run.imported_count, 2)

    def test_import_kansas_historical_markers_is_repeatable(self):
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', encoding='utf-8') as temp_file:
            temp_file.write(self.KANSAS_MARKERS_SAMPLE_HTML)
            temp_file.flush()
            call_command('import_kansas_historical_markers', source_file=temp_file.name)
            call_command('import_kansas_historical_markers', source_file=temp_file.name)

        source_feed = SourceFeed.objects.get(slug='kansas-historical-markers')
        self.assertEqual(HistoricSite.objects.filter(source_feed=source_feed).count(), 2)
        latest_run = ImportRun.objects.filter(source_feed=source_feed).latest('started_at')
        self.assertEqual(latest_run.updated_count, 2)
