'''
description:
    creates a gist of github gists in markdown table format
running:
    pip3 install -r requirements.txt
    python3 gistofgists.py -u neelabalan
'''

import requests
import json
import argparse

try:
    from pytablewriter import MarkdownTableWriter
except ImportError as error:
    print("module not found - {}".format(error))

def validUser(response):
    ''' check if the user exists in github '''
    if response.status_code != 200 and response.json().get('message') == 'Not Found':
        return False 
    else:
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u',
        '--user',
        help = 'provide unique github user as arguement'
    )
    args = parser.parse_args()
    if args.user:
        user     = args.user
        url      = 'https://api.github.com/users/{}/gists'.format(user)
        response = requests.get(url)
        if validUser(response):
            md                = list() 
            userGistUrl       = 'gist.github.com/{}'.format(user)
            writer            = MarkdownTableWriter()
            gists             = response.json()
            writer.table_name = '[Gist of Gists]({})'.format(userGistUrl)
            writer.headers    = [
                'description', 
                'files',
            ]

            for gist in gists:
                files       = ['`{}`'.format(file) for file in gist.get('files').keys()]
                filestr     = '<br>'.join(files) if len(files) > 1 else ''.join(files)
                description = gist.get('description')
                gistUrl     = gist.get('url')
                md.append(['[{}]({})'.format(description, gistUrl), filestr])

            writer.value_matrix = md
            with open('README.md', 'w+') as file:
                file.write(writer.dumps()) 

        else:
            print('user does not exist')
    else:
        print('no user provided')
