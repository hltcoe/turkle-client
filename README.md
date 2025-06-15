# Turkle Client
This is a client for the [Turkle](https://github.com/hltcoe/turkle) annotation platform.
It provides a commandline interface to create and work with users, groups, projects and batches.

## Install
Install from pip:
```
pip install turkle-client
```

## Usage
The commandline client works similar to tools like git where there is a hierarchy
of commands. The top level commands are config, users, groups, projects, and batches.
Each has sub-commands like retrieve, create, or update.

To get the top level documentation, pass the -h flag:
```
turkle-client -h
```
To get documentation on an individual command:
```
turkle-client batches -h
```

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

### Projects
A project needs a template html file:
```
{
  "name": "Image Contains",
  "filename": "~/templates/image_contains.html"
}
```
and the json object can have additional optional fields such as
allotted_assignment_time and assignments_per_task.
```
turkle-client projects create --file myproject.json
```

To get information about the batches that have been published for the project:
```
turkle-client projects batches --id 8
```

### Batches
To create a batch, you will need the name, project id, and csv file:
```
{
  "name": "Bird Photos",
  "project": 20,
  "filename": "image_contains.csv",
}
```
The json object can have additional fields just like creating projects.
```
turkle-client batches create --file mybatch.json
```

Getting the progress, the input csv or the results csv all work the same way:
```
turkle-client batches progress --id 17
turkle-client batches input --id 17
turkle-client batches results --id 17
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