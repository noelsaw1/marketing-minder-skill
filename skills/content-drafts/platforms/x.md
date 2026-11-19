# X drafts

Write posts a person can approve. The X drafts connector saves drafts. It does not publish them.

## Length

A standard post is 280 weighted characters. Count a normal Latin letter as 1. Count an emoji or a wide character, including Chinese, Japanese and Korean, as 2. Count each `http` or `https` URL as 23, whatever its length, because X wraps links. Attached images do not add to the count. The script's counter is the gate for the queue. The X composer is the last check, because a combined emoji can weigh less than this counter estimates.

An account with X Premium can hold 25,000 characters in one post. Use that limit only after the person says so, by passing `--x-premium` when the calendar is built. The first 280 characters still have to earn the click. Leave the flag off otherwise.

## Shape

One idea per post. Put the point in the first line. Zero or two hashtags is enough; more than two is a warning, and the tags count toward the 280.

A thread is two to six posts. Each post has its own 280. The first post is the hook. Put a link on the last post when you need one. More than eight posts raises a warning. The export file keeps every post in order. The Buffer CSV keeps the first post only, because Buffer's bulk upload has no thread.

## What to avoid

Skip a claim the brand file or the event file does not support. Read recent posts from this account when an X reading connector is available, and do not repeat them. When the connector is missing, say so and draft from the files you have.
