# New Implementation of StellarisClient.py

import time
import json
import os
from common_context import CommonContext
from archipelago_client import ArchipelagoClient

class StellarisClient:
    def __init__(self, save_file_path):
        self.save_file_path = save_file_path
        self.tech_progress = {}
        self.archipelago_client = ArchipelagoClient()

    def parse_tech_status(self):
        with open(self.save_file_path, 'r') as save_file:
            data = json.load(save_file)
            # Assuming the tech_status is structured in some specific way
            tech_status = data.get('tech_status', {})
            # Only extract player character's tech progress
            self.tech_progress = tech_status.get('player_character', {})

    def monitor_save_file(self):
        last_progress = self.tech_progress.copy()

        while True:
            time.sleep(5)  # Check every 5 seconds
            self.parse_tech_status()
            new_progress = self.tech_progress.copy()
            if new_progress != last_progress:
                self.check_for_new_technologies(last_progress, new_progress)
                last_progress = new_progress

    def check_for_new_technologies(self, old_progress, new_progress):
        for tech, level in new_progress.items():
            if tech in old_progress and old_progress[tech] < level:
                print(f'Technology completed: {tech} from level {old_progress[tech]} to {level}')
                self.archipelago_client.send_location_check(tech)

# Example usage
if __name__ == '__main__':
    save_file = 'path/to/your/save_file.sav'
    client = StellarisClient(save_file)
    client.monitor_save_file()