# scrachess
Simple Chess.com scrapper bot

requirements installation:
-------------

```
$ pip install -r requirements.txt
```

usage:
-------------

```
$ python main.py --help
```

# Docker installation

build image:
-------------

```
$ docker build -t scrachess-img --rm .
```

run simple container:
-------------

```
$ docker run --rm -it --name scrachess scrachess-img <args>
```

run container with volume to export results to json
-------------

```
$ docker run --rm -it --name scrachess --volume <abspath>:/logs scrachess-img <args>
```

