from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.tasks import capture_snapshots_for_active_lectures
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Capture snapshots for all active lectures using the existing task function'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        
        if verbose:
            self.stdout.write(
                self.style.SUCCESS(f'[{timezone.now()}] Starting snapshot capture task...')
            )
        
        try:
            # Call the existing task function directly
            result = capture_snapshots_for_active_lectures()
            
            if verbose:
                self.stdout.write(
                    self.style.SUCCESS(f'[{timezone.now()}] {result["message"]}')
                )
                self.stdout.write(f'Processed {result["processed_lectures"]} active lectures')
                
                # Display detailed results
                for lecture_result in result["results"]:
                    self.stdout.write(f'Lecture {lecture_result["lecture_id"]}:')
                    for detail in lecture_result["results"]:
                        if "Error" in detail:
                            self.stdout.write(self.style.ERROR(f'  ❌ {detail}'))
                        else:
                            self.stdout.write(f'  ✅ {detail}')
            
            # Log the summary for monitoring
            logger.info(result["message"])
            
            return result["message"]
            
        except Exception as e:
            error_msg = f'Snapshot capture failed: {str(e)}'
            logger.error(error_msg)
            if verbose:
                self.stdout.write(self.style.ERROR(f'[{timezone.now()}] {error_msg}'))
            raise e