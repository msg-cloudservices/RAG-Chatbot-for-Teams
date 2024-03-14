#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from dotenv import load_dotenv

load_dotenv()

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.getenv("MICORSOFT_APP_IDD")
    APP_PASSWORD = os.getenv("MICORSOFT_APP_PASSWORDD")
    print(f"APP_ID: {APP_ID}; APP_PASSWORD: {APP_PASSWORD}")
