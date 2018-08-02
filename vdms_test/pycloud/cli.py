# -*- coding: utf-8 -*-

"""Console script for vdms_test."""
import sys
import click

from vdms_test.logger import configure_logger, get_logger
from vdms_test.pycloud.provisioners.plan_executor import PlanExecutor

logger = get_logger()


@click.group()
@click.option('-a', '--access-key', envvar='AWS_ACCESS_KEY',
              help='AWS Access Key. You can also set environment variable AWS_ACCESS_KEY.')
@click.option('-s', '--secret-key', envvar='AWS_SECRET_KEY',
              help='AWS Secret Key. You can also set environment variable AWS_SECRET_KEY.')
@click.pass_context
def pycloud(ctx, access_key, secret_key):
    """
    PyCloud Provisions a VM in the cloud,
    """
    ctx.obj = {}
    if not access_key:
        click.secho(
            'Please provide AWS Access Key either as a parameter "--access-key=VALUE" '
            'or as an environment variable AWS_ACCESS_KEY',
            fg='red')
        raise click.BadParameter('Access Key is not set.')
    if not secret_key:
        click.secho(
            'Please provide AWS Secret Key either as a parameter "--secret-key=VALUE" '
            'or as an environment variable AWS_SECRET_KEY',
            fg='red')
        raise click.BadParameter('Secret Key is not set.')

    logger.debug("Access KEY: %s" % (access_key))
    logger.debug("Secret KEY: %s" % ("*" * len(secret_key)))

    ctx.obj['AWS_ACCESS_KEY'] = access_key
    ctx.obj['AWS_SECRET_KEY'] = secret_key
    configure_logger()
    return 0

@pycloud.command()
@click.argument('plan', type=click.Path(exists=True))
@click.pass_context
def execute(ctx, plan):
    '''
    Sets up the infrastructure as specified by the plan.
    '''
    executor = PlanExecutor(plan, _globals=ctx.obj)
    executor.execute_plan()


@pycloud.command()
@click.argument('plan', type=click.Path(exists=True))
@click.pass_context
def dry_run(ctx, plan):
    '''
    Sets up the infrastructure requested in the CLI.
    :param ctx:
    :return:
    '''
    executor = PlanExecutor(plan, _globals=ctx.obj)
    executor.dry_execute_plan()

@pycloud.command()
@click.pass_context
def help(ctx):
    '''
    Dumps the documentation for the available provisioners.
    '''
    executor = PlanExecutor(None, _globals=ctx.obj)
    executor.help()



if __name__ == "__main__":
    sys.exit(pycloud())  # pragma: no cover