from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
from datetime import datetime
import subprocess
import os

class Command(BaseCommand):
    help = 'Backup database to S3'

    def handle(self, *args, **options):
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backup_{timestamp}.sql'

        # Dump database
        dump_cmd = f'pg_dump -h {settings.DATABASES["default"]["HOST"]} ' \
                  f'-U {settings.DATABASES["default"]["USER"]} ' \
                  f'-d {settings.DATABASES["default"]["NAME"]} > {backup_file}'
        
        subprocess.run(dump_cmd, shell=True, env={
            'PGPASSWORD': settings.DATABASES['default']['PASSWORD']
        })

        # Upload to S3
        s3 = boto3.client('s3')
        s3.upload_file(
            backup_file,
            settings.AWS_STORAGE_BUCKET_NAME,
            f'backups/db/{backup_file}'
        )

        # Clean up local file
        os.remove(backup_file)
        self.stdout.write(self.style.SUCCESS(f'Successfully backed up database to {backup_file}')) 