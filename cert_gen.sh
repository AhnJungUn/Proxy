#!/bin/sh

openssl genrsa -out root.key 2048
openssl req -new -x509 -days 3650 -key root.key -out root.crt
