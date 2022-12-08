import argparse
import sys

from .client import Batches, Groups, Permissions, Projects, Users

users_choices = ['list', 'create', 'retrieve', 'update']
users_help = """list      List all users as jsonl
create    Create new users
retrieve  Retrieve a user selected by a username or integer identifier
update    Update users
"""

groups_choices = ['list', 'create', 'retrieve', 'addusers']
groups_help = """list      List all groups as jsonl
create    Create new groups
retrieve  Retrieve a group selected by name or integer identifier
addusers  Add users to an existing group by passing their ids
"""

projects_choices = ['list', 'create', 'retrieve', 'update']
projects_help = """list      List all projects as jsonl
create    Create new projects
retrieve  Retrieve a project based on integer identifier
update    Update projects
"""

batches_choices = ['list', 'create', 'retrieve', 'update']
batches_help = """list      List all batches as jsonl
create    Create new batches
retrieve  Retrieve a batch based on integer identifier
update    Update batches
"""

perm_choices = ['retrieve', 'add', 'replace']
perm_help = """retrieve  Retrieve permissions for a project or batch
add       Add users or groups to a project's or batch's permissions
replace   Replace a project's or batch's permissions
"""


class Cmd:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Turkle client help')
        self.parser.add_argument('--token', help='API token')
        self.update_title(self.parser, 'Object command')
        subparsers = self.parser.add_subparsers(dest='command')

        users_parser = subparsers.add_parser(
            'users',
            help='List, create, or update users.',
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.update_title(users_parser)
        users_parser.add_argument('subcommand', choices=users_choices, help=users_help)
        users_parser.add_argument('--id', help='User id (integer) - for retrieve')
        users_parser.add_argument('--username', help='Username - for retrieve')
        users_parser.add_argument('--file', help='Jsonl file - required for create and update')

        groups_parser = subparsers.add_parser(
            'groups',
            help='List, create, update groups or add users to a group.',
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.update_title(groups_parser)
        groups_parser.add_argument('subcommand', choices=groups_choices, help=groups_help)
        groups_parser.add_argument('--id', help='User id - required for retrieve')
        groups_parser.add_argument('--name', help='Group name - for retrieve')
        groups_parser.add_argument('--file', help='Jsonl file - required for create or addusers')

        projects_parser = subparsers.add_parser(
            'projects',
            help='List, create, or update projects.',
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.update_title(projects_parser)
        projects_parser.add_argument('subcommand', choices=projects_choices, help=projects_help)
        projects_parser.add_argument('--id', help='Project id - required for retrieve')
        projects_parser.add_argument('--file', help='Jsonl file - required for create or update')

        batches_parser = subparsers.add_parser(
            'batches',
            help='List, create, or update batches.',
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.update_title(batches_parser)
        batches_parser.add_argument('subcommand', choices=batches_choices, help=batches_help)
        batches_parser.add_argument('--id', help='Batch id - required for retrieve')
        batches_parser.add_argument('--file', help='Jsonl file - required for create or update')

        perm_parser = subparsers.add_parser(
            'permissions',
            help='List, add, or replace permissions.',
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.update_title(perm_parser)
        perm_parser.add_argument('subcommand', choices=perm_choices, help=perm_help)
        perm_parser.add_argument('--pid', help='Project id')
        perm_parser.add_argument('--bid', help='Batch id')
        perm_parser.add_argument('--file', help='Jsonl file - required for add or replace')

    @staticmethod
    def update_title(parser, title='Subcommand'):
        parser._positionals.title = title

    def dispatch(self):
        args = self.parser.parse_args()
        client_class = getattr(sys.modules[__name__], args.command.capitalize())
        client = client_class("http://localhost:8000/", args.token)
        print(getattr(client, args.subcommand)(**vars(args)))


def main():
    try:
        Cmd().dispatch()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
