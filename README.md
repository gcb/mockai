# mock openai rest endpoints

Develop locally or run functional tests.

## usage

```
host$ make build
host$ make
docker$ cd code
docker$ python -m pip install -r requirements.txt && python mockai.py
```

It will listen on `127.0.0.1:8080` by default.

### Parameters/config

Override parameters in `Makefile.local` (must create file). The defaults are documented at the start of `Makefile`.

### convenience/dot files

If you want dot files for the user in the container, add them to a directory `./user-home/`, e.g. `./user-home/.bash_profile`.

Everything in this optional dir will be copied to the user home in the container, during container build step.

# LICENSE

AGPL3 or newer

# Similar projects

- https://github.com/polly3d/mockai - more mature version in javascript
