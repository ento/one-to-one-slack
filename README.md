Tiny script to create private 1:1 channels on Slack.

A private 1:1 channel gives you a communication channel between a specific person
that is not as intrusive as regular DMs, which always generate notifications unless
the other person is in do-not-disturb mode.

## Usage

```
pip install -r requirements.txt
```

Get yourself a [legacy Slack access token](https://api.slack.com/custom-integrations/legacy-tokens).

### One-off channel creation

```
SLACK_TOKEN=xoxp-xxxxxxx python main.py create \
    --first-message "Message to post after creating a channel (optional)" \
    --purpose "Purpose of the channel (optional)" \
    --dry-run \
    other-name \
    other-person-slack-user-id \
    my-name
```

Executing this without the `--dry-run` flag creates a new private channel.
The two members of the channel will be the user identified by the user ID and
the user to which the access token belongs to (you).

The name of the channel will be `<other-name>-<my-name>`, or
`<my-name>-<other-name>` if `<my-name>` comes first when sorted alphabetically.

You can copy the ID of a user by going to their profile on Slack.

### Creating in bulk


Export a list of users:

```
SLACK_TOKEN=xoxp-xxxxxxxx python main.py channel_members <channel_name> > members.txt
```

Edit `members.txt` so that it contains only those users you want to create a 1:1 channel for.

The format is:

```
<other-name> <user-id> <my-name>
bob U0XYABCDE alice
carol UFGHIJKL alice
...
```

To dry run:

```
cat members.txt | sed -e 's/[[:blank:]]+$//' | SLACK_TOKEN=xoxp-xxxxxxx xargs -L1 python main.py create --first-message "Message to post after creating a channel (optional)" --purpose "Purpose of the channel (optional)" --dry-run
```

Execute the above without the `--dry-run` flag to actually create channels.
