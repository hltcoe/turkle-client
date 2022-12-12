import argparse
import json
import os.path
import sys

import appdirs

from .client import Batches, Groups, Permissions, Projects, Users
from .wrappers import BatchesWrapper, GroupsWrapper, PermissionsWrapper, ProjectsWrapper, \
    UsersWrapper

config_choices = ['token', 'url']
config_help = """token  Set the API token
url    Set the base URL for the Turkle site. Ex: http://localhost:8000/ 
"""

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
addusers  Add users to an existing group by passing their ids as list in file
"""

projects_choices = ['list', 'create', 'retrieve', 'update', 'batches']
projects_help = """list      List all projects as jsonl
create    Create new projects
retrieve  Retrieve a project based on integer identifier
update    Update projects
batches   List batches for a project
"""

batches_choices = ['list', 'create', 'retrieve', 'update', 'input', 'results', 'progress']
batches_help = """list      List all batches as jsonl
create    Create new batches
retrieve  Retrieve a batch based on integer identifier
update    Update batches
input     Download the input CSV
results   Download the current results CSV
progress  Get current progress information
"""

perm_choices = ['retrieve', 'add', 'replace']
perm_help = """retrieve  Retrieve permissions for a project or batch
add       Add users or groups to a project's or batch's permissions
replace   Replace a project's or batch's permissions
"""


class Cmd:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Turkle client help')
        self.parser.add_argument('-t', '--token', help='API token')
        self.parser.add_argument('-u', '--url', help='Base URL for the Turkle site')
        self.update_title(self.parser, 'Object command')
        subparsers = self.parser.add_subparsers(dest='command')

        config_parser = subparsers.add_parser(
            'config',
            help='Set the token or url in the config.',
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.update_title(config_parser, 'Parameter')
        config_parser.add_argument('subcommand', choices=config_choices, help=config_help)
        config_parser.add_argument('value', help='The value to set for the parameter')

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
        projects_parser.add_argument('--id', help='Project id - required for retrieve and batches')
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

        if args.command == 'config':
            self.set_config(args.subcommand, args.value)
            print(f"{args.subcommand} set to {args.value}")
            return

        # load config but default to command line arguments
        config = self.load_config()
        args.token = args.token if args.token else config.get('token', None)
        args.url = args.url if args.url else config.get('url', None)
        if not args.token:
            raise ValueError("token not specified")
        if not args.url:
            raise ValueError("url not specified")

        # construct the class and method from the command and subcommand
        client = self.construct_client(args.command.capitalize(), args.url, args.token)
        print(getattr(client, args.subcommand)(**vars(args)), end='')

    def construct_client(self, name, url, token):
        client_class = getattr(sys.modules[__name__], name)
        client = client_class(url, token)
        wrapper_class = getattr(sys.modules[__name__], name + 'Wrapper')
        return wrapper_class(client)

    @property
    def config_dir(self):
        return appdirs.user_config_dir('turkle-client', 'HLTCOE')

    @property
    def config_file(self):
        return os.path.join(self.config_dir, 'config.json')

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as fh:
                config = json.load(fh)
                return config
        else:
            return {}

    def set_config(self, parameter, value):
        config = self.load_config()
        config[parameter] = value
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, 'w') as fh:
            json.dump(config, fh)


def main():
    #try:
        Cmd().dispatch()
    #except Exception as e:
    #    print(f"Error: {e}")


if __name__ == '__main__':
    main()
