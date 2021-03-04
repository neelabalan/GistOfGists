import requests
from   pytablewriter import MarkdownTableWriter

import sys
import math
import json
from functools import partial

def get_url(key, user=None, page=1, total=None):
    urls = {
        'API': 'https://api.github.com/users/{}'.format(user),
        'GIST_API': 'https://api.github.com/users/{}/gists?per_page=100&page={}'.format(user, page),
        'USER_GIST': 'https://gist.github.com/{}'.format(user),
        'TOTAL_BADGE': '![Total](https://img.shields.io/badge/Total-{}-blue.svg)'.format(total),
        'BUILD_BADGE': '![update README](https://github.com/{}/mygists/actions/workflows/update_readme.yml/badge.svg)'.format(user),
    }
    return urls.get(key)

def fetch_responses(total_gist, user_urls):
    responses    = list()
    if total_gist > 0:
        number_of_pages = math.ceil( total_gist / 100 )
        for counter in range( number_of_pages ):
            responses +=  requests.get( 
                user_urls('GIST_API', total=counter+1)
            ).json()

    return responses
 
if __name__ == "__main__":

    user = sys.argv[1] if len(sys.argv) > 0 else None
    if not user:
        sys.exit('no user provided')

    response = requests.get(get_url(key='API', user=user)) 
    if response.status_code == 200:
        user_urls         = partial(get_url, user=user)
        md                = list() 
        writer            = MarkdownTableWriter()
        total_gist        = response.json().get('public_gists')
        writer.table_name = '''[My Github Gists]({})<br>{}{}'''.format(
            user_urls(key='USER_GIST'), 
            user_urls(key='TOTAL_BADGE', total=total_gist), 
            user_urls(key='BUILD_BADGE')
        )
        writer.headers    = [
            'description', 
            'files',
        ]
        gists = fetch_responses(total_gist, user_urls)

        for gist in gists:
            files       = ['`{}`'.format(file) for file in gist.get('files').keys()]
            filestr     = '<br>'.join(files) if len(files) > 1 else ''.join(files)
            description = gist.get('description')
            gist_url = gist.get('html_url')
            md.append(['[{}]({})'.format(description, gist_url), filestr]) \
                if description \
                else md.append(['[url]({})'.format(gist_url), filestr])

        writer.value_matrix = md
        # uncomment for testing
        # with open('TEST.md', 'w+') as file:
        with open('README.md', 'w+') as file:
            file.write(writer.dumps()) 
    else:
        sys.exit('user does not exist')

