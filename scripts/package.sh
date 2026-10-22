#!/bin/sh
# Run inside the already-used Tizen SDK container with the project at /project.
# Private profiles.xml is provisioned locally; it is intentionally not in Git.
set -eu
cd /project
test -f /project/backup/profiles.xml
tizen cli-config profiles.path=/project/backup/profiles.xml
tizen package -t wgt -s QuietHome -o /project/backup -- /project/launcher
