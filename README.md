Tiny script to create private 1:1 channels on Slack.

A private 1:1 channel gives you a communication channel that is not as intrusive as regular DMs, which always generate notifications unless the other person is in do-not-disturb mode.

## Usage

```
pip install -r requirements.txt
```

Get yourself a access token:

1. Create an app https://api.slack.com/apps
2. OAuth & Permissions > Scopes > User Token Scopes: add
   - `channels:read` (for the `channel_members` command)
   - `users:read` (for the `channel_members` command)
   - `groups:read`
   - `groups:write`
   - `chat:write` (for the first message)
3. Install to workspace
4. There will be an OAuth access token ready for copying

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

`other-name` and `my-name` are only used for specifying the name of the channel.
The names will be sorted alphabetically and concatenated with a hyphen.
For example, `alice-bob`, or `bob-carol`.

You can find the ID of a user by going to their profile on Slack.

### Creating in bulk


Export a list of users:

```
SLACK_TOKEN=xoxp-xxxxxxxx python main.py channel_members <channel_name> > members.txt
```

Edit `members.txt` so that it contains only those users you want to create 1:1 channels for.

The format is:

```
<other-name> <user-id> <my-name>
bob U0XYABCDE alice
carol UFGHIJKL alice
...
```

As was the case with one-off channel creation, `other-name` and `my-name` only matter for how channel names are generated.

To dry run:

```
cat members.txt | sed -e 's/[[:blank:]]+$//' | SLACK_TOKEN=xoxp-xxxxxxx xargs -L1 python main.py create --first-message "Message to post after creating a channel (optional)" --purpose "Purpose of the channel (optional)" --dry-run
```

Execute the above without the `--dry-run` flag to actually create channels.
