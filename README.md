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