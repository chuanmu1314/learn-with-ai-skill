"""维护概念复习日程；日期由调用方按用户时区显式传入。"""

import argparse
import json
import math
import re
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path


def parse_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("日期必须为 YYYY-MM-DD")
    return date.fromisoformat(value)


def validate(data):
    if not isinstance(data, dict) or not isinstance(data.get("concepts"), dict):
        raise ValueError("复习档案必须含 concepts 对象")
    for concept, card in data["concepts"].items():
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", concept):
            raise ValueError("概念 ID 必须为英文 kebab-case")
        if not isinstance(card, dict) or not isinstance(card.get("label"), str) or not card["label"].strip():
            raise ValueError(f"{concept}: 缺少概念名称")
        ease = card.get("ease_factor")
        if type(ease) not in (int, float) or not math.isfinite(ease) or ease < 1.3:
            raise ValueError(f"{concept}: 无效 ease_factor")
        for key, minimum in (("repetitions", 0), ("interval_days", 1)):
            if type(card.get(key)) is not int or card[key] < minimum:
                raise ValueError(f"{concept}: 无效 {key}")
        if card["interval_days"] > 365:
            raise ValueError(f"{concept}: 间隔超过 365 天")
        last = parse_date(card.get("last_review"))
        if parse_date(card.get("next_review")) != last + timedelta(days=card["interval_days"]):
            raise ValueError(f"{concept}: 下次日期与间隔不一致")
        history = card.get("history")
        if not isinstance(history, list) or not history:
            raise ValueError(f"{concept}: 缺少历史证据")
        ids = set()
        previous = None
        for event in history:
            if not isinstance(event, dict):
                raise ValueError(f"{concept}: 无效历史事件")
            event_id = event.get("event_id")
            if not isinstance(event_id, str) or not event_id.strip() or event_id in ids:
                raise ValueError(f"{concept}: 无效或重复事件 ID")
            ids.add(event_id)
            if type(event.get("quality")) is not int or not 0 <= event["quality"] <= 5:
                raise ValueError(f"{concept}: 质量必须为 0–5")
            event_date = parse_date(event.get("date"))
            if previous is not None and event_date < previous:
                raise ValueError(f"{concept}: 历史事件日期倒序")
            previous = event_date
        if previous != last:
            raise ValueError(f"{concept}: 最近日期与历史不一致")


def load(path):
    if not path.exists():
        return {"concepts": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    validate(data)
    return data


def record(data, concept, label, quality, event_id, today):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", concept):
        raise ValueError("概念 ID 必须为英文 kebab-case")
    if not label.strip() or not event_id.strip():
        raise ValueError("概念名称与事件 ID 不能为空")
    card = data["concepts"].get(concept)
    if card:
        for event in card["history"]:
            if event["event_id"] == event_id:
                if event["date"] != today.isoformat() or event["quality"] != quality:
                    raise ValueError("同一事件 ID 对应了不同日期或质量")
                return card, False
        if today < parse_date(card["last_review"]):
            raise ValueError("新回答日期早于最近复习，原档案保持不变")
    else:
        card = {"label": label, "ease_factor": 2.5, "repetitions": 0,
                "interval_days": 1, "history": []}
        data["concepts"][concept] = card

    same_day = card.get("last_review") == today.isoformat()
    if quality < 3:
        card["repetitions"] = 0
        card["interval_days"] = 1
    elif not same_day:
        n = card["repetitions"]
        interval = 1 if n == 0 else 6 if n == 1 else round(card["interval_days"] * card["ease_factor"])
        card["interval_days"] = min(365, max(1, interval))
        card["repetitions"] += 1
    if not same_day or quality < 3:
        delta = 5 - quality
        card["ease_factor"] = round(max(1.3, card["ease_factor"] + 0.1 - delta * (0.08 + delta * 0.02)), 4)
    card["label"] = label
    card["last_review"] = today.isoformat()
    card["next_review"] = (today + timedelta(days=card["interval_days"])).isoformat()
    card["history"].append({"event_id": event_id, "date": today.isoformat(), "quality": quality})
    validate(data)
    return card, True


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("due", "record"):
        sub = subcommands.add_parser(name)
        sub.add_argument("--file", type=Path, required=True)
        sub.add_argument("--date", required=True)
        if name == "record":
            sub.add_argument("--concept", required=True)
            sub.add_argument("--label", required=True)
            sub.add_argument("--quality", type=int, choices=range(6), required=True)
            sub.add_argument("--event", required=True)
    args = parser.parse_args()
    try:
        if not args.file.is_absolute():
            raise ValueError("--file 必须为绝对路径")
        today = parse_date(args.date)
        data = load(args.file)
        if args.command == "due":
            result = [{"concept": key, "label": card["label"], "next_review": card["next_review"]}
                      for key, card in data["concepts"].items() if parse_date(card["next_review"]) <= today]
            result.sort(key=lambda item: (item["next_review"], item["concept"]))
        else:
            card, applied = record(data, args.concept, args.label, args.quality, args.event, today)
            if applied:
                save(args.file, data)
            result = {"concept": args.concept, "applied": applied,
                      **{key: value for key, value in card.items() if key != "history"}}
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    except (ValueError, OSError, TypeError) as error:
        print(f"复习档案错误：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
