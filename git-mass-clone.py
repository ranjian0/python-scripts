import os
import json
import requests

BASE_URL = 'https://api.github.com/users/ranjian0/repos'

def get_repos():
    resp = requests.get(BASE_URL)
    return json.loads(resp.text)

def clone_repos():

    for repo in get_repos():
        clone_url = repo['clone_url']
        print("Cloning --> {}".format(clone_url))
        os.system('git clone ' + clone_url)

clone_repos()

