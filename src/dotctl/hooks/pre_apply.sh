#!/bin/env bash

set -e

SCRIPT=$(basename "$0")
CWD=$(dirname "$0")
BASEDIR=$(realpath $CWD)

echo "Running pre apply hook $SCRIPT from $BASEDIR"
