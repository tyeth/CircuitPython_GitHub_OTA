import hashlib
import requests
import supervisor

REPO = "tyeth/ProfBoots_Mini-Fork"
BRANCH = None  # string or None
BASE_PATH = "MiniFork_wifi_CircuitPython/"  # empty string for root e.g. ""
FILES_TO_CHECK = ['html_home_page.py', 'code.py']  # code.py last as it possibly reboots

# Function to compute SHA1 hash of a file
def compute_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

# Function to compare and update file if needed
def update_file(file_name):
    local_sha1 = compute_sha1(file_name)
    #TODO: switch to looking at the whole folder in one go, avoids downloading base64 content unnecessarily
    url = f'https://api.github.com/repos/{REPO}/contents/{BASE_PATH}{file_name}{("" if BRANCH is None else "?ref=" + BRANCH)}'
    response = requests.get(url)
    response_data = response.json()
    github_sha1 = response_data['sha']

    if local_sha1 != github_sha1:
        print(f'{file_name} mismatched')
        if file_name == 'code.py':
            content = requests.get(response_data['download_url']).content
            new_file_path = f'code_{github_sha1}.py'
            with open(new_file_path, 'wb') as f:
                f.write(content)
            
            if compute_sha1(new_file_path) == github_sha1:
                supervisor.set_next_code_file(new_file_path)
                supervisor.reload()
        else:
            print(f'{file_name} hash mismatch but no action taken')

def check_files(files_to_check = FILES_TO_CHECK):
  # Check each file
  for file in files_to_check:
      update_file(file)
