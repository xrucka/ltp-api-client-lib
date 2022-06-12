import click
from ltp_api_client_lib.archive import Archive
from ltp_api_client_lib.audit import Audit
from ltp_api_client_lib.bagit import Bagit
import pprint
import json


@click.group()
@click.option(
    '--token', '-t', help='Token for communication with LTP API'
)
@click.option(
    '--context',
    '-c',
    help='Context/group for communication with LTP API',
)
@click.option(
    '--address',
    '-a',
    default='https://ltp.cesnet.cz/api',
    help='Http address of  LTP API',
)
@click.pass_context
def cli(ctx, token, context, address):
    ctx.ensure_object(dict)
    ctx.obj['token'] = token
    ctx.obj['context'] = context
    ctx.obj['address'] = address


@click.group()
@click.pass_context
def archive(ctx):
    if 'token' not in ctx.obj or 'context' not in ctx.obj:
        return "Context & Token has to be set for archive"
    token = ctx.obj['token']
    context = ctx.obj['context']
    address = ctx.obj['address']
    ctx.obj['archive'] = (
        Archive(ltp_api_address=address).setup_context(context).setup_token(token)
    )


@click.command()
@click.option('--path', '-p', required=True, help='Path to archive')
@click.option(
    '--data',
    '-d',
    required=True,
    help='Data in JSON format: {"name": "test", "user_metadata": {}}',
)
@click.pass_context
def create(ctx, path, data):
    data = json.loads(data)
    resp = ctx.obj['archive'].create(data, path)
    pprint.pprint(resp.data)


@click.command()
@click.option(
    '--id', '-i', type=int, required=True, help='Primary key of archive object'
)
@click.option(
    '--data',
    '-d',
    required=True,
    help='Data in JSON format: {"name": "test", "user_metadata": {}}',
)
@click.option(
    '--path', '-p', help='Path to archive which should replace archive on selected id'
)
@click.pass_context
def update(ctx, id, data, path=None):
    data = json.loads(data)
    if path is None:
        resp = ctx.obj['archive'].patch(id, data)
    else:
        resp = ctx.obj['archive'].put(id, data, path)
    pprint.pprint(resp.data)


@click.command(name='download')
@click.option(
    '--id', '-i', type=int, required=True, help='Primary key of archive object'
)
@click.option(
    '--path',
    '-p',
    required=True,
    help='Path to archive which should replace archive on selected id',
)
@click.pass_context
def download(ctx, id, path):
    resp = ctx.obj['archive'].download(id, path)
    pprint.pprint(resp.data)


@click.command()
@click.option(
    '--id', '-i', type=int, required=True, help='Primary key of archive object'
)
@click.pass_context
def get(ctx, id):
    resp = ctx.obj['archive'].get(id)
    pprint.pprint(resp.data)


@click.command(name='list')
@click.option('--limit', '-l', type=int, default=10, help='Limit for fetched data')
@click.pass_context
def list_(ctx, limit=None):
    resp = ctx.obj['archive'].list()
    pprint.pprint(resp.data)


@click.group()
@click.pass_context
def audit(ctx):
    if 'token' not in ctx.obj or 'context' not in ctx.obj:
        return "Context & Token has to be set for audit"
    token = ctx.obj['token']
    context = ctx.obj['context']
    address = ctx.obj['address']
    ctx.obj['audit'] = (
        Audit(ltp_api_address=address).setup_context(context).setup_token(token)
    )


@click.command(name='get')
@click.option(
    '--id', '-i', type=int, required=True, help='Primary key of archive object'
)
@click.option('--limit', '-l', type=int, default=10, help='Limit for fetched data')
@click.pass_context
def get_for_archive(ctx, id, limit):
    resp = ctx.obj['audit'].get_for_archive(id, limit)
    pprint.pprint(resp.data)


@click.command(name='list')
@click.option('--limit', '-l', type=int, default=10, help='Limit for fetched data')
@click.pass_context
def list_for_archive(ctx, limit=10):
    resp = ctx.obj['audit'].list_for_archive(limit)
    pprint.pprint(resp.data)



@click.group()
@click.pass_context
def bagit(ctx):
    ctx.obj['bagit'] = (
        Bagit()
    )
@click.command(name='build')
@click.option(
    '--path',
    '-p',
    required=True,
    help='Path to data which are desired to bag-it',
)
@click.option(
    '--json_metadata',
    '-j',
    required=True,
    help='Metadata for bagit see https://datatracker.ietf.org/doc/html/rfc8493#section-2.2.2\
    minimal is Contact-Name.',
)
@click.pass_context
def build(ctx, path, json_metadata):
    resp = ctx.obj['bagit'].build(path, json_metadata)
    pprint.pprint(resp)


@click.command(name='zipit')
@click.option(
    '--zip_name',
    '-z',
    required=True,
    help='Zip name',
)
@click.option(
    '--path',
    '-p',
    required=True,
    help='Path to data which are desired to zip-it',
)
@click.pass_context
def zipit(ctx, zip_name, path):
    resp = ctx.obj['bagit'].zipit(zip_name, path)
    pprint.pprint(resp)


@click.command(name='validate')
@click.option(
    '--path',
    '-p',
    required=True,
    help='Path to data which are desired to bag-it',
)

@click.pass_context
def validate(ctx, path):
    resp = ctx.obj['bagit'].validate(path)
    pprint.pprint(resp)


archive.add_command(create)
archive.add_command(update)
archive.add_command(get)
archive.add_command(list_)
archive.add_command(download)
audit.add_command(get_for_archive)
audit.add_command(list_for_archive)
cli.add_command(archive)
cli.add_command(audit)
bagit.add_command(build)
bagit.add_command(validate)
bagit.add_command(zipit)
cli.add_command(bagit)

if __name__ == '__main__':
    cli()
