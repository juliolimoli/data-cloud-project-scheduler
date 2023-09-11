import pytest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path to the scripts folder
scripts_folder_path = os.path.join(current_dir, '..', 'scripts')
print(scripts_folder_path)
# Add the scripts folder path to sys.path temporarily
sys.path.append(scripts_folder_path)

# Now you can import modules from the scripts folder
import src.app as app

# Don't forget to remove the added path
sys.path.remove(scripts_folder_path)

payload = {
    "latitude": "-23.556519",
    "longitude": "-46.686597",
    "points": "1",
    "radius": "200",
    "days": "1"
    }

@pytest.fixture
def test_coordinates(payload):
    assert [("-23.556519", "-46.686597")] == app.set_coordinates(payload)
