#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# NOTE: This file has been created by an LLM (from something that was worse).
# It mostly serves as test to ensure we don't accidentally break anything.
# If you encounter something weird in here, do not hesitate to replace this
# test by something more appropriate.

from cmk.agent_based.v2 import Metric, Result, Service, State, StringTable
from cmk.legacy_checks.cisco_prime_wifi_connections import (
    check_cisco_prime_wifi_connections,
    discover_cisco_prime_wifi_connections,
    parse_cisco_prime_wifi_connections,
)

_STRING_TABLE: StringTable = [
    [
        '{ "queryResponse": {  "entity": [   {    "@dtoType": "clientCountsDTO",    "@type": "ClientCounts",    "@url": "https://hello.world.de/webacs/api/v1/data/ClientCounts/61671983180",    "clientCountsDTO": {     "@displayName": "61671983180",     "@id": "61671983180",     "authCount": 7247,     "collectionTime": 1494512992280,     "count": 7319,     "dot11aAuthCount": 1227,     "dot11aCount": 1243,     "dot11acAuthCount": 430,     "dot11acCount": 433,     "dot11bAuthCount": 0,     "dot11bCount": 0,     "dot11gAuthCount": 2400,     "dot11gCount": 2415,     "dot11n2_4AuthCount": 2253,     "dot11n2_4Count": 2271,     "dot11n5AuthCount": 937,     "dot11n5Count": 942,     "key": "All SSIDs"    }   }  ] }}'
    ]
]


def test_discover_cisco_prime_wifi_connections_test() -> None:
    """Test discovery function for cisco_prime_wifi_connections check."""
    parsed = parse_cisco_prime_wifi_connections(_STRING_TABLE)
    result = list(discover_cisco_prime_wifi_connections(parsed))
    assert result == [Service()]


def test_check_cisco_prime_wifi_connections_test() -> None:
    """Test check function for cisco_prime_wifi_connections check."""
    parsed = parse_cisco_prime_wifi_connections(_STRING_TABLE)
    result = list(check_cisco_prime_wifi_connections({}, parsed))
    assert result == [
        Result(state=State.OK, summary="Total connections: 7247"),
        Metric("wifi_connection_total", 7247),
        Result(state=State.OK, summary="802.11a: 1227"),
        Metric("wifi_connection_dot11a", 1227),
        Result(state=State.OK, summary="802.11b: 0"),
        Metric("wifi_connection_dot11b", 0),
        Result(state=State.OK, summary="802.11g: 2400"),
        Metric("wifi_connection_dot11g", 2400),
        Result(state=State.OK, summary="802.11ac: 430"),
        Metric("wifi_connection_dot11ac", 430),
        Result(state=State.OK, summary="802.11n24: 2253"),
        Metric("wifi_connection_dot11n2_4", 2253),
        Result(state=State.OK, summary="802.11n5: 937"),
        Metric("wifi_connection_dot11n5", 937),
    ]
