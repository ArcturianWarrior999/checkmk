===========================================
Livestatus client - cmk.livestatus_client
===========================================

Introduction and goals
======================

Livestatus is providing data held by the the in-memory database of our
monitoring core for external programs.

The distributed architecture of Checkmk is powered by the livestatus protocol
making it one of the most important parts of Checkmk.

The most used client library implementation is our python implementation
`cmk.livestatus_client`. Many of our internal components use this library to
communicate with the monitoring core.

Implementation
--------------

The implementation is located in the Checkmk git at
`packages/cmk-livestatus-client`.

The client is built as standalone package and must not rely on other Python
code of Checkmk.

See also
--------
- :doc:`arch-comp-core`
- :doc:`arch-comp-livestatus`
- `User manual: Livestatus <https://docs.checkmk.com/master/en/livestatus.html>`_
