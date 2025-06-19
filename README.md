# Turkle Client
This is a client for the [Turkle](https://github.com/hltcoe/turkle) annotation platform.
It provides a commandline interface to create and work with users, groups, projects and batches.
There is also a client library for building utilities to interact with Turkle.

## Install
Install from pip:
```
pip install turkle-client
```

## CLI Usage
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

Updating a user requires a json object with the id of the user and then
any fields that you want to change:
```
{"id": 5, "email": "my_new_addr@example.org"}
```
and is passed to the command using the file argument:
```
turkle-client users update --file user_update.json
```

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

Adding tasks to a batch can be done by passing the path to a csv file:
```
turkle-client batches add_tasks --id 3 --file new_tasks.csv
```

### Permissions
Projects and batches can be limited to certain users or groups.
These permissions can be retrieved, added to, and replaced.
The dictionary to add or replace permissions looks like this:
```
{"users": [2, 3], "groups": []}
```
All the methods require a project or batch id passed with `--pid` or `--bid`.
The add and replace methods require an additional file argument:
```
turkle-client permissions replace --pid 4 --file new_perms.json
```

## Library
The library is primarily a wrapper around the REST API of Turkle.
To use it, import the `Client` class and pass the url of the site and a token
to initialize it.
```
import turkle_client as tc

client = tc.Client("https://example.org", "abcdefghijkl")
```
Each section of the API (users, groups, projects, batches, and permissions)
has its own object available from the client:
```
users = client.users.list()
```
The client methods expect json dictionaries as input.
To create a new user, pass a dictionary with at least a username and password:
```
new_user = client.users.create({
    "username": "testuser",
    "password": "password"
})
```

### Dynamic Batches
Normally, batches are fixed when they are created, but the API adds support
for adding tasks.
A dictionary with the batch id and a string with the csv fields including headers
are passed to `add_tasks()`:
```
with open(file_path, 'r') as file:
    csv_content = file.read()
    client.batches.add_tasks({
        'id': batch_id,
        'csv_text': csv_content
    })
```

The library provides a `BatchMonitor` that could support an active learning workflow.
It polls the `progress` function of a batch and returns when a goal has been reached:
```
def goal_fn(progress):
    percent = progress["total_finished_tasks"] / progress["total_tasks"]
    return percent > 0.75

def on_goal_reached(progress):
    # add additional tasks here
    print("Batch is 75% complete")

monitor = tc.BatchMonitor(
    client=client,
    batch_id=3,
    goal_fn=goal_fn,
    callback_fn=on_goal_reached,
    interval=10
)

monitor.wait()
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