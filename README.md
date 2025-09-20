# calibre-rest

calibre-rest wraps
[calibredb](https://manual.calibre-ebook.com/generated/en/calibredb.html) to
provide a simple REST API server for your [Calibre](https://calibre-ebook.com/)
library.

### Disclaimer

- calibre-rest is alpha code and subject to bugs and breaking changes. Please
use it at your own risk.
- This code has been tested on `amd64` Linux systems with Calibre 8.5.0.
- Contributions for testing and support on other OS platforms and Calibre versions
are greatly welcome.

## Overview

calibre-rest is a self-hosted REST API server that wraps `calibredb` to expose a
Calibre library. I wrote this project as I could not find a good
language-agnostic method to programmatically manipulate a Calibre library
(locally or remotely).

```bash
# get metadata with book id
$ curl localhost:5000/books/1

# query books with title
$ curl --get --data-urlencode "search=title:~^foo.*bar$" \
    http://localhost:5000/books

# add ebook file to library
$ curl -X POST -H "Content-Type:multipart/form-data" \
    --form "file=@foo.epub" http://localhost:5000/books

# download ebook from library
$ curl http://localhost:5000/export/1 -o bar.epub
```

See [API.md](API.md) for
full documentation of all API endpoints and examples.

calibre-rest is not meant to be a direct replacement for [Calibre Content
Server](https://manual.calibre-ebook.com/server.html). It does not have any
frontend interface and has no native access to a remote Calibre library without
an existing `calibre-server` instance. It is best used as a alternative backend
for any scripts or clients that wish to access the library remotely.

## Installation

calibre-rest requires the following dependencies:

- A Calibre library on the local filesystem or served by a [Calibre content
  server](https://manual.calibre-ebook.com/generated/en/calibre-server.html)
- Python >3.7 but Python 3.13 is recommended.
- The `calibre` Python library, at `/usr/lib/calibre`.
- Calibre's system dependencies.

The latter two are satisfied when you install calibre on your local machine.
If not, set the environment variable `CALIBRE_LIBRARY` appropriately.

### Install from PyPI

```console
$ sudo apt install calibre python3-flask python3-gunicorn python3-dateparse python3-jsonschema
$ pip install calibre-rest --break-system-packages
```

### Build from Source

To run calibre-rest on your local machine, Calibre and its dependencies must be installed:

```console
# clone the repository
$ git clone git@github.com:smurfix/calibre-rest.git
$ cd calibre-rest && python3 -m venv .venv

# install Python dependencies
$ source .venv/bin/activate
$ python3 -m pip install .

# install calibre
$ sudo apt install calibre
```

## Usage

Start the server:

```console
$ python3 -mcalibre_rest --help

usage: calibre-rest [options]

Options:
  -h, --help         show this help message and exit
  -d, --dev          Start in dev/debug mode
  -l, --library      Path to calibre library
  -u, --username     Calibre library username
  -p, --password     Calibre library password
  -b, --bind         Bind address HOST:PORT
  -g, --log-level    Log level
  -v, --version      Print version
```

calibre-rest can access any local Calibre libraries or remote [Calibre content
server](https://manual.calibre-ebook.com/generated/en/calibre-server.html)
instances.

For the latter, authentication must be enabled and configured.
For more information, refer to the [calibredb
documentation](https://manual.calibre-ebook.com/generated/en/calibredb.html).

### Configuration

The server can be configured with the following environment variables.

| Env Variable    | Description    | Type    | Default    |
|---------------- | --------------- | --------------- | --------------- |
| `CALIBRE_LIBRARY` | Path to `calibre` library    | string | `/var/lib/calibre` |
| `CALIBRE_REST_LIBRARY` | Path to calibre library   | string   | `./library`   |
| `CALIBRE_REST_USERNAME` | Calibre library username  | string  |  |
| `CALIBRE_REST_PASSWORD` | Calibre library password   | string  |  |
| `CALIBRE_REST_LOG_LEVEL` | Log Level | string  | `INFO`   |
| `CALIBRE_REST_ADDR` | Server bind address | string   | `localhost:5000` |

If running directly on your local machine, we can also use flags:

```console
$ python3 -mcalibre_rest --bind localhost:5000
```

## Development

calibre-rest is built with Python 3.13 and Flask.

To contribute, clone the repository and [build from source](#build-from-source).

```console
# install all dev dependencies
$ make pip.install

# run the dev server
$ make run.dev

# run tests
$ make test
```

## Roadmap

- [x] Support remote libraries
- [x] Pagination
- [ ] Add `pyproject.toml`
- [ ] Submit to PyPI
- [ ] Authentication (via Calibre)
- [ ] Add a way to select the current library that doesn't depend on the URL fragment
- [ ] Feature parity with `calibredb`
- [ ] Merge into Calibre

## Not on the roadmap

This code does not support TLS. If required, use `nginx` or `apache` as a
frontend.
