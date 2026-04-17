import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from pages.models import HistoricSite, ImportRun, SourceFeed


class Command(BaseCommand):
    help = 'Import sample national historical sites into HistoricSite.'

    def handle(self, *args, **options):
        dataset_path = (
            Path(__file__).resolve().parents[2] / 'data' / 'sample_national_register.json'
        )

        source_feed, _ = SourceFeed.objects.get_or_create(
            slug='national-register-sample',
            defaults={
                'name': 'National Register Sample Dataset',
                'jurisdiction_level': 'national',
                'jurisdiction_name': 'United States',
                'source_type': 'json',
                'homepage_url': 'https://www.nps.gov/subjects/nationalregister/index.htm',
                'download_url': '',
                'license': 'Sample development data',
                'refresh_strategy': 'Manual import command',
                'is_active': True,
            },
        )

        import_run = ImportRun.objects.create(
            source_feed=source_feed,
            status='running',
            notes=f'Importing sample national dataset from {dataset_path.name}',
        )

        try:
            with dataset_path.open() as dataset_file:
                records = json.load(dataset_file)

            created_count = 0
            updated_count = 0

            with transaction.atomic():
                for record in records:
                    site, created = HistoricSite.objects.update_or_create(
                        source_feed=source_feed,
                        source_id=record['source_id'],
                        defaults={
                            'name': record['name'],
                            'summary': record['summary'],
                            'description': record.get('description', ''),
                            'latitude': record['latitude'],
                            'longitude': record['longitude'],
                            'address': record.get('address', ''),
                            'city': record.get('city', ''),
                            'state': record.get('state', ''),
                            'category': record.get('category', 'other'),
                            'designation': record.get('designation', ''),
                            'era': record.get('era', ''),
                            'source_name': source_feed.name,
                            'wikipedia_url': record.get('wikipedia_url', ''),
                            'reference_url': record.get('reference_url', ''),
                            'image_url': record.get('image_url', ''),
                            'is_verified': record.get('is_verified', True),
                        },
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

            import_run.imported_count = len(records)
            import_run.created_count = created_count
            import_run.updated_count = updated_count
            import_run.status = 'completed'
            import_run.finished_at = timezone.now()
            import_run.save(update_fields=[
                'imported_count',
                'created_count',
                'updated_count',
                'status',
                'finished_at',
            ])

            self.stdout.write(
                self.style.SUCCESS(
                    f'Imported {len(records)} sample national sites '
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
