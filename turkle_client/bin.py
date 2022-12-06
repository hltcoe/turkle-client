import argparse
import sys

from .client import Users

users_help = """list      List all users as jsonl
create    Create a new users
retrieve  Retrieve a user selected by a username or integer identifier
update    Update a user selected by a username or integer identifier
"""


class Cmd:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Turkle client help')
        self.parser.add_argument('--token', help='API token')
        self.parser._positionals.title = 'Object command'
        subparsers = self.parser.add_subparsers(dest='command')

        users_parser = subparsers.add_parser(
            'users',
            help='List, create, or update users.',
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.update_title(users_parser)
        choices = ['list', 'create', 'retrieve', 'update']
        users_parser.add_argument('subcommand', choices=choices, help=users_help)
        users_parser.add_argument('--id', help='User id - required for retrieve')
        users_parser.add_argument('--file', help='Json file - required for create and update')

        groups_parser = subparsers.add_parser('groups', help='List, create, or update groups.')
        self.update_title(groups_parser)
        groups_parser.add_argument('subcommand')

        projects_parser = subparsers.add_parser('projects',
                                                help='List, create, or update projects.')
        self.update_title(projects_parser)
        projects_parser.add_argument('subcommand')

        batches_parser = subparsers.add_parser('batches', help='List, create, or update batches.')
        self.update_title(batches_parser)
        batches_parser.add_argument('subcommand')

    @staticmethod
    def update_title(parser):
        parser._positionals.title = 'Subcommand'

    def dispatch(self):
        args = self.parser.parse_args()

        # some subcommands require id
        if args.subcommand == 'retrieve':
            if not args.id:
                raise ValueError(f"--id must be set for {args.command}")
        elif args.subcommand in ['create', 'update']:
            if not args.file:
                raise ValueError(f"--file must be set for {args.command}")

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
