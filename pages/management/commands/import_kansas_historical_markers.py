import re
from pathlib import Path
from urllib.request import urlopen

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from pages.models import HistoricSite, ImportRun, SourceFeed


DEFAULT_KANSAS_MARKERS_URL = 'https://www.kansashistory.gov/p/kansas-historical-markers/14999'
MARKER_PATTERN = re.compile(r'^(?P<number>\d+(?:\([A-Z]\))?)\.\s+(?P<title>.+)$')
COORD_PATTERN = re.compile(r'^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$')


def clean_text(value):
    return ' '.join((value or '').split())


def build_source_id(marker_number, county_name):
    normalized_county = clean_text(county_name).lower().replace(' ', '-')
    normalized_number = marker_number.lower().replace('(', '').replace(')', '')
    return f'ks-marker-{normalized_county}-{normalized_number}'


class Command(BaseCommand):
    help = 'Import Kansas Historical Markers from the Kansas Historical Society markers page.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-url',
            default=DEFAULT_KANSAS_MARKERS_URL,
            help='Override the remote HTML source URL.',
        )
        parser.add_argument(
            '--source-file',
            help='Read the Kansas markers HTML from a local file instead of downloading it.',
        )

    def handle(self, *args, **options):
        source_feed, _ = SourceFeed.objects.get_or_create(
            slug='kansas-historical-markers',
            defaults={
                'name': 'Kansas Historical Markers',
                'jurisdiction_level': 'state',
                'jurisdiction_name': 'Kansas',
                'source_type': 'html',
                'homepage_url': DEFAULT_KANSAS_MARKERS_URL,
                'download_url': options['source_url'],
                'license': 'Official Kansas Historical Society source; verify reuse terms for production display.',
                'refresh_strategy': 'Manual import command from Kansas Historical Society marker listings page',
                'is_active': True,
            },
        )

        import_run = ImportRun.objects.create(
            source_feed=source_feed,
            status='running',
            notes='Importing Kansas Historical Markers listings.',
        )

        try:
            html = self._load_source(options['source_file'], options['source_url'])
            markers = self._parse_markers(html)

            created_count = 0
            updated_count = 0

            with transaction.atomic():
                for marker in markers:
                    _, created = HistoricSite.objects.update_or_create(
                        source_feed=source_feed,
                        source_id=marker['source_id'],
                        defaults={
                            'name': marker['name'],
                            'summary': marker['summary'],
                            'description': marker['description'],
                            'latitude': marker['latitude'],
                            'longitude': marker['longitude'],
                            'address': marker['address'],
                            'city': '',
                            'state': 'Kansas',
                            'category': 'marker',
                            'designation': 'Kansas Historical Marker',
                            'era': '',
                            'source_name': source_feed.name,
                            'wikipedia_url': '',
                            'reference_url': DEFAULT_KANSAS_MARKERS_URL,
                            'image_url': '',
                            'is_verified': True,
                        },
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

            import_run.imported_count = len(markers)
            import_run.created_count = created_count
            import_run.updated_count = updated_count
            import_run.status = 'completed'
            import_run.finished_at = timezone.now()
            import_run.notes = (
                f'Imported from Kansas Historical Society source: '
                f'{options["source_file"] or options["source_url"]}'
            )
            import_run.save(update_fields=[
                'imported_count',
                'created_count',
                'updated_count',
                'status',
                'finished_at',
                'notes',
            ])

            self.stdout.write(
                self.style.SUCCESS(
                    f'Imported {len(markers)} Kansas historical markers '
                    f'({created_count} created, {updated_count} updated).'
                )
            )
        except Exception as exc:
            import_run.status = 'failed'
            import_run.failed_count = 1
            import_run.error_log = str(exc)
            import_run.finished_at = timezone.now()
            import_run.save(update_fields=['status', 'failed_count', 'error_log', 'finished_at'])
            raise

    def _load_source(self, source_file, source_url):
        if source_file:
            return Path(source_file).read_text(encoding='utf-8')

        with urlopen(source_url) as response:
            return response.read().decode('utf-8', errors='ignore')

    def _parse_markers(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='content-body') or soup

        county_name = ''
        current_marker = None
        markers = []

        for element in container.find_all(['h2', 'h3', 'h4', 'p', 'li']):
            text = clean_text(element.get_text(' ', strip=True))
            if not text:
                continue

            if element.name in {'h2', 'h3', 'h4'} and text.endswith('County'):
                if current_marker:
                    markers.append(self._finalize_marker(current_marker))
                county_name = text
                current_marker = None
                continue

            marker_match = MARKER_PATTERN.match(text)
            if marker_match and county_name:
                if current_marker:
                    markers.append(self._finalize_marker(current_marker))
                current_marker = {
                    'marker_number': marker_match.group('number'),
                    'name': clean_text(marker_match.group('title')).title(),
                    'county_name': county_name,
                    'description_lines': [],
                    'address_lines': [],
                    'latitude': None,
                    'longitude': None,
                }
                continue

            if not current_marker:
                continue

            coords_match = COORD_PATTERN.match(text)
            if coords_match:
                current_marker['latitude'] = float(coords_match.group(1))
                current_marker['longitude'] = float(coords_match.group(2))
                continue

            if text.startswith('Note:'):
                current_marker['description_lines'].append(text)
                continue

            if any(token in text for token in ['US-', 'I-', 'K-', 'Road', 'mile', 'Milepost', 'junction', 'rest area', 'service area', 'bridge']):
                current_marker['address_lines'].append(text)
                continue

            if text != 'No historic markers currently are located in this county.':
                current_marker['description_lines'].append(text)

        if current_marker:
            markers.append(self._finalize_marker(current_marker))

        return markers

    def _finalize_marker(self, marker):
        description = '\n\n'.join(marker['description_lines']).strip()
        address = '\n'.join(marker['address_lines']).strip()
        summary = marker['description_lines'][0] if marker['description_lines'] else (
            f"Kansas Historical Marker in {marker['county_name']}."
        )

        return {
            'source_id': build_source_id(marker['marker_number'], marker['county_name']),
            'name': marker['name'],
            'summary': summary[:500],
            'description': description,
            'address': address,
            'latitude': marker['latitude'],
            'longitude': marker['longitude'],
        }
