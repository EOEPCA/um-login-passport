# -*- coding: utf-8-unix -*-

# Checks waits for the following to happen before moving on to the
# passed command:
#
# - Consul is up and populated
# - oxAuth UMA endpoint is up
# - oxTrust Passport endpoint is up
#
# author: torstein@escenic.com

import logging as log
import os
import sys
import time

import requests

from gluu_config import ConfigManager

GLUU_OXAUTH_BACKEND = os.environ.get("GLUU_OXAUTH_BACKEND", "localhost:8081")
GLUU_OXTRUST_BACKEND = os.environ.get("GLUU_OXTRUST_BACKEND", "localhost:8082")

MAX_WAIT_SECONDS = 300
SLEEP_DURATION = 5
LAST_CONFIG_KEY = "oxauth_openid_jwks_fn"

# When debugging wait-for-it, set level=log.INFO or pass
# --log=DEBUG on the command line.
log.basicConfig(
    level=log.INFO,
    format='%(asctime)s [%(levelname)s] [%(filename)s] - %(message)s'
)


def wait_for_config(config_manager):
    for i in range(0, MAX_WAIT_SECONDS, SLEEP_DURATION):
        try:
            if config_manager.get(LAST_CONFIG_KEY):
                log.info("Config backend is ready.")
                return
        except Exception as exc:
            log.warn(exc)
            log.warn(
                "Config backend is not ready, retrying in {} seconds.".format(
                    SLEEP_DURATION))
        time.sleep(SLEEP_DURATION)

    log.error("Config backend is not ready after {} seconds.".format(MAX_WAIT_SECONDS))
    sys.exit(1)


def wait_for_oxauth():
    url = "http://{}/oxauth/restv1/uma2-configuration".format(GLUU_OXAUTH_BACKEND)
    log.warn("Waiting for oxAuth to be up URL={}".format(url))

    for i in range(0, MAX_WAIT_SECONDS, SLEEP_DURATION):
        try:
            r = requests.head(url)
            if r.status_code == 200:
                log.info("oxAuth is up :-)")
                return
            else:
                log.warn("oxAuth URL={} is not up yet, retrying in {} seconds".format(
                    url, SLEEP_DURATION,
                ))
        except Exception as exc:
            log.warn("oxAuth URL={} is not up yet, error={}, retrying in {} seconds".format(
                url, exc, SLEEP_DURATION,
            ))
        time.sleep(SLEEP_DURATION)

    log.error("oxAuth not ready, after {} seconds.".format(MAX_WAIT_SECONDS))
    sys.exit(1)


def wait_for_oxtrust():
    url = "http://{}/identity/restv1/passport/config".format(GLUU_OXTRUST_BACKEND)
    log.warn("Waiting for oxTrust to be up URL={}".format(url))

    for i in range(0, MAX_WAIT_SECONDS, SLEEP_DURATION):
        try:
            r = requests.head(url)
            if r.status_code in (200, 401):
                log.info("oxTrust is up :-)")
                return
            elif r.status_code == 503:
                log.warn("oxTrust is up but oxPassport config is disabled, "
                         "please enable it first, retrying in {} seconds".format(SLEEP_DURATION))
            else:
                log.warn("oxTrust URL={} is not up yet, retrying in {} seconds".format(url, SLEEP_DURATION))
        except Exception as exc:
            log.warn("oxTrust URL={} is not up yet, error={}, retrying in {} seconds".format(url, exc, SLEEP_DURATION))
        time.sleep(SLEEP_DURATION)

    log.error("oxTrust not ready, after {} seconds.".format(MAX_WAIT_SECONDS))
    sys.exit(1)


def execute_passed_command(command_list):
    log.info(
        "Now executing the arguments passed to " +
        sys.argv[0] +
        ": " +
        " ".join(command_list)
    )
    os.system(" ".join(command_list))


if __name__ == "__main__":
    log.info(
        "Hi world, waiting for config backend, oxAuth, and oxTrust to be ready before " +
        "running " + " ".join(sys.argv[1:])
    )
    config_manager = ConfigManager()
    wait_for_config(config_manager)
    # wait_for_oxauth()
    # wait_for_oxtrust()
    execute_passed_command(sys.argv[1:])
