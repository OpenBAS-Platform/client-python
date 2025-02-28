OpenBAS client for Python
=========================

The PyOBAS library is designed to help OpenBAS users and developers to interact
with the OpenBAS platform API using Python. It requires Python 3.11 or above.

Quickstart
==========

Installation
------------
`PyOBAS is available via PyPI <https://pypi.org/project/pyobas/>`_, so it may be installed with any good package manager.

Install with ``pip``:

.. code:: shell

    poetry add pyobas

Or with ``poetry``:

.. code:: shell

    poetry add pyobas

Call into OpenBAS!
-----
As a demonstration, let's imagine we want to make a query for active users on a running OpenBAS server.

.. code:: python

    from pyobas.client import OpenBAS;

    def main():
        # for example
        url = "__OPENBAS_SERVER_URL__"
        # find yours in your own profile on OpenBAS
        token = "__API_TOKEN__"

        client = OpenBAS(url, token)

        users = client.user.list()

        for user in users:
            print(user.user_email)

    if __name__ == "__main__":
        main()

Feature set
===========
PyOBAS is not just an API client.

* Interact with OpenBAS and query or modify its entities via a straightforward REST API
* Extend OpenBAS with custom Injectors, allowing for new capabilities
* Integrate with third-party security software suites to track the outcome of a simulated attack