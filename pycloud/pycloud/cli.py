# -*- coding: utf-8 -*-

"""Console script for pycloud."""
import sys
import click

from pycloud.logger import configure_logger, get_logger, ALLOWED_LOG_LEVELS
from pycloud.pycloud.provisioners.plan_executor import PlanExecutor

logger = get_logger()

def validate_for_aws(access_key, secret_key):
    '''
    Validates the provided aws access_key and secret_key.
    '''
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



@click.group()
@click.option('-l', '--log-level', envvar='PYCLOUD_LOG_LEVEL',
              help='Set the Log Level for the command. Default: info',
              type=click.Choice([l.lower() for l in ALLOWED_LOG_LEVELS]),
              default='info')
@click.pass_context
def pycloud(ctx, log_level):
    """
    PyCloud Provisions a VM in the cloud,
    """
    ctx.obj = {}
    configure_logger(level=log_level)
    return 0

@pycloud.command()
@click.option('-a', '--access-key', envvar='AWS_ACCESS_KEY',
              help='AWS Access Key. You can also set environment variable AWS_ACCESS_KEY.')
@click.option('-s', '--secret-key', envvar='AWS_SECRET_KEY',
              help='AWS Secret Key. You can also set environment variable AWS_SECRET_KEY.')
@click.argument('plan', type=click.Path(exists=True))
@click.pass_context
def execute(ctx, access_key, secret_key, plan):
    '''
    Sets up the infrastructure as specified by the plan.
    '''
    validate_for_aws(access_key, secret_key)
    ctx.obj['AWS_ACCESS_KEY'] = access_key
    ctx.obj['AWS_SECRET_KEY'] = secret_key
    executor = PlanExecutor(plan, _globals=ctx.obj)
    executor.execute_plan()


@pycloud.command()
@click.option('-a', '--access-key', envvar='AWS_ACCESS_KEY',
              help='AWS Access Key. You can also set environment variable AWS_ACCESS_KEY.')
@click.option('-s', '--secret-key', envvar='AWS_SECRET_KEY',
              help='AWS Secret Key. You can also set environment variable AWS_SECRET_KEY.')
@click.argument('plan', type=click.Path(exists=True))
@click.pass_context
def dry_run(ctx, access_key, secret_key, plan):
    '''
    Sets up the infrastructure requested in the CLI.
    '''
    validate_for_aws(access_key, secret_key)
    ctx.obj['AWS_ACCESS_KEY'] = access_key
    ctx.obj['AWS_SECRET_KEY'] = secret_key
    executor = PlanExecutor(plan, _globals=ctx.obj)
    executor.dry_execute_plan()

@pycloud.command()
@click.pass_context
def docs(ctx):
    '''
    Dumps the documentation for the available provisioners.
    '''
    executor = PlanExecutor(None, _globals=ctx.obj)
    executor.help()



if __name__ == "__main__":
    sys.exit(pycloud())  # pragma: no cover
