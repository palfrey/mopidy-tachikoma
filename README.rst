Mopidy-Tachikoma
================

.. image:: https://img.shields.io/pypi/v/mopidy-tachikoma.svg
    :target: https://pypi.python.org/pypi/Mopidy-Tachikoma/
.. image:: https://travis-ci.org/palfrey/mopidy-tachikoma.svg?branch=master
    :target: https://travis-ci.org/palfrey/mopidy-tachikoma
.. image:: https://coveralls.io/repos/github/palfrey/mopidy-tachikoma/badge.svg?branch=master
    :target: https://coveralls.io/github/palfrey/mopidy-tachikoma?branch=master

`Mopidy <http://mopidy.com>`_ extension for talking to `Slack <https://slack.com>`_

Installation
------------

1. `pip install Mopidy-Tachikoma`
2. Create new bot at https://my.slack.com/services/new/bot
3. Set "slack_token" in `mopidy.config` to the API Token it provides
4. Restart Mopidy
5. Add the bot to any channels you'd like it to tell you about new songs on
