#!/usr/bin/env python3
"""Build and check a social draft queue for one business.

Reads brands/<business>/brand.md, writes a queue under
brands/<business>/content/, and exports drafts for a person to approve.
The publish command stays off unless --approve-publish is set and
CONTENT_QUEUE_ALLOW_PUBLISH=1. That command creates Postiz drafts only.
"""

import argparse
import csv
import datetime
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCHEMA = "marketing-minder.content-queue.v1"
X_DRAFTS_SCHEMA = "marketing-minder.x-drafts.v1"
POSTIZ_SCHEMA = "marketing-minder.postiz-drafts.v1"
EXPORT_SCHEMA = "marketing-minder.content-export.v1"

PLATFORMS = ("x", "linkedin", "instagram")
STATUSES = ("slot", "draft", "exported", "queued-draft")
BUFFER_COLUMNS = ("Text", "Image URL", "Tags", "Posting Time")
CONTENT_FIELDS = (
    "text",
    "thread",
    "hashtags",
    "link",
    "image_url",
    "alt_text",
    "visual_brief",
    "carousel",
    "basis",
    "source",
)
FORMATS = ("buffer", "postiz", "x-drafts")

# Limits the platform guides describe. X uses a weighted count.
X_LIMIT = 280
X_PREMIUM_LIMIT = 25000
X_URL_WEIGHT = 23
X_HASHTAG_WARN = 2
THREAD_WARN = 8
LINKEDIN_LIMIT = 3000
LINKEDIN_RECOMMENDED = 1500
LINKEDIN_SEE_MORE = 210
LINKEDIN_HASHTAG_WARN = 5
INSTAGRAM_LIMIT = 2200
INSTAGRAM_HASHTAG_LIMIT = 30
INSTAGRAM_HASHTAG_RECOMMENDED = 5
INSTAGRAM_SEE_MORE = 125
INSTAGRAM_CAROUSEL_MAX = 20
ALT_TEXT_LIMIT = 1000
POSTIZ_HOURLY_LIMIT = 30

CADENCE = (
    (0, "08:30", "linkedin", "Founder note in the brand voice"),
    (1, "09:15", "x", "One observation the ideal customer would stop for"),
    (2, "11:00", "instagram", "Visual or carousel that shows the offer"),
    (3, "12:30", "x", "A useful point, or a short thread"),
    (4, "08:30", "linkedin", "Offer or story, tied to a key date when one falls this week"),
    (5, "10:00", "instagram", "A second visual, from a different angle"),
    (6, "17:00", "x", "A lighter post with one idea"),
)

INTEGRATION_ENV = {
    "x": "POSTIZ_INTEGRATION_X",
    "linkedin": "POSTIZ_INTEGRATION_LINKEDIN",
    "instagram": "POSTIZ_INTEGRATION_INSTAGRAM",
}

SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
URL_RE = re.compile(r"https?://[^\s<>]+", re.IGNORECASE)
HASHTAG_RE = re.compile(r"(?<![\w])#([\w]+)", re.UNICODE)
HASHTAG_FULL_RE = re.compile(r"#[\w]+", re.UNICODE)
IMAGE_EXT_RE = re.compile(r"\.(?:jpe?g|png|webp|gif)(?:\?.*)?$", re.IGNORECASE)
LOCAL_TIME_RE = re.compile(r"(\d{4}-\d{2}-\d{2})[T ](\d{2}):(\d{2})")
OFFSET_RE = re.compile(r"([+-])(\d{2}):(\d{2})")
MILESTONE_RE = re.compile(r"T([+-])(\d+)\b")
TRAILING_URL_PUNCT = ".,!?:;)]}\"'`"
LAST_CHANCE_PHRASES = (
    "last chance",
    "last-chance",
    "order cut-off",
    "order cutoff",
    "cut-off",
    "cutoff",
)


class ValidationFailed(ValueError):
    def __init__(self, report):
        super().__init__("validation failed")
        self.report = report


def current_date():
    return datetime.date.today()


def require_slug(slug):
    if not isinstance(slug, str) or SLUG_RE.fullmatch(slug) is None:
        raise ValueError("Business must be a lowercase domain slug, such as example")
    return slug


def parse_date(value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValueError("Expected a date as YYYY-MM-DD, got {0!r}".format(value))


def parse_offset(value):
    match = OFFSET_RE.fullmatch((value or "").strip())
    if match is None:
        raise ValueError("UTC offset must look like -08:00 or +00:00")
    sign = 1 if match.group(1) == "+" else -1
    minutes = sign * (int(match.group(2)) * 60 + int(match.group(3)))
    if not -14 * 60 <= minutes <= 14 * 60:
        raise ValueError("UTC offset must look like -08:00 or +00:00")
    return datetime.timezone(datetime.timedelta(minutes=minutes))


def content_dir(root, slug):
    require_slug(slug)
    root = Path(root).resolve()
    directory = (root / "brands" / slug / "content").resolve()
    if directory.parent.name != slug or directory.name != "content":
        raise ValueError("Refusing to write outside brands/<business>/content")
    try:
        directory.relative_to(root / "brands" / slug)
    except ValueError:
        raise ValueError("Refusing to write outside brands/<business>/content")
    return directory


def ensure_brands_gitignored(root):
    root = Path(root).resolve()
    if not (root / ".git").exists():
        return
    result = subprocess.run(
        ["git", "-C", str(root), "check-ignore", "-q", "--", "brands/"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        raise ValueError("brands/ is not gitignored; refusing to write business content")


def ensure_private_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)


def assert_inside(root, path):
    root = Path(root).resolve()
    path = Path(path).resolve()
    if path != root and root not in path.parents:
        raise ValueError("Refusing to write outside the content directory")


def write_text(path, text):
    path = Path(path)
    ensure_private_dir(path.parent)
    assert_inside(path.parent, path)
    handle_fd, name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(name, 0o600)
        os.replace(name, path)
        os.chmod(path, 0o600)
    except Exception:
        try:
            os.unlink(name)
        except OSError:
            pass
        raise


def write_json(path, payload):
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def read_text(path):
    return Path(path).read_text(encoding="utf-8-sig")


def display_path(root, path):
    path = Path(path).resolve()
    root = Path(root).resolve()
    try:
        return str(path.relative_to(root))
    except ValueError:
        return "external file"


def parse_sections(text):
    matches = list(H2_RE.finditer(text))
    preamble = text[: matches[0].start()] if matches else text
    sections = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip()] = text[match.end() : end].strip()
    return preamble.strip(), sections


def field_value(preamble, label):
    prefix = label + ":"
    for line in preamble.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix) :].strip()
    return ""


def parse_brand(text):
    preamble, sections = parse_sections(text)
    title = ""
    for line in preamble.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    key_dates = []
    for line in sections.get("Key dates", "").splitlines():
        found = DATE_RE.search(line)
        if found:
            key_dates.append({"date": found.group(1), "text": line.strip()})
    return {
        "title": title,
        "site": field_value(preamble, "Site"),
        "last_read": field_value(preamble, "Last read from site"),
        "sections": sections,
        "key_dates": key_dates,
    }


def milestone_delta(line):
    if line.lower().startswith("launch"):
        return 0
    match = MILESTONE_RE.match(line)
    if match is None:
        return None
    sign = 1 if match.group(1) == "+" else -1
    return sign * int(match.group(2))


TARGET_LABELS = {
    "target date",
    "target launch date",
    "event date",
    "launch date",
    "in-file date",
    "date/timezone",
    "date and timezone",
    "date",
}
EVENT_NAME_RE = re.compile(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
ZONE_RE = re.compile(r"\b(UTC|GMT|[A-Za-z]+/[A-Za-z0-9_+-]+)\b")
UNKNOWN_DATE_RE = re.compile(r"\b(tbd|unknown|not set|none)\b", re.IGNORECASE)
PHASE_HEADINGS = ("phase", "milestone", "timeline", "campaign")


def split_label(line):
    stripped = line.strip()
    if stripped.startswith(("- ", "* ")):
        stripped = stripped[2:].strip()
    stripped = stripped.replace("**", "").strip()
    if ":" not in stripped:
        return None
    label, value = stripped.split(":", 1)
    label = re.sub(r"\s+", " ", label).strip().lower()
    if not label or len(label) > 40:
        return None
    return label, value.strip()


def parse_event_document(text, event_id, filename_date=""):
    """Read scheduling fields from an event file.

    The date inside the file is the one that schedules posts. filename_date
    is recorded and never used as the target date.
    """
    found_dates = []
    saw_unknown = False
    timezone = ""
    goal = ""
    milestones = []
    heading = ""
    for raw in text.splitlines():
        if raw.startswith("#"):
            heading = raw.lstrip("#").strip().lower()
            continue
        pair = split_label(raw)
        if pair:
            label, value = pair
            if label in TARGET_LABELS:
                if UNKNOWN_DATE_RE.search(value):
                    saw_unknown = True
                match = DATE_RE.search(value)
                if match:
                    found_dates.append(match.group(1))
                zone = ZONE_RE.search(value)
                if zone and not timezone:
                    timezone = zone.group(1)
            if label in ("goal", "goal/metric", "outcome") and not goal:
                goal = value[:200]
        in_phase = any(word in heading for word in PHASE_HEADINGS)
        stripped = raw.strip()
        if stripped.startswith("- "):
            body = stripped[2:].strip()
            offset = milestone_delta(body)
            dated = DATE_RE.search(body)
            if offset is not None or (in_phase and dated):
                milestones.append({
                    "text": body,
                    "offset": offset,
                    "date": dated.group(1) if dated else "",
                })
    unique = list(dict.fromkeys(found_dates))
    conflicts = []
    target = ""
    if len(unique) > 1:
        conflicts.append("target dates disagree: {0}".format(", ".join(unique)))
    elif unique:
        target = unique[0]
    return {
        "id": event_id,
        "filename_date": filename_date or "",
        "target_date": target,
        "timezone": timezone,
        "goal": goal,
        "legacy_link": "launch-plan.md" in text and event_id != "launch-plan",
        "conflicts": conflicts,
        "date_unknown": bool(saw_unknown and not target and not conflicts),
        "milestones": milestones,
    }


def parse_launch_plan(text):
    """Parse a legacy launch-plan.md. The in-file target date still wins."""
    event = parse_event_document(text, "launch-plan", "")
    return {
        "target_launch_date": event["target_date"],
        "milestones": [item["text"] for item in event["milestones"]],
        "event": event,
    }


def campaign_stage(slot_date, launch_date):
    if launch_date is None:
        return "none"
    delta = (slot_date - launch_date).days
    if delta == 0:
        return "announcement"
    if -7 <= delta <= -1:
        return "countdown"
    if -21 <= delta <= -8:
        return "teaser"
    if 1 <= delta <= 7:
        return "follow-up"
    return "none"


def notes_say_last_chance(notes):
    text = " ".join(notes).lower()
    return any(phrase in text for phrase in LAST_CHANCE_PHRASES)


def milestone_notes(event, day):
    if event.get("conflicts"):
        return []
    target = parse_date(event["target_date"]) if event.get("target_date") else None
    notes = []
    iso = day.isoformat()
    for milestone in event.get("milestones") or []:
        when = milestone.get("date") or ""
        if not when and milestone.get("offset") is not None and target is not None:
            when = (target + datetime.timedelta(days=milestone["offset"])).isoformat()
        if when == iso:
            notes.append("{0}: {1}".format(event["id"], milestone.get("text") or "milestone"))
    if target is not None and target == day:
        notes.append("{0}: launch day".format(event["id"]))
    return notes


def notes_for_day(day, key_dates, events):
    notes = []
    iso = day.isoformat()
    for item in key_dates or []:
        if item.get("date") == iso:
            notes.append(item.get("text") or iso)
    for event in events or []:
        notes.extend(milestone_notes(event, day))
    return notes


def purpose_with_notes(base, notes):
    if not notes:
        return base
    extra = " ".join(notes)
    if len(extra) > 240:
        extra = extra[:237] + "..."
    return base + " | " + extra


def blank_item(item_id, platform, scheduled_local, purpose, stage):
    return {
        "id": item_id,
        "platform": platform,
        "status": "slot",
        "scheduled_local": scheduled_local,
        "purpose": purpose,
        "campaign_stage": stage,
        "text": "",
        "thread": [],
        "hashtags": [],
        "link": "",
        "image_url": "",
        "alt_text": "",
        "visual_brief": "",
        "carousel": [],
        "source": "brand.md",
        "basis": "",
        "events": [],
    }


def stage_for_day(day, events, notes):
    refs = []
    stages = []
    for event in events or []:
        if event.get("conflicts") or not event.get("target_date"):
            continue
        stage = campaign_stage(day, parse_date(event["target_date"]))
        if stage == "none":
            continue
        stages.append(stage)
        refs.append({
            "id": event["id"],
            "stage": stage,
            "target_date": event["target_date"],
        })
    if notes_say_last_chance(notes):
        for ref in refs:
            ref["stage"] = "last-chance"
        return "last-chance", refs
    if not stages:
        return "none", []
    if len(set(stages)) == 1:
        return stages[0], refs
    return "mixed", refs


def build_week_items(week, brand, events):
    if week.weekday() != 0:
        raise ValueError("{0} is not a Monday".format(week.isoformat()))
    key_dates = (brand or {}).get("key_dates") or []
    items = []
    for offset, clock, platform, purpose in CADENCE:
        day = week + datetime.timedelta(days=offset)
        notes = notes_for_day(day, key_dates, events)
        stage, refs = stage_for_day(day, events, notes)
        item = blank_item(
            "{0}-{1}-1".format(day.isoformat(), platform),
            platform,
            "{0}T{1}".format(day.isoformat(), clock),
            purpose_with_notes(purpose, notes),
            stage,
        )
        item["events"] = refs
        items.append(item)
    return items


def build_idea_item(day, platform, events):
    if platform not in PLATFORMS:
        raise ValueError("Platform must be x, linkedin, or instagram")
    clock = "08:15" if platform == "x" else "08:00"
    purpose = "Daily X idea" if platform == "x" else "Daily idea"
    stage, refs = stage_for_day(day, events, [])
    item = blank_item(
        "{0}-{1}-idea".format(day.isoformat(), platform),
        platform,
        "{0}T{1}".format(day.isoformat(), clock),
        purpose,
        stage,
    )
    item["events"] = refs
    return item


def monday_on_or_before(day):
    return day - datetime.timedelta(days=day.weekday())


def empty_queue(slug, timezone, week):
    return {
        "schema": SCHEMA,
        "business": slug,
        "timezone": timezone,
        "week": week.isoformat(),
        "publish": False,
        "x_premium": False,
        "launch_date": "",
        "events": [],
        "legacy_warning": "",
        "sources": [],
        "updated": current_date().isoformat(),
        "items": [],
    }


def normalize_item(item):
    if not isinstance(item, dict):
        raise ValueError("Each queue item must be a JSON object")
    text = str(item.get("text") or "").strip()
    thread = item.get("thread") or []
    has_body = bool(text) or any(str(part).strip() for part in thread)
    if item.get("status") not in STATUSES:
        item["status"] = "draft" if has_body else "slot"
    return item


def prepare_queue(queue):
    if not isinstance(queue, dict):
        raise ValueError("Queue must be a JSON object")
    if queue.get("schema") != SCHEMA:
        raise ValueError("Queue schema is not {0}".format(SCHEMA))
    if not isinstance(queue.get("items"), list):
        raise ValueError("Queue items must be a list")
    for item in queue["items"]:
        normalize_item(item)
    queue["publish"] = False
    return queue


def load_queue(path):
    data = json.loads(read_text(path))
    return prepare_queue(data)


def merge_items(existing, incoming):
    by_id = {}
    order = []
    for item in existing:
        by_id[item["id"]] = item
        order.append(item["id"])
    for item in incoming:
        current = by_id.get(item["id"])
        if current is None:
            by_id[item["id"]] = item
            order.append(item["id"])
            continue
        if current.get("status") == "slot" and not str(current.get("text") or "").strip():
            current["purpose"] = item["purpose"]
            current["campaign_stage"] = item["campaign_stage"]
            current["scheduled_local"] = item["scheduled_local"]
            current["events"] = item.get("events") or []
    return [by_id[item_id] for item_id in order]


def render_calendar(queue):
    lines = [
        "# Content queue",
        "",
        "Generated from queue.json. Edit the JSON, or use the apply command. This file is overwritten.",
        "",
        "Business: {0}".format(queue.get("business", "")),
        "Timezone: {0}".format(queue.get("timezone", "")),
        "Week: {0}".format(queue.get("week", "")),
        "Publish: no",
        "",
    ]
    for item in queue.get("items") or []:
        lines.append("## {0} {1}".format(item.get("scheduled_local", ""), item.get("platform", "")))
        lines.append("")
        lines.append("- Id: {0}".format(item.get("id", "")))
        lines.append("- Status: {0}".format(item.get("status", "")))
        lines.append("- Stage: {0}".format(item.get("campaign_stage", "")))
        lines.append("- Purpose: {0}".format(item.get("purpose", "")))
        if item.get("events"):
            rendered = ", ".join(
                "{0} ({1})".format(ref.get("id"), ref.get("stage")) for ref in item["events"]
            )
            lines.append("- Events: {0}".format(rendered))
        thread = item.get("thread") or []
        if thread:
            lines.append("- Thread:")
            for index, post in enumerate(thread, start=1):
                lines.append("  {0}. {1}".format(index, post))
        elif item.get("text"):
            lines.append("")
            lines.append(item["text"])
        else:
            lines.append("")
            lines.append("_Empty slot._")
        if item.get("visual_brief"):
            lines.append("")
            lines.append("Visual: {0}".format(item["visual_brief"]))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def locked_update(path, mutator):
    path = Path(path)
    ensure_private_dir(path.parent)
    lock_path = path.with_suffix(".lock")
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        os.chmod(lock_path, 0o600)
        current = load_queue(path) if path.exists() else None
        updated = mutator(current)
        updated["publish"] = False
        write_json(path, updated)
        write_text(path.parent / "calendar.md", render_calendar(updated))
        return updated


def iter_urls(text):
    cursor = 0
    for match in URL_RE.finditer(text):
        raw = match.group(0)
        trimmed = raw.rstrip(TRAILING_URL_PUNCT)
        if not trimmed:
            continue
        start = match.start()
        if start < cursor:
            continue
        end = start + len(trimmed)
        yield start, end
        cursor = end


def codepoint_weight(text):
    weight = 0
    for char in text:
        if char in ("\u200d", "\ufe0e", "\ufe0f"):
            continue
        if unicodedata.east_asian_width(char) in ("W", "F"):
            weight += 2
            continue
        code = ord(char)
        category = unicodedata.category(char)
        if code >= 0x1F000 or 0x2600 <= code <= 0x27BF or (category == "So" and code >= 0x2190):
            weight += 2
            continue
        weight += 1
    return weight


def x_weighted_length(text):
    total = 0
    cursor = 0
    for start, end in iter_urls(text or ""):
        total += codepoint_weight(text[cursor:start])
        total += X_URL_WEIGHT
        cursor = end
    total += codepoint_weight((text or "")[cursor:])
    return total


def extract_hashtags(text):
    return ["#" + match.group(1) for match in HASHTAG_RE.finditer(text or "")]


def normalize_hashtag(tag):
    tag = str(tag).strip()
    if not tag:
        return ""
    if not tag.startswith("#"):
        tag = "#" + tag
    if HASHTAG_FULL_RE.fullmatch(tag) is None:
        raise ValueError("Invalid hashtag: {0}".format(tag))
    return tag


def render_posts(item):
    thread = item.get("thread") or []
    if not isinstance(thread, list):
        raise ValueError("thread must be a list of strings")
    warnings = []
    if thread and any(not str(part).strip() for part in thread):
        raise ValueError("thread posts must not be blank")
    posts = [str(part) for part in thread]
    if posts and str(item.get("text") or "").strip():
        warnings.append("thread is set, so text is ignored")
    if not posts:
        text = str(item.get("text") or "")
        posts = [text] if text.strip() else []
    if not posts:
        return [], warnings
    last = posts[-1]
    link = str(item.get("link") or "").strip()
    if link and link not in last:
        last = last.rstrip() + "\n" + link
    hashtags = item.get("hashtags") or []
    if not isinstance(hashtags, list):
        raise ValueError("hashtags must be a list")
    existing = {tag.lower() for tag in extract_hashtags(last)}
    extra = []
    for tag in hashtags:
        normalized = normalize_hashtag(tag)
        if not normalized or normalized.lower() in existing:
            continue
        extra.append(normalized)
        existing.add(normalized.lower())
    if extra:
        last = last.rstrip() + "\n" + " ".join(extra)
    posts[-1] = last
    return posts, warnings


def buffer_time(value):
    match = LOCAL_TIME_RE.fullmatch((value or "").strip())
    if match is None:
        raise ValueError("scheduled_local must be YYYY-MM-DDTHH:MM, got {0!r}".format(value))
    return "{0} {1}:{2}".format(match.group(1), match.group(2), match.group(3))


def has_visual(item):
    if str(item.get("visual_brief") or "").strip():
        return True
    if str(item.get("image_url") or "").strip():
        return True
    carousel = item.get("carousel") or []
    if not isinstance(carousel, list):
        return False
    for slide in carousel:
        brief = slide if isinstance(slide, str) else (slide or {}).get("brief", "")
        if str(brief).strip():
            return True
    return False


def validate_item(item, x_premium=False):
    errors = []
    warnings = []
    platform = item.get("platform")
    item_id = item.get("id")
    if platform not in PLATFORMS:
        return {
            "id": item_id,
            "platform": platform,
            "errors": ["platform must be x, linkedin, or instagram"],
            "warnings": [],
            "lengths": [],
        }
    try:
        posts, render_warnings = render_posts(item)
    except ValueError as error:
        return {
            "id": item_id,
            "platform": platform,
            "errors": [str(error)],
            "warnings": [],
            "lengths": [],
        }
    if not posts:
        return None
    warnings.extend(render_warnings)
    if not str(item.get("basis") or "").strip():
        warnings.append("set basis to [guess], [owner], [site: /path], or [unknown]")
    if item.get("scheduled_local"):
        try:
            buffer_time(item.get("scheduled_local"))
        except ValueError as error:
            errors.append(str(error))
    else:
        errors.append("scheduled_local must be YYYY-MM-DDTHH:MM")
    lengths = []
    if platform == "x":
        limit = X_PREMIUM_LIMIT if x_premium else X_LIMIT
        if item.get("thread") and len(posts) < 2:
            warnings.append("a thread needs at least 2 posts")
        if len(posts) > THREAD_WARN:
            warnings.append("thread has {0} posts; keep threads to {1} or fewer".format(len(posts), THREAD_WARN))
        for index, post in enumerate(posts, start=1):
            length = x_weighted_length(post)
            lengths.append(length)
            if length > limit:
                errors.append("post {0} is {1} weighted characters; limit is {2}".format(index, length, limit))
            tags = extract_hashtags(post)
            if len(tags) > X_HASHTAG_WARN:
                warnings.append("post {0} has {1} hashtags; use at most {2}".format(index, len(tags), X_HASHTAG_WARN))
    elif platform == "linkedin":
        if len(posts) > 1:
            errors.append("LinkedIn items are a single post; threads are for X")
        post = posts[0]
        length = len(post)
        lengths.append(length)
        if length > LINKEDIN_LIMIT:
            errors.append("post is {0} characters; limit is {1}".format(length, LINKEDIN_LIMIT))
        elif length > LINKEDIN_RECOMMENDED:
            warnings.append("post is {0} characters; aim under {1}".format(length, LINKEDIN_RECOMMENDED))
        first = post.split("\n", 1)[0]
        if len(first) > LINKEDIN_SEE_MORE:
            warnings.append("first line is {0} characters; the point may sit behind see more".format(len(first)))
        tags = extract_hashtags(post)
        if len(tags) > LINKEDIN_HASHTAG_WARN:
            warnings.append("{0} hashtags; 3 to 5 is the usual range".format(len(tags)))
    else:
        if len(posts) > 1:
            errors.append("Instagram items are a single caption; threads are for X")
        post = posts[0]
        length = len(post)
        lengths.append(length)
        if length > INSTAGRAM_LIMIT:
            errors.append("caption is {0} characters; limit is {1}".format(length, INSTAGRAM_LIMIT))
        first = post.split("\n", 1)[0]
        if len(first) > INSTAGRAM_SEE_MORE:
            warnings.append("first line is {0} characters; the hook may sit behind more".format(len(first)))
        tags = extract_hashtags(post)
        if len(tags) > INSTAGRAM_HASHTAG_LIMIT:
            errors.append("{0} hashtags; Instagram's API limit is {1}".format(len(tags), INSTAGRAM_HASHTAG_LIMIT))
        elif len(tags) > INSTAGRAM_HASHTAG_RECOMMENDED:
            warnings.append("{0} hashtags; use {1} or fewer".format(len(tags), INSTAGRAM_HASHTAG_RECOMMENDED))
        if not has_visual(item):
            errors.append("Instagram needs a visual_brief, carousel, or image_url")
        carousel = item.get("carousel") or []
        if not isinstance(carousel, list):
            errors.append("carousel must be a list")
        elif len(carousel) > INSTAGRAM_CAROUSEL_MAX:
            errors.append("carousel has {0} slides; limit is {1}".format(len(carousel), INSTAGRAM_CAROUSEL_MAX))
        else:
            for index, slide in enumerate(carousel, start=1):
                brief = slide if isinstance(slide, str) else (slide or {}).get("brief", "")
                if not str(brief).strip():
                    errors.append("carousel slide {0} needs a brief".format(index))
        alt = str(item.get("alt_text") or "")
        if alt and len(alt) > ALT_TEXT_LIMIT:
            errors.append("alt text is {0} characters; limit is {1}".format(len(alt), ALT_TEXT_LIMIT))
        elif not alt:
            warnings.append("add alt text for the image")
        image_url = str(item.get("image_url") or "").strip()
        if image_url and not image_url.startswith("https://"):
            errors.append("image_url must be a public https URL")
        elif image_url and IMAGE_EXT_RE.search(image_url) is None:
            warnings.append("image_url should be a direct link ending in .jpg, .png, .webp, or .gif")
        if not image_url:
            warnings.append("Buffer leaves this Instagram row out until image_url is a public https link")
    return {
        "id": item_id,
        "platform": platform,
        "errors": errors,
        "warnings": warnings,
        "lengths": lengths,
    }


def validate_queue(queue, x_premium=None):
    queue = prepare_queue(queue)
    if x_premium is None:
        x_premium = bool(queue.get("x_premium"))
    results = []
    for item in queue["items"]:
        result = validate_item(item, x_premium=x_premium)
        if result is not None:
            results.append(result)
    error_count = sum(len(item["errors"]) for item in results)
    warning_count = sum(len(item["warnings"]) for item in results)
    return {
        "ok": error_count == 0,
        "publish": False,
        "error_count": error_count,
        "warning_count": warning_count,
        "x_premium": bool(x_premium),
        "items": results,
    }


def write_csv(path, rows):
    path = Path(path)
    ensure_private_dir(path.parent)
    handle_fd, name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=BUFFER_COLUMNS,
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
                extrasaction="ignore",
            )
            writer.writeheader()
            for row in rows:
                writer.writerow({column: row.get(column, "") for column in BUFFER_COLUMNS})
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(name, 0o600)
        os.replace(name, path)
        os.chmod(path, 0o600)
    except Exception:
        try:
            os.unlink(name)
        except OSError:
            pass
        raise


def local_to_utc_iso(scheduled_local, utc_offset):
    match = LOCAL_TIME_RE.fullmatch(scheduled_local.strip())
    if match is None:
        raise ValueError("scheduled_local must be YYYY-MM-DDTHH:MM, got {0!r}".format(scheduled_local))
    local = datetime.datetime(
        int(match.group(1)[0:4]),
        int(match.group(1)[5:7]),
        int(match.group(1)[8:10]),
        int(match.group(2)),
        int(match.group(3)),
    )
    aware = local.replace(tzinfo=parse_offset(utc_offset))
    utc = aware.astimezone(datetime.timezone.utc)
    return utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def postiz_settings(item):
    platform = item["platform"]
    if platform == "x":
        return {"__type": "x", "who_can_reply_post": "everyone"}
    if platform == "linkedin":
        return {"__type": "linkedin", "post_as_images_carousel": bool(item.get("carousel"))}
    if platform == "instagram":
        return {"__type": "instagram", "post_type": "post"}
    raise ValueError("Platform must be x, linkedin, or instagram")


def postiz_images(item):
    url = str(item.get("image_url") or "").strip()
    if not url:
        return []
    image = {"id": item["id"], "path": url}
    alt = str(item.get("alt_text") or "").strip()
    if alt:
        image["alt"] = alt
    return [image]


def build_postiz_body(item, integration_id, date_value):
    posts, _warnings = render_posts(item)
    if not posts:
        raise ValueError("Cannot export an empty draft")
    images = postiz_images(item)
    if item["platform"] == "x" and len(posts) > 1:
        value = [{"content": post, "image": []} for post in posts]
    else:
        value = [{"content": posts[0], "image": images}]
    body = {
        "type": "draft",
        "date": date_value,
        "shortLink": False,
        "tags": [],
        "posts": [
            {
                "integration": {"id": integration_id},
                "value": value,
                "settings": postiz_settings(item),
            }
        ],
    }
    assert_draft_payload(body)
    return body


def assert_draft_payload(payload):
    if not isinstance(payload, dict) or payload.get("type") != "draft":
        raise ValueError("Refusing to send a post that is not a draft")


def build_x_drafts(queue):
    items = []
    for item in queue["items"]:
        if item.get("platform") != "x":
            continue
        posts, _warnings = render_posts(item)
        if not posts:
            continue
        items.append({"id": item["id"], "posts": posts})
    return {
        "schema": X_DRAFTS_SCHEMA,
        "publish": False,
        "note": "Create each posts array with the X drafts connector, in order. The user publishes.",
        "items": items,
    }


def filled_items(queue):
    ready = []
    for item in queue["items"]:
        posts, _warnings = render_posts(item)
        if posts:
            ready.append(item)
    return ready


def export_queue(queue, directory, formats, day):
    report = validate_queue(queue)
    if not report["ok"]:
        raise ValidationFailed(report)
    directory = Path(directory)
    out = directory / "exports"
    included = set()
    omitted_instagram = []
    thread_first_post_only = []
    files = []
    grouped = {platform: [] for platform in PLATFORMS}
    grouped_ids = {platform: [] for platform in PLATFORMS}
    postiz_items = []
    for item in filled_items(queue):
        posts, _warnings = render_posts(item)
        platform = item["platform"]
        if "buffer" in formats:
            image = str(item.get("image_url") or "").strip()
            if platform == "instagram" and not image:
                omitted_instagram.append(item["id"])
            else:
                if platform == "x" and len(posts) > 1:
                    thread_first_post_only.append(item["id"])
                grouped[platform].append(
                    {
                        "Text": posts[0],
                        "Image URL": image,
                        "Tags": "",
                        "Posting Time": buffer_time(item["scheduled_local"]),
                    }
                )
                grouped_ids[platform].append(item["id"])
                included.add(item["id"])
        if "postiz" in formats:
            postiz_items.append(
                {
                    "id": item["id"],
                    "scheduled_local": item["scheduled_local"],
                    "body": build_postiz_body(
                        item,
                        "SET_INTEGRATION_ID",
                        item["scheduled_local"],
                    ),
                }
            )
            included.add(item["id"])
        if "x-drafts" in formats and platform == "x":
            included.add(item["id"])
    if "buffer" in formats:
        for platform in PLATFORMS:
            rows = grouped[platform]
            if not rows:
                continue
            name = "{0}-buffer-{1}.csv".format(day, platform)
            path = out / name
            write_csv(path, rows)
            files.append("exports/" + name)
    if "postiz" in formats:
        name = "{0}-postiz-drafts.json".format(day)
        write_json(
            out / name,
            {
                "schema": POSTIZ_SCHEMA,
                "publish": False,
                "dates_are": "local",
                "timezone": queue.get("timezone") or "",
                "note": (
                    "Each body is a Postiz draft. date is the queue's local time, "
                    "without a UTC marker. The publish command converts it when "
                    "CONTENT_QUEUE_UTC_OFFSET is set."
                ),
                "items": postiz_items,
            },
        )
        files.append("exports/" + name)
    if "x-drafts" in formats:
        name = "{0}-x-drafts.json".format(day)
        write_json(out / name, build_x_drafts(queue))
        files.append("exports/" + name)
    for item in queue["items"]:
        if item["id"] in included and item.get("status") != "queued-draft":
            item["status"] = "exported"
    queue["publish"] = False
    queue["updated"] = day
    manifest = {
        "schema": EXPORT_SCHEMA,
        "publish": False,
        "date": day,
        "formats": list(formats),
        "files": files,
        "omitted_instagram": omitted_instagram,
        "thread_first_post_only": thread_first_post_only,
        "validation": {
            "ok": True,
            "warning_count": report["warning_count"],
        },
    }
    manifest_name = "{0}-manifest.json".format(day)
    write_json(out / manifest_name, manifest)
    manifest["files"] = files + ["exports/" + manifest_name]
    manifest["content_dir"] = "brands/{0}/content".format(queue.get("business", ""))
    return manifest


def resolve_formats(values):
    if not values:
        raise ValueError("Pass --format buffer, postiz, x-drafts, or all")
    if "all" in values:
        return list(FORMATS)
    unknown = [value for value in values if value not in FORMATS]
    if unknown:
        raise ValueError("Unknown format: {0}".format(", ".join(unknown)))
    return [name for name in FORMATS if name in values]


def postiz_ref(body):
    if isinstance(body, list) and body:
        first = body[0]
        if isinstance(first, dict):
            return str(first.get("postId") or first.get("id") or "")
    if isinstance(body, dict):
        return str(body.get("postId") or body.get("id") or "")
    return ""


def post_json(url, payload, api_key, opener):
    assert_draft_payload(payload)
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", api_key)
    request.add_header("User-Agent", "marketing-minder-content-queue")
    try:
        with opener(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        detail = ""
        if error.fp is not None:
            detail = error.read().decode("utf-8", "replace")[:500]
        raise ValueError("Postiz returned HTTP {0}: {1}".format(error.code, detail)) from None
    except urllib.error.URLError as error:
        raise ValueError("Postiz request failed: {0}".format(error.reason)) from None
    if not raw:
        return {}
    return json.loads(raw)


def publishable_items(queue):
    ready = []
    for item in filled_items(queue):
        if item.get("status") == "queued-draft":
            continue
        ready.append(item)
    return ready


def queue_postiz_drafts(
    queue,
    *,
    approve,
    allow_publish,
    api_key,
    api_base,
    integration_ids,
    utc_offset,
    dry_run,
    opener,
    save,
):
    report = validate_queue(queue)
    if not report["ok"]:
        raise ValidationFailed(report)
    if not utc_offset:
        raise ValueError(
            "Set --utc-offset or CONTENT_QUEUE_UTC_OFFSET, for example -08:00, "
            "so draft times convert to UTC"
        )
    ready = publishable_items(queue)
    if not ready:
        raise ValueError("No drafts to queue")
    if len(ready) > POSTIZ_HOURLY_LIMIT:
        raise ValueError(
            "Postiz allows {0} requests an hour; this batch has {1}. Split it.".format(
                POSTIZ_HOURLY_LIMIT, len(ready)
            )
        )
    missing = []
    for item in ready:
        env_name = INTEGRATION_ENV[item["platform"]]
        if not integration_ids.get(item["platform"]):
            missing.append(env_name)
    if missing:
        raise ValueError("Missing integration id: {0}".format(", ".join(sorted(set(missing)))))
    payloads = []
    for item in ready:
        payloads.append(
            build_postiz_body(
                item,
                integration_ids[item["platform"]],
                local_to_utc_iso(item["scheduled_local"], utc_offset),
            )
        )
    if dry_run:
        if save is not None:
            pass
        return {"dry_run": True, "publish": False, "mode": "draft", "requests": payloads}
    if not approve or allow_publish != "1":
        raise ValueError(
            "Refusing to contact Postiz. Pass --approve-publish and set "
            "CONTENT_QUEUE_ALLOW_PUBLISH=1. This command creates drafts only."
        )
    if not api_key:
        raise ValueError("POSTIZ_API_KEY is not set")
    url = api_base.rstrip("/") + "/posts"
    sent = []
    try:
        for item, payload in zip(ready, payloads):
            assert_draft_payload(payload)
            body = post_json(url, payload, api_key, opener)
            item["status"] = "queued-draft"
            item["postiz_draft_id"] = postiz_ref(body)
            sent.append({"id": item["id"], "post_id": item["postiz_draft_id"]})
    finally:
        if sent and save is not None:
            queue["publish"] = False
            queue["updated"] = current_date().isoformat()
            save(queue)
    return {"ok": True, "publish": False, "mode": "draft", "queued": sent}


def require_timezone(value):
    value = (value or "UTC").strip()
    if not value:
        raise ValueError("Timezone must be a label such as America/Los_Angeles or UTC")
    return value


def brand_path_for(root, slug, override):
    if override:
        return Path(override)
    return Path(root) / "brands" / slug / "brand.md"


def load_event_file(path, root):
    path = Path(path)
    if path.name == "launch-plan.md":
        event_id = "launch-plan"
        filename_date = ""
    else:
        event_id = path.stem
        match = re.match(r"(\d{4}-\d{2}-\d{2})-", path.name)
        filename_date = match.group(1) if match else ""
    event = parse_event_document(read_text(path), event_id, filename_date)
    event["path"] = display_path(root, path)
    return event


def event_summary(event):
    return {
        "id": event.get("id") or "",
        "path": event.get("path") or "",
        "filename_date": event.get("filename_date") or "",
        "target_date": "" if event.get("conflicts") else (event.get("target_date") or ""),
        "timezone": event.get("timezone") or "",
        "conflicts": list(event.get("conflicts") or []),
        "date_unknown": bool(event.get("date_unknown")),
    }


def sole_launch_date(events):
    dates = []
    for event in events:
        if event.get("target_date") and not event.get("conflicts"):
            dates.append(event["target_date"])
    if len(set(dates)) == 1 and len(dates) == len([event for event in events if event.get("target_date")]):
        return dates[0]
    if len(dates) == 1:
        return dates[0]
    return ""


def select_events(root, slug, event_paths, launch_plan_path):
    """Prefer brands/<slug>/events/<YYYY-MM-DD>-<slug>.md.

    A legacy launch-plan.md is used only when no event file represents it.
    Passing --event or --launch-plan selects those files and skips discovery.
    """
    root = Path(root)
    if event_paths or launch_plan_path:
        chosen = [load_event_file(path, root) for path in (event_paths or [])]
        if launch_plan_path:
            chosen.append(load_event_file(launch_plan_path, root))
        return chosen, ""
    events_dir = root / "brands" / slug / "events"
    chosen = []
    skipped = []
    if events_dir.is_dir():
        for path in sorted(events_dir.glob("*.md")):
            if EVENT_NAME_RE.fullmatch(path.name):
                chosen.append(load_event_file(path, root))
            else:
                skipped.append(path.name)
    legacy = root / "brands" / slug / "launch-plan.md"
    warning = ""
    if skipped:
        warning = "ignored event filenames: {0}".format(", ".join(skipped))
    if legacy.is_file():
        if not chosen:
            chosen.append(load_event_file(legacy, root))
        elif not any(event.get("legacy_link") for event in chosen):
            legacy_note = (
                "legacy launch-plan.md was left unused because events/ has files "
                "that do not identify it; confirm which event it is before scheduling it"
            )
            warning = "{0} {1}".format(warning, legacy_note).strip() if warning else legacy_note
    return chosen, warning


def load_business_queue(root, slug):
    path = content_dir(root, slug) / "queue.json"
    if not path.exists():
        raise ValueError("No queue yet. Run calendar first.")
    queue = load_queue(path)
    if queue.get("business") not in (None, slug):
        raise ValueError("Queue belongs to a different business")
    return path, queue


def add_common(parser):
    parser.add_argument("--business", required=True, help="Lowercase domain slug, such as example")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root")


def cmd_brand(args):
    slug = require_slug(args.business)
    path = brand_path_for(args.root, slug, args.brand)
    print(json.dumps(parse_brand(read_text(path)), indent=2, ensure_ascii=False))
    return 0


def cmd_calendar(args):
    slug = require_slug(args.business)
    week = parse_date(args.week)
    if week.weekday() != 0:
        raise ValueError("{0} is not a Monday".format(week.isoformat()))
    timezone = require_timezone(args.timezone)
    root = Path(args.root).resolve()
    ensure_brands_gitignored(root)
    directory = content_dir(root, slug)
    brand = parse_brand(read_text(brand_path_for(root, slug, args.brand)))
    events, legacy_warning = select_events(root, slug, args.event, args.launch_plan)
    incoming = build_week_items(week, brand, events)
    sources = [display_path(root, brand_path_for(root, slug, args.brand))]
    sources.extend(event["path"] for event in events if event.get("path"))

    def mutate(current):
        queue = current or empty_queue(slug, timezone, week)
        if queue.get("business") not in (None, slug):
            raise ValueError("Queue belongs to a different business")
        queue["schema"] = SCHEMA
        queue["business"] = slug
        queue["timezone"] = timezone
        queue["week"] = week.isoformat()
        queue["events"] = [event_summary(event) for event in events]
        queue["launch_date"] = sole_launch_date(events)
        queue["legacy_warning"] = legacy_warning
        queue["sources"] = sources
        queue["updated"] = current_date().isoformat()
        if args.x_premium:
            queue["x_premium"] = True
        elif args.no_x_premium:
            queue["x_premium"] = False
        else:
            queue["x_premium"] = bool(queue.get("x_premium"))
        queue["items"] = merge_items(queue.get("items") or [], incoming)
        queue["publish"] = False
        return queue

    queue = locked_update(directory / "queue.json", mutate)
    print(json.dumps(queue_summary(queue, "calendar"), indent=2))
    return 0


def add_idea(queue, day, platform, force=False):
    prefix = "{0}-{1}-".format(day.isoformat(), platform)
    existing = [item for item in queue["items"] if str(item.get("id", "")).startswith(prefix)]
    idea_id = prefix + "idea"
    for item in existing:
        if item["id"] == idea_id:
            return False, item["id"], "an {0} item already exists for this date".format(platform)
    if existing and not force:
        return False, existing[0]["id"], "an {0} item already exists for this date".format(platform)
    item = build_idea_item(day, platform, queue.get("events") or [])
    queue["items"].append(item)
    return True, item["id"], ""


def cmd_idea(args):
    slug = require_slug(args.business)
    root = Path(args.root).resolve()
    ensure_brands_gitignored(root)
    platform = args.platform
    if platform not in PLATFORMS:
        raise ValueError("Platform must be x, linkedin, or instagram")
    day = parse_date(args.date)
    directory = content_dir(root, slug)
    path = directory / "queue.json"

    def mutate(current):
        timezone = require_timezone(args.timezone or (current or {}).get("timezone") or "UTC")
        queue = current or empty_queue(slug, timezone, monday_on_or_before(day))
        if queue.get("business") not in (None, slug):
            raise ValueError("Queue belongs to a different business")
        queue["schema"] = SCHEMA
        queue["business"] = slug
        queue["timezone"] = timezone
        queue["week"] = queue.get("week") or monday_on_or_before(day).isoformat()
        queue["publish"] = False
        created, item_id, reason = add_idea(queue, day, platform, force=args.force)
        queue["updated"] = current_date().isoformat()
        queue["_idea_result"] = {"created": created, "id": item_id, "reason": reason}
        return queue

    queue = locked_update(path, mutate)
    result = queue.pop("_idea_result")
    write_json(path, queue)
    write_text(path.parent / "calendar.md", render_calendar(queue))
    result.update(queue_summary(queue, "idea"))
    print(json.dumps(result, indent=2))
    return 0


def apply_drafts(queue, drafts):
    incoming = drafts["items"] if isinstance(drafts, dict) else drafts
    if not isinstance(incoming, list):
        raise ValueError("Drafts must be a list or an object with items")
    by_id = {item["id"]: item for item in queue["items"]}
    unknown = []
    for draft in incoming:
        if not isinstance(draft, dict) or not draft.get("id"):
            raise ValueError("Each draft needs an id")
        target = by_id.get(draft["id"])
        if target is None:
            unknown.append(draft["id"])
            continue
        changed = False
        for field in CONTENT_FIELDS:
            if field in draft and draft[field] != target.get(field):
                target[field] = draft[field]
                changed = True
        normalize_item(target)
        has_body = str(target.get("text") or "").strip() or any(
            str(part).strip() for part in (target.get("thread") or [])
        )
        if changed and target.get("status") in ("exported", "queued-draft"):
            target["status"] = "draft" if has_body else "slot"
            target.pop("postiz_draft_id", None)
        elif has_body and target.get("status") == "slot":
            target["status"] = "draft"
    if unknown:
        raise ValueError("Unknown draft id: {0}".format(", ".join(unknown)))
    queue["publish"] = False
    queue["updated"] = current_date().isoformat()
    return queue


def cmd_apply(args):
    slug = require_slug(args.business)
    root = Path(args.root).resolve()
    ensure_brands_gitignored(root)
    drafts = json.loads(read_text(args.drafts))
    path = content_dir(root, slug) / "queue.json"

    def mutate(current):
        if current is None:
            raise ValueError("No queue yet. Run calendar first.")
        if current.get("business") not in (None, slug):
            raise ValueError("Queue belongs to a different business")
        return apply_drafts(current, drafts)

    queue = locked_update(path, mutate)
    print(json.dumps(queue_summary(queue, "apply"), indent=2))
    return 0


def cmd_validate(args):
    slug = require_slug(args.business)
    _path, queue = load_business_queue(args.root, slug)
    premium = None
    if args.x_premium:
        premium = True
    elif args.no_x_premium:
        premium = False
    report = validate_queue(queue, x_premium=premium)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


def cmd_export(args):
    slug = require_slug(args.business)
    root = Path(args.root).resolve()
    ensure_brands_gitignored(root)
    formats = resolve_formats(args.format)
    path = content_dir(root, slug) / "queue.json"
    held = {}

    def mutate(current):
        if current is None:
            raise ValueError("No queue yet. Run calendar first.")
        if current.get("business") not in (None, slug):
            raise ValueError("Queue belongs to a different business")
        manifest = export_queue(current, path.parent, formats, current_date().isoformat())
        held["manifest"] = manifest
        return current

    try:
        locked_update(path, mutate)
    except ValidationFailed as error:
        print(json.dumps(error.report, indent=2))
        return 1
    print(json.dumps(held["manifest"], indent=2))
    return 0


def integration_ids_from_env():
    return {platform: os.environ.get(env_name, "") for platform, env_name in INTEGRATION_ENV.items()}


def cmd_publish(args):
    if args.provider != "postiz":
        raise ValueError(
            "The publish command only creates Postiz drafts. "
            "Buffer is a CSV you upload, and X stays in the drafts connector."
        )
    slug = require_slug(args.business)
    root = Path(args.root).resolve()
    ensure_brands_gitignored(root)
    path = content_dir(root, slug) / "queue.json"
    if not path.exists():
        raise ValueError("No queue yet. Run calendar first.")
    queue = load_queue(path)
    if queue.get("business") not in (None, slug):
        raise ValueError("Queue belongs to a different business")

    def save(updated):
        write_json(path, updated)
        write_text(path.parent / "calendar.md", render_calendar(updated))

    try:
        result = queue_postiz_drafts(
            queue,
            approve=args.approve_publish,
            allow_publish=os.environ.get("CONTENT_QUEUE_ALLOW_PUBLISH", ""),
            api_key=os.environ.get("POSTIZ_API_KEY", ""),
            api_base=os.environ.get("POSTIZ_API_BASE", "https://api.postiz.com/public/v1"),
            integration_ids=integration_ids_from_env(),
            utc_offset=args.utc_offset or os.environ.get("CONTENT_QUEUE_UTC_OFFSET", ""),
            dry_run=args.dry_run,
            opener=urllib.request.urlopen,
            save=None if args.dry_run else save,
        )
    except ValidationFailed as error:
        print(json.dumps(error.report, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


def queue_summary(queue, command):
    counts = {platform: 0 for platform in PLATFORMS}
    drafts = 0
    for item in queue.get("items") or []:
        counts[item.get("platform")] = counts.get(item.get("platform"), 0) + 1
        if item.get("status") != "slot":
            drafts += 1
    return {
        "command": command,
        "business": queue.get("business"),
        "week": queue.get("week"),
        "timezone": queue.get("timezone"),
        "publish": False,
        "content_dir": "brands/{0}/content".format(queue.get("business", "")),
        "events": [event.get("id") for event in queue.get("events") or []],
        "legacy_warning": queue.get("legacy_warning") or "",
        "items": len(queue.get("items") or []),
        "drafts": drafts,
        "by_platform": counts,
    }


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    brand = commands.add_parser("brand", help="Print the parsed brand file as JSON")
    add_common(brand)
    brand.add_argument("--brand", type=Path, help="Brand file, default brands/<business>/brand.md")
    brand.set_defaults(func=cmd_brand)

    calendar = commands.add_parser("calendar", help="Add a Monday-Sunday draft calendar")
    add_common(calendar)
    calendar.add_argument("--week", required=True, help="Monday of the week, YYYY-MM-DD")
    calendar.add_argument("--timezone", default="UTC", help="Label stored on the queue")
    calendar.add_argument("--brand", type=Path)
    calendar.add_argument(
        "--event",
        action="append",
        type=Path,
        help="One event file. Repeat for concurrent events. Default: brands/<business>/events/*.md",
    )
    calendar.add_argument(
        "--launch-plan",
        type=Path,
        help="Legacy launch-plan.md. Used on its own only when no event file represents it.",
    )
    premium = calendar.add_mutually_exclusive_group()
    premium.add_argument("--x-premium", action="store_true", help="Allow 25000-character X posts")
    premium.add_argument("--no-x-premium", action="store_true")
    calendar.set_defaults(func=cmd_calendar)

    idea = commands.add_parser("idea", help="Add one daily idea slot if that day has none")
    add_common(idea)
    idea.add_argument("--date", required=True, help="YYYY-MM-DD")
    idea.add_argument("--platform", default="x")
    idea.add_argument("--timezone", default="")
    idea.add_argument("--force", action="store_true", help="Add an idea slot beside an existing one")
    idea.set_defaults(func=cmd_idea)

    apply_cmd = commands.add_parser("apply", help="Copy draft text into queue slots")
    add_common(apply_cmd)
    apply_cmd.add_argument("--drafts", type=Path, required=True)
    apply_cmd.set_defaults(func=cmd_apply)

    validate = commands.add_parser("validate", help="Check filled drafts against platform limits")
    add_common(validate)
    validate_premium = validate.add_mutually_exclusive_group()
    validate_premium.add_argument("--x-premium", action="store_true")
    validate_premium.add_argument("--no-x-premium", action="store_true")
    validate.set_defaults(func=cmd_validate)

    export = commands.add_parser("export", help="Write Buffer, Postiz, and X draft files")
    add_common(export)
    export.add_argument(
        "--format",
        action="append",
        required=True,
        help="buffer, postiz, x-drafts, or all. Repeat to choose more than one.",
    )
    export.set_defaults(func=cmd_export)

    publish = commands.add_parser("publish", help="Create Postiz drafts. Off unless you opt in.")
    add_common(publish)
    publish.add_argument("--provider", default="postiz", choices=("postiz",))
    publish.add_argument("--approve-publish", action="store_true")
    publish.add_argument("--utc-offset", default="", help="Fixed offset such as -08:00")
    publish.add_argument("--dry-run", action="store_true", help="Print draft payloads and do not call Postiz")
    publish.set_defaults(func=cmd_publish)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        code = args.func(args) or 0
    except ValidationFailed as error:
        print(json.dumps(error.report, indent=2))
        return 1
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, csv.Error) as error:
        parser.exit(1, "{0} failed: {1}\n".format(args.command, error))
    return code


if __name__ == "__main__":
    sys.exit(main())
