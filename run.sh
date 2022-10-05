#!/usr/bin/bash

export $(grep -v '^#' .flaskenv | xargs)

waitress-serve --call photoshare:create_app
