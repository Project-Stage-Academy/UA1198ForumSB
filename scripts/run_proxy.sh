#!/bin/bash

docker build -t forum_proxy ./scripts/proxy

docker run --rm --net=host forum_proxy
