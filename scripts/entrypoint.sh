#!/bin/sh

set -e

run_wait() {
    python /app/scripts/wait.py
}

run_entrypoint() {
    if [ ! -f /deploy/touched ]; then
        python /app/scripts/entrypoint.py
        touch /deploy/touched
    fi
}

cat << LICENSE_ACK

# ================================================================================= #
# Gluu License Agreement: https://www.gluu.org/support-license/                     #
# The use of Gluu Server Enterprise Edition is subject to the Gluu Support License. #
# ================================================================================= #

LICENSE_ACK

if [ -f /etc/redhat-release ]; then
    source scl_source enable python27 && run_wait
    source scl_source enable python27 && run_entrypoint
    source scl_source enable rh-nodejs8 && node /opt/gluu/node/passport/server/app.js
else
    run_wait
    run_entrypoint
    node /opt/gluu/node/passport/server/app.js
fi
