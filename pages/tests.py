from django.test import Client, TestCase
from django.urls import reverse

from .models import HistoricSite


class HistoricSiteApiTests(TestCase):
    def setUp(self):
        self.client = Client()
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
            source_name='National Park Service',
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
        self.assertEqual(payload['results'][0]['name'], self.site.name)

    def test_site_detail_returns_selected_site(self):
        response = self.client.get(reverse('site-detail', args=[self.site.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.site.id)

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
