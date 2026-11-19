# Instagram drafts

Every Instagram item needs a picture. The caption is the words. The visual brief is the instructions for the image the person will make or approve. Nothing is posted from this file.

## Caption

The hard limit is 2,200 characters. Put the hook in the first line, about 125 characters, before "more".

Use 5 or fewer hashtags, in the caption. More than five is a warning. More than 30 fails validation, which is the cap in Meta's API reference; older captions sometimes stuffed 30 tags, and that is a poor fit here. Do not hide extra tags in the first comment.

Hashtags, line breaks and the link all count toward the 2,200.

## Visual

Write a `visual_brief` for a single image, or a `carousel` list of up to 20 slides. Twenty is the feed maximum. One extra slide fails validation. Say the orientation once for the whole carousel (portrait 1080×1350 or square 1080×1080) and, for each slide, the words that must appear and what the picture shows.

Add `alt_text` that describes the image. The limit is 1,000 characters. Missing alt text is a warning.

`image_url` stays empty until the file is a public `https` link ending in `.jpg`, `.png`, `.webp` or `.gif`. A path under `brands/` is the working copy, not a Buffer image. Buffer's bulk upload accepts one image per row and rejects an Instagram row without one, so the export leaves those rows out and lists them. The caption stays in the queue.

## What to avoid

Do not claim the image exists because the brief is written. Do not invent a product photo, a review, or a scarcity line. Tie the caption to the offer and, when an event file has an in-file date, to that date.
