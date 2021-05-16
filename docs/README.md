# Building the documentation

## Generating the .rst files
Before you can generate the html files, you need to generate the `.rst` files.
Run `sphinx-apidoc -o . ../src/hips` in the `docs` directory.

## Generating the html files
Simply run `make html` in the shell, the html files are then located in `_build/html`