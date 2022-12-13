import requests
from pytablewriter import MarkdownTableWriter

import sys
import math
import json
from functools import partial
from typing import List, Dict, Any, Optional, Callable


def get_url(
    key: str, user: str = None, page: int = 1, total: int = None
) -> Optional[str]:
    """
    - get all related URL to writer markdown
        - API           get user info
        - GIST_API      gist info of user
        - USER_GIST     gist URL of user
        - TOTAL_BADGE   badge for total gist the user has
        - BUILD_BADGE   badge display to github action build status
    """
    urls = {
        "API": "https://api.github.com/users/{}".format(user),
        "GIST_API": "https://api.github.com/users/{}/gists?per_page=100&page={}".format(
            user, page
        ),
        "USER_GIST": "https://gist.github.com/{}".format(user),
        "TOTAL_BADGE": "![Total](https://img.shields.io/badge/Total-{}-blue.svg)".format(
            total
        ),
        "BUILD_BADGE": "![update README](https://github.com/{}/mygists/actions/workflows/update_readme.yml/badge.svg)".format(
            user
        ),
    }
    return urls.get(key)


def fetch_responses(
    total_gist: int, user_urls: Callable[..., Any]
) -> List[Dict[Any, Any]]:
    """get all gist API responses in json format"""
    responses = list()
    if total_gist > 0:
        number_of_pages = math.ceil(total_gist / 100)
        for counter in range(number_of_pages):
            responses += requests.get(user_urls("GIST_API", total=counter + 1)).json()

    return responses


def write_markdown(writer: MarkdownTableWriter, md_file: str = "README.md") -> None:
    """write README.md with markdown writer dumps"""
    with open(md_file, "w+") as file:
        file.write(writer.dumps())


def get_url_response(user: str) -> requests.models.Response:
    """get URL response for the Github user"""
    try:
        response = requests.get(get_url(key="API", user=user))
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        sys.exit(err)

    return response


def get_total_gists(response: requests.models.Response) -> int:
    """get total number of github user's gists"""
    return response.json().get("public_gists")


def prepare_table(
    user: str, total: int, user_urls: Callable[..., Any]
) -> MarkdownTableWriter:
    """
    prepare the header of table with
        - user Gist link
        - total badge
        - build status
    """

    writer = MarkdownTableWriter()
    writer.table_name = """[My Github Gists]({})<br>{}{}""".format(
        user_urls(key="USER_GIST"),
        user_urls(key="TOTAL_BADGE", total=total),
        user_urls(key="BUILD_BADGE"),
    )
    writer.headers = [
        "description",
        "files",
    ]
    return writer


def construct_table(
    gists: List[Dict[Any, Any]], writer: MarkdownTableWriter
) -> MarkdownTableWriter:
    """construct the markdown table"""

    md = list()
    for gist in gists:
        # get all files related to the gist
        files = ["`{}`".format(file) for file in gist.get("files").keys()]

        # have HTML <br> for each file
        filestr = "<br>".join(files) if len(files) > 1 else "".join(files)

        # get the description for the gist
        description = gist.get("description")

        # the URL to gist
        gist_url = gist.get("html_url")

        # put them all together
        md.append(
            ["[{}]({})".format(description, gist_url), filestr]
        ) if description else md.append(["[url]({})".format(gist_url), filestr])

    writer.value_matrix = md
    return writer


def run(args: List[str]):
    user = args[1] if len(args) > 0 else None
    if not user:
        sys.exit("no user provided")
    else:
        # get user gist response
        resp = get_url_response(user)

        # get URLs for the user
        user_urls = partial(get_url, user=user)

        total_gist = get_total_gists(resp)

        # prepare the header of the table
        writer = prepare_table(user, total_gist, user_urls)

        # fetch all responses for table construction
        gists = fetch_responses(total_gist, user_urls)
        write_markdown(construct_table(gists, writer))

        # uncomment below line and comment above line for local testing
        # write_markdown(construct_table(gists, writer), md_file='TEST.md')


if __name__ == "__main__":
    args = sys.argv
    run(args=args)
