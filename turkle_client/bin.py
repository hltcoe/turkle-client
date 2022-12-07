import argparse
import sys

from .client import Groups, Users

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
        users_parser.add_argument('--file', help='Json file - required for create and update')

        groups_parser = subparsers.add_parser(
            'groups',
            help='List, create, update groups or add users to a group.',
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.update_title(groups_parser)
        groups_parser.add_argument('subcommand', choices=groups_choices, help=groups_help)
        groups_parser.add_argument('--id', help='User id - required for retrieve')
        groups_parser.add_argument('--name', help='Group name - for retrieve')
        groups_parser.add_argument('--file', help='Json file - required for create or addusers')

        projects_parser = subparsers.add_parser('projects',
                                                help='List, create, or update projects.')
        self.update_title(projects_parser)
        projects_parser.add_argument('subcommand')

        batches_parser = subparsers.add_parser('batches', help='List, create, or update batches.')
        self.update_title(batches_parser)
        batches_parser.add_argument('subcommand')

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
