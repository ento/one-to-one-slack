#!/usr/bin/env python3
import re
import logging

import click
import requests
import slack
from slack.io.requests import SlackAPI
from slack.exceptions import SlackAPIError


logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s')
logger = logging.getLogger(None)


@click.group()
@click.option('--token')
@click.pass_context
def cli(ctx, token):
    ctx.obj = token


@cli.command()
@click.argument('other_name')
@click.argument('other_id')
@click.argument('my_name')
@click.option('--purpose')
@click.option('--first-message')
@click.option('--dry-run/--no-dry-run', default=False)
@click.pass_obj
def create(slack_token, other_name, other_id, my_name, purpose, first_message, dry_run):
    session = requests.session()
    client = SlackAPI(token=slack_token, session=session)

    new_channel_name = format_channel_name(my_name, other_name)

    channel_info = None

    if dry_run:
        logger.info('would have attempted to create a channel named %s', new_channel_name)
    else:
        channel_info = create_private_channel(client, new_channel_name)

    if not channel_info and not dry_run:
        logger.error('not doing anything further, such as inviting the other user, setting channel purpose, etc.')
        return

    if dry_run:
        logger.info('would have invited %s', other_name)
    else:
        invite_user(client, channel_info['id'], other_id)

    if purpose:
        if dry_run:
            logger.info('would have set purpose to: %s', purpose)
        else:
            set_channel_purpose(client, channel_info['id'], purpose)

    if first_message:
        if dry_run:
            logger.info('would have posted a message: %s', first_message)
        else:
            post_first_message(client, channel_info['id'], first_message)

    if not dry_run:
        logger.info('channel is ready: %s', channel_info['name'])


def create_private_channel(client, new_channel_name) -> dict:
    try:
        create_result = client.query(slack.methods.CONVERSATIONS_CREATE, {
            'name': new_channel_name,
            'is_private': True})
        logger.info('created channel %s', new_channel_name)
        return create_result['channel']
    except SlackAPIError as e:
        logger.error(
            'could not create channel %s because of error %r; looking for existing channel',
            new_channel_name, e)
        return find_channel_by_name(client, new_channel_name, include_public=False)



def invite_user(client, channel_id, member_id):
    try:
        invite_result = client.query(slack.methods.CONVERSATIONS_INVITE, {
            'channel': channel_id,
            'users': member_id})
        logger.info('invited the other member')
    except SlackAPIError as e:
        logger.warn('could not invite the user: %s', e)


def post_first_message(client, channel_id, text):
    try:
        post_result = client.query(slack.methods.CHAT_POST_MESSAGE, {
            'channel': channel_id,
            'text': text,
            'as_user': True})
        logger.info('posted the first message')
    except SlackAPIError as e:
        logger.warn('could not post the first message: %s', e)


def set_channel_purpose(client, channel_id, purpose):
    try:
        purpose_result = client.query(slack.methods.CONVERSATIONS_SET_PURPOSE, {
            'channel': channel_id,
            'purpose': purpose})
        logger.info('channel purpose has been set')
    except SlackAPIError as e:
        logger.warn('could not set the purpose: %s', e)


@cli.command()
@click.argument('channel_name')
@click.pass_obj
def channel_members(slack_token, channel_name):
    session = requests.session()
    client = SlackAPI(token=slack_token, session=session)
    channel = find_channel_by_name(client, channel_name, include_public=True)

    auth_info = client.query(slack.methods.AUTH_TEST)
    my_info = client.query(slack.methods.USERS_INFO, {'user': auth_info['user_id']})['user']

    members = client.query(slack.methods.CONVERSATIONS_MEMBERS, {'channel': channel['id']})['members']
    for member_id in members:
        user_info = client.query(slack.methods.USERS_INFO, {'user': member_id})['user']
        if user_info['deleted'] or user_info['is_bot']:
            continue

        if user_info['id'] == my_info['id']:
            continue

        print(
            user_info['profile']['display_name_normalized'],
            user_info['id'],
            my_info['profile']['display_name_normalized'])


def find_channel_by_name(client, channel_name, include_public=False):
    raw_channel_name = re.sub(r'^#', '', channel_name)
    types = 'public_channel,private_channel' if include_public else 'private_channel'
    for channel in client.iter(slack.methods.CONVERSATIONS_LIST, {
            'types': types}):
        if channel['name'] == raw_channel_name:
            return channel


def format_channel_name(my_name, other_name):
    raw_names = [re.sub(r'^@', '', name) for name in [my_name, other_name]]
    return '-'.join(sorted(raw_names))


if __name__ == '__main__':
    cli(auto_envvar_prefix='SLACK')
