import time
from django.core.management.base import BaseCommand
from token_manager.views import refresh_access_token

class Command(BaseCommand):
    help = 'Refresh access token and update it in the database every 1 minute for testing'

    def handle(self, *args, **kwargs):
        """Handle the command execution"""
        self.stdout.write(self.style.SUCCESS('Starting token refresh process...'))

        # Run the token refresh process every 1 minute (for testing purposes)
        while True:
            response = refresh_access_token()
            if 'error' in response:
                self.stdout.write(self.style.ERROR(f"Error: {response['error']}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Access token refreshed successfully: {response['access_token']}"))

            time.sleep(1800)
