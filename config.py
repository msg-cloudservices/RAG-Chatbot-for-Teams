#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from dotenv import load_dotenv

load_dotenv

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.getenv("MICROSOFT_APP_ID")
    APP_PASSWORD = os.get("MICROSOFT_APP_PASSWORD")
