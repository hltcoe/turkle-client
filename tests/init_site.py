# preload a clean site with objects for testing
# 2 users already exist before this runs (anonymous and the first admin)
# this is to make it easier to use vcr for repeatable tests.
# saves us from having to do a lot of mocking
import argparse
import os
import sys

import turkle_client as tc

def load_file(path):
    with open(path, 'r') as fh:
        return fh.read()

def add_users(base_url, token):
    users = [
        {'username': 'user1', 'password': 'password', 'first_name': 'Bob'},
        {'username': 'user2', 'password': 'password', 'first_name': 'Sue'},
        {'username': 'user3', 'password': 'password', 'first_name': 'Ed'},
        {'username': 'user4', 'password': 'password', 'first_name': 'Megan'},
    ]
    client = tc.Users(base_url, token)
    for user in users:
        client.create(user)

def add_groups(base_url, token):
    groups = [
        {'name': 'Group1', 'users': [3, 4]},
        {'name': 'Group2', 'users': [5, 6]},
        {'name': 'Group3', 'users': [3, 4, 5, 6]},
        {'name': 'Group4', 'users': [3]}
    ]
    client = tc.Groups(base_url, token)
    for group in groups:
        client.create(group)

def add_projects(base_url, token, turkle_path):
    client = tc.Projects(base_url, token)
    filename = os.path.join(turkle_path, 'examples/translate_minimal.html')
    client.create({
        'name': 'Translate',
        'html_template': load_file(filename),
        'filename': os.path.basename(filename)
    })
    filename = os.path.join(turkle_path, 'examples/image_contains.html')
    client.create({
        'name': 'Image Contains',
        'html_template': load_file(filename),
        'filename': os.path.basename(filename)
    })

def add_batches(base_url, token, turkle_path):
    client = tc.Batches(base_url, token)
    filename = os.path.join(turkle_path, 'examples/translate_two_cities.csv')
    client.create({
        'name': 'Dickens',
        'project': 1,
        'csv_text': load_file(filename),
        'filename': os.path.basename(filename)
    })
    filename = os.path.join(turkle_path, 'examples/image_contains.csv')
    client.create({
        'name': 'Birds',
        'project': 2,
        'csv_text': load_file(filename),
        'filename': os.path.basename(filename)
    })

def add_permissions(base_url, token):
    client = tc.Permissions(base_url, token)
    client.add("project", 1, {
        'users': [],
        'groups': [2, 3]
    })
    client.add("project", 2, {
        'users': [5],
        'groups': [1]
    })


def main():
    parser = argparse.ArgumentParser(description="Turkle helper script.")
    parser.add_argument("turkle_path", help="Path to the Turkle directory")
    parser.add_argument("token", help="Authentication token for the Turkle API")
    parser.add_argument("--host", default="http://localhost:8000",
                        help="Base URL of the Turkle server (default: http://localhost:8000)"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.turkle_path):
        print(f"Error: '{args.turkle_path}' is not a valid directory.")
        sys.exit(1)

    add_users(args.host, args.token)
    add_groups(args.host, args.token)
    add_projects(args.host, args.token, args.turkle_path)
    add_batches(args.host, args.token, args.turkle_path)
    add_permissions(args.host, args.token)


if __name__ == "__main__":
    main()
