# Turkle Client
This is a client for the [Turkle](https://github.com/hltcoe/turkle) annotation platform.
It provides a commandline interface to create and work with users, groups, projects and batches.

## Install
Install from pip:
```
pip install turkle-client
```

## Usage

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