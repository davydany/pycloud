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

  pip install --upgrade pycloud

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

    pycloud execute ./example_plans/test_plan.yml

If you'd like to see all the available provisioners, along with their required
and optional arguments, run:

.. code:: bash

    pycloud docs