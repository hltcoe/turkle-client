# Turkle Client
This is a client for the [Turkle](https://github.com/hltcoe/turkle) annotation platform.
It provides a commandline interface to create and work with users, groups, projects and batches.

## Install
Install from pip:
```
pip install turkle-client
```

## Usage

### Configuration
Set the url of the Turkle site and your token:
```
turkle-client config url https://example.org/
turkle-client config token 41dcbb22264dd60c5232383fc844dbbab4839146
```
To view your configuration:
```
turkle-client config print
```

The token and url can also be specified on the command line:
```
turkle-client -u https://example.org -t abcdef users list
```

### Users
To list current users:
```
turkle-client users list
```

To create users, create a CSV file like this:
```
username,password,first_name,last_name,email
smithgc1,p@ssw0rd,george,smith,gcs@mail.com
jonesrt1,12345678,roger,jones,jones@mail.com
```
and then pass it to the client::
```
turkle-client users create --file new_users.csv
```
The create command also accepts jsonl files.

### Groups
List groups with:
```
turkle-client groups list
```

Creating a group requires a jsonl or json file with the name and a 
list of user IDs:
```
{"name":"Spanish annotators","users":[3,7,54]}
```
and then passed to the command:
```
turkle-client groups create --file spanish.json
```

Adding users to a group requires a json file with the list of user IDs:
```
[2,4,17,34]
```
which is passed to the command with the group id:
```
turkle-client groups addusers --id 5 --file june_users.json
```

## Developers

### Installing
```
pip install -e .[dev]
```

### Testing
```
pytest
```

### Releasing
1. Update the version in __version__.py
2. Update the changelog
3. Create git tag
4. Upload to PyPI
    * rm -rf dist/ build/ *.egg-info/
    * python -m build
    * twine upload dist/*