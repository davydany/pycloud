import time
# 
from boto import ec2

from pycloud.core.keypair_storage import KeyPairStorage
from pycloud.core.provisioners.base import BaseProvisioner
from pycloud.core.provisioners.utils.mixins import AWSProvisionerMixin
from pycloud.core.registry import Registry

class EC2KeyPairProvisioner(AWSProvisionerMixin, BaseProvisioner):

    name = 'EC2 Key Pair Provisioner'

    slug = 'ec2_key_pair'

    description = 'The EC2 Key Pair Provisioner can be used to create a AWS EC2 Service\'s Key Pair.'

    required_args = ['region', 'key_name']

    optional_args = None

    def verify(self, name, key_name=None, region=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None):

        self.verify_is_not_null('region', region)
        self.verify_is_not_null('key_name', key_name)
        self.verify_is_not_null('AWS_ACCESS_KEY', AWS_ACCESS_KEY)
        self.verify_is_not_null('AWS_SECRET_KEY', AWS_SECRET_KEY)

    def up(self, name, key_name=None, region=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None):

        # create connection
        conn = self.ec2_connect(region, AWS_ACCESS_KEY, AWS_SECRET_KEY)
        
        # determine if this key pair already exists or not
        try:
            existing_key_pairs = conn.get_all_key_pairs(keynames=[key_name])
            self.logger.warn('A Key Pair with the name "%s" already exists. Skipping now.' % (key_name))
        except Exception:
            existing_key_pairs = []

        if existing_key_pairs == []:
            self.logger.info('Creating a new Key Pair with name "%s"'% (key_name))
            ec2_keypair = conn.create_key_pair(key_name, dry_run=self.dry_run)
            fs_keypair = KeyPairStorage(key_name)
            fs_keypair.save(ec2_keypair)
            
    
    def down(self, name, key_name=None, region=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None):

        # create connection
        conn = self.ec2_connect(region, AWS_ACCESS_KEY, AWS_SECRET_KEY)

        # determine if this key pair already exists or not
        try:
            self.logger.info('Deleting Key Pair with name "%s"'% (key_name))
            existing_key_pairs = conn.get_all_key_pairs(keynames=[key_name])
            conn.delete_key_pair(key_name, dry_run=self.dry_run)
            fs_keypair = KeyPairStorage(key_name)
            fs_keypair.delete()

        except Exception:
            self.logger.warn('A Key Pair with the name "%s" does not exist. Skipping now.' % (key_name))
            


class EC2SecurityGroupProvisioner(AWSProvisionerMixin, BaseProvisioner):

    name = 'EC2 Security Group Provisioner'

    slug = 'ec2_security_group'

    description = 'The EC2 Security Group provisioner can be used to create a AWS\'s EC2 Service\'s Security Groups'

    required_args = ['group_name', 'group_description', 'region', 'rules']

    optional_args = None

    def verify(self, name, 
            group_name=None, group_description=None, 
            region=None, rules=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None):

        self.verify_is_not_null('group_name', group_name)
        self.verify_is_not_null('region', region)
        self.verify_is_not_null('rules', rules)
        self.verify_is_not_null('AWS_ACCESS_KEY', AWS_ACCESS_KEY)
        self.verify_is_not_null('AWS_SECRET_KEY', AWS_SECRET_KEY)

        # ensure that the rules are setup properly
        self.verify_is_type('rules', rules, list)
        for rule in rules:
            rule_keys = list(rule.keys())
            if len(rule_keys) != 1:
                raise ValueError('Rule "%s" must have only 1 key at the top level. It has "%d".' % (
                    rule,
                    len(rule_keys)
                ))
            allowed_protocols = ['tcp', 'udp', 'icmp']
            protocol = rule_keys[0]
            if protocol not in allowed_protocols:
                raise ValueError('Protocol "%s" is not a valid protocol. Valid values: %s' % (protocol, str(allowed_protocols)))

            rule_key = rule_keys[0]
            if 'start' not in rule[rule_key]:
                raise ValueError('Rule "%s" does not have "start" value.' % (rule_key))
            if 'end' not in rule[rule_key]:
                raise ValueError('Rule "%s" does not have "end" value.' % (rule_key))
            if 'cidr_ip' not in rule[rule_key]:
                raise ValueError('Rule "%s" does not have "cidr_ip" value.' % (rule_key))


    def up(self, name, 
            group_name=None, group_description=None, 
            region=None, rules=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None):

        # make the connection and get all the available security groups
        conn = self.ec2_connect(region, AWS_ACCESS_KEY, AWS_SECRET_KEY)
        try:

            existing_security_groups = conn.get_all_security_groups(groupnames=[group_name])
            self.logger.info("Security Group already exists. Using Security Group '%s'" % group_name)
            security_group = existing_security_groups[0]
        except Exception:

            self.logger.info("Creating New Security Group '%s'" % group_name)
            security_group = conn.create_security_group(group_name, group_description)
        
            
        existing_rules = security_group.rules
        for rule in rules:

            rule_keys = list(rule.keys())
            protocol = rule_keys[0]
            from_port = str(rule[protocol]['start'])
            to_port = str(rule[protocol]['end'])
            cidr_ip = rule[protocol]['cidr_ip']

            rule_exists = False
            for existing_rule in existing_rules:

                if existing_rule.ip_protocol == protocol and \
                    existing_rule.from_port == from_port and \
                    existing_rule.to_port == to_port and \
                    cidr_ip in [str(g) for g in existing_rule.grants]:
                    
                    rule_exists = True
                    break

            if rule_exists:
                self.logger.warn("Rule: '%s' (%s-%s :: %s) already exists. Skipping Creation." % (
                    protocol,
                    from_port,
                    to_port,
                    cidr_ip
                ))
            else:
                self.logger.info("Authorizing Rule for Security Group '%s': %s (%s-%s) for %s" % (
                    group_name, 
                    protocol, 
                    from_port, 
                    to_port, 
                    cidr_ip))
                security_group.authorize(
                    ip_protocol=protocol, 
                    from_port=from_port, 
                    to_port=to_port, 
                    cidr_ip=cidr_ip, 
                    dry_run=self.dry_run)


    def down(self, name, 
            group_name=None, group_description=None, 
            region=None, rules=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None):

        # make the connection and get all the available security groups
        conn = self.ec2_connect(region, AWS_ACCESS_KEY, AWS_SECRET_KEY)
        try:
            existing_security_groups = conn.get_all_security_groups(groupnames=[group_name])
            self.logger.info('Deleting Security Group "%s".' % group_name)
            conn.delete_security_group(name=group_name, dry_run=self.dry_run)

        except Exception:
            self.logger.warning('Security Group "%s" does not exist. Skipping Now.' % group_name)
        

class EC2InstanceProvisioner(AWSProvisionerMixin, BaseProvisioner):

    name = 'EC2 Instance Provisioner'

    slug = 'ec2_instance'

    description = 'The EC2 Instance Provisioner can be used to Provision Amazon Web Service\'s EC2 Service'

    required_args = ['region', 'ami_id', 'instance_type', 'security_group', 'key_name', 'instance_id_ref']

    optional_args = ['min_count', 'max_count']

    def verify(self, name, region=None, ami_id=None, instance_type=None, security_group=None, key_name=None,
                  AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None, instance_id_ref=None, min_count=None, max_count=None):
        
        self.verify_is_not_null('region', region)
        self.verify_is_not_null('ami_id', ami_id)
        self.verify_is_not_null('instance_type', instance_type)
        self.verify_is_not_null('security_group', security_group)
        self.verify_is_not_null('key_name', key_name)
        self.verify_is_not_null('instance_id_ref', instance_id_ref)
        self.verify_is_not_null('security_group', security_group)
        self.verify_is_not_null('AWS_ACCESS_KEY', AWS_ACCESS_KEY)
        self.verify_is_not_null('AWS_SECRET_KEY', AWS_SECRET_KEY)

    def up(self, name, region=None, ami_id=None, instance_type=None, security_group=None, key_name=None,
                  AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None, instance_id_ref=None, min_count=None, max_count=None):


        # set default values for optional fields
        min_count = 1 if min_count == None else min_count
        max_count = 1 if max_count == None else max_count
        
        # create a connection and use boto to setup instances
        connection = self.ec2_connect(region, AWS_ACCESS_KEY, AWS_SECRET_KEY)

        # get the security group corresponding to the provided 'security_group' name
        sg = [s for s in connection.get_all_security_groups() if s.name == security_group]
        if len(sg) != 1:
            raise ValueError("Security Group does not exist. Please create using 'ec2_security_group' first.")
        else:
            sg = sg[0]

        # existing instances
        existing_instance_ids = self.config.get(instance_id_ref)
        if existing_instance_ids == None:
            
            # create the instances
            reservation = connection.run_instances(
                ami_id, 
                min_count=min_count,
                max_count=max_count,
                instance_type=instance_type, 
                security_group_ids=[sg.id],
                key_name=key_name,
                dry_run=self.dry_run)
            instances = reservation.instances
            self.logger.info("Created %d instances with reservation id: %s" % (len(reservation.instances), reservation.id))
            for instance in instances:
                self.logger.info("Instance ID '%s' was created." % (instance.id))
            instance_ids = [instance.id for instance in instances]

            # wait for all instances to start
            for instance in instances:
                while instance.state != 'running':
                    self.logger.info('Waiting for Instance '\
                        '(id=%s) to go from "%s" to "running"' % (
                            instance.id, instance.state))
                    time.sleep(5)
                    instance.update()
                time.sleep(5)
                self.logger.info("Instance State is '%s'" % (instance.state))

            # store instance state in config
            if not self.dry_run:
                self.config.set(instance_id_ref, instance_ids)
        else:
            self.logger.warning("Instances already exist for this task. Skipping Instance Creation.")

    def down(self, name, region=None, ami_id=None, instance_type=None, security_group=None, key_name=None,
                  AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None, instance_id_ref=None, min_count=None, max_count=None):
        
        # create a connection and use boto to setup instances
        connection = self.ec2_connect(region, AWS_ACCESS_KEY, AWS_SECRET_KEY)

        # get all the existing instance ids
        existing_instance_ids = self.config.get(instance_id_ref)
        if existing_instance_ids == None:
            self.logger.warning("There are no existing instances that were recorded.")
            self.logger.warning("The instances might exist, but the instance ids do not exist in the PyCloud local state.")
            self.logger.warning("Skipping EC2 Instance Provision teardown() process")
        else:
            self.logger.info('Terminating "%d" Instances.' % (len(existing_instance_ids)))
            connection.terminate_instances(instance_ids=existing_instance_ids, dry_run=self.dry_run)

            # store instance state in config
            if not self.dry_run:
                self.config.delete(instance_id_ref)


Registry.register_provisioner(EC2InstanceProvisioner)
Registry.register_provisioner(EC2SecurityGroupProvisioner)
Registry.register_provisioner(EC2KeyPairProvisioner)