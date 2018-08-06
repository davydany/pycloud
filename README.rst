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


If you'd like to run the process in reverse, and teardown the setup plan, run:

.. code:: bash

    pycloud teardown ./example_plans/test_plan.yml


If you'd like to see all the available provisioners, along with their required
and optional arguments, run:

.. code:: bash

    pycloud docs

Using the docs in **pycloud docs**, you can create your own plan, like the one
below:

.. code:: yaml

    ---
    tasks:
        - ec2_security_group:
            name: Create Security Groups for our Ubuntu Instance
            region: us-east-1a
            group_name: 'ubuntu_sg'
            group_description: 'The Ubuntu Security Group'
            rules:
                - tcp:
                    start: 22
                    end: 22
                    cidr_ip: '0.0.0.0/0'
            
        - ec2_key_pair:
            name: Create the Key Pair we need to access the Ubuntu Instance
            region: us-east-1a
            key_name: admin_kp
            
        - ec2_instance:
            name: Setup Simple Ubuntu Instance on AWS
            region: us-east-1a
            ami_id:  ami-456b493a
            instance_type: t2.micro
            security_group: ubuntu_sg
            key_name: admin_kp
            min_count: 1
            max_count: 2
            instance_id_ref: $ubuntu_vms

        - ssh_keygen:
            name: Generate a RSA Key for our user, Rick Sanchez! 
            key_type: 'rsa'
            file: id_rsa
            passphrase: ''
            out_dir: '/tmp/keys/'

        - user_add:
            name: Creates the Rick Sanchez user on the referenced Instances
            region: us-east-1a
            key_name: admin_kp
            user_name: rsanchez
            instance_id_ref: $ubuntu_vms
            default_shell: /bin/bash
            public_key: /tmp/keys/id_rsa.pub
