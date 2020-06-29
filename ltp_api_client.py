import click
from ltp_api_client_lib.archive import Archive
from ltp_api_client_lib.audit import Audit
import pprint
import json


@click.group()
@click.option('--token', '-t', required=True, help='Token for communication with LTP API')
@click.option('--context', '-c', required=True, help='Context/group for communication with LTP API')
@click.option('--address', '-a', default="https://rep2.du2.cesnet.cz/api", help='Http address of  LTP API')
@click.pass_context
def cli(ctx, token, context, address):
    ctx.ensure_object(dict)
    ctx.obj['token'] = token
    ctx.obj['context'] = context
    ctx.obj['address'] = address


@click.group()
@click.pass_context
def archive(ctx):
    token = ctx.obj['token']
    context = ctx.obj['context']
    address = ctx.obj['address']
    ctx.obj['archive'] = Archive(ltp_api_address=address).setup_context(context).setup_token(token)


@click.command()
@click.option('--path', '-p', required=True, help='Path to archive')
@click.option('--data', '-d', required=True, help='Data in JSON format: {"name": "test", "user_metadata": {}}')
@click.pass_context
def create(ctx, path, data):
    data = json.loads(data)
    resp = ctx.obj["archive"].create(data, path)
    pprint.pprint(resp.data)


@click.command()
@click.option('--id', '-i', type=int, required=True, help='Primary key of archive object')
@click.option('--data', '-d', required=True, help='Data in JSON format: {"name": "test", "user_metadata": {}}')
@click.option('--path', '-p', help='Path to archive which should replace archive on selected id')
@click.pass_context
def update(ctx, id, data, path=None):
    data = json.loads(data)
    if path is None:
        resp = ctx.obj["archive"].patch(id, data)
    else:
        resp = ctx.obj["archive"].put(id, data, path)
    pprint.pprint(resp.data)


@click.command()
@click.option('--id', '-i', type=int, required=True, help='Primary key of archive object')
@click.pass_context
def get(ctx, id):
    resp = ctx.obj["archive"].get(id)
    pprint.pprint(resp.data)


@click.command(name="list")
@click.option('--limit', '-l', type=int, default=10, help='Limit for fetched data')
@click.pass_context
def list_(ctx, limit=None):
    resp = ctx.obj["archive"].list()
    pprint.pprint(resp.data)


@click.group()
@click.pass_context
def audit(ctx):
    token = ctx.obj['token']
    context = ctx.obj['context']
    address = ctx.obj['address']
    ctx.obj['audit'] = Audit(ltp_api_address=address).setup_context(context).setup_token(token)


@click.command(name="get")
@click.option('--id', '-i', type=int, required=True, help='Primary key of archive object')
@click.option('--limit', '-l', type=int, default=10, help='Limit for fetched data')
@click.pass_context
def get_for_archive(ctx, id, limit):
    resp = ctx.obj["audit"].get_for_archive(id, limit)
    pprint.pprint(resp.data)


@click.command(name="list")
@click.option('--limit', '-l', type=int, default=10, help='Limit for fetched data')
@click.pass_context
def list_for_archive(ctx, limit=10):
    resp = ctx.obj["audit"].list_for_archive(limit)
    pprint.pprint(resp.data)


archive.add_command(create)
archive.add_command(update)
archive.add_command(get)
archive.add_command(list_)
audit.add_command(get_for_archive)
audit.add_command(list_for_archive)
cli.add_command(archive)
cli.add_command(audit)

if __name__ == '__main__':
    cli()
