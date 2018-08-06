=========
PyCloud
=========

.. image:: https://travis-ci.org/davydany/pycloud.svg?branch=master
    :target: https://travis-ci.org/davydany/pycloud


What it Does
------------

A simple cloud provisioner for provisioning VMs on EC2 and configuring them
based on a simple plan.

Getting Started
---------------

.. code:: bash

  pip install --upgrade git+https://github.com/davydany/pycloud

Usage
-----

To see all the options available for you, run:

.. code:: bash

    pycloud --help

PyCloud uses a plan file to setup your infrastructure, similar to how 
Ansible works. There are a few sample files in **example_plans** directory.

Here is how to execute a plan:

.. code:: bash

    export AWS_ACCESS_KEY="<YOUR_AWS_ACCESS_KEY>"
    export AWS_SECRET_KEY="<YOUR_AWS_SECRET_KEY>"

    pycloud setup ./example_plans/test_plan.yml

If you'd like to see all the available provisioners, along with their required
and optional arguments, run:

.. code:: bash

    pycloud docs

If you'd like to run the process in reverse, and teardown the setup plan, run:

.. code:: bash

    pycloud teardown ./example_plans/test_plan.yml

If you'd like run both **setup** and **teardown** in dry-run, mode to verify
the plans are valid, run the following, respectively:

.. code:: bash

    # dry-run setup
    pycloud dry_setup ./example_plans/test_plan.yml

    # dry-run teardown
    pycloud dry_teardown ./example_plans/test_plan.yml