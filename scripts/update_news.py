#!/usr/bin/env python3
"""副業ニュースの自動更新スクリプト（標準ライブラリのみ）。

国の機関が公開している一次情報（RSS／公式の新着一覧）から、副業・働き方・お金・
詐欺対策に関係する見出しだけを集め、data/news.json と、news.html・index.html の
自動更新ブロックを書き換える。本文は転載せず、見出し・日付・出典・公式ページへの
リンクだけを載せる。

使い方:  python scripts/update_news.py
"""
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "news.json"
JST = timezone(timedelta(hours=9))
UA = ("Mozilla/5.0 (compatible; NaoFukugyouLabNewsBot/1.0; "
      "+https://nao-web-lab.github.io/nao-fukugyou-lab/)")
MAX_ITEMS = 150
MAX_AGE_DAYS = 540

# 取得元。allowed_hosts 以外へのリンクは採用しない。
SOURCES = [
    {
        "id": "kokusen", "name": "国民生活センター", "type": "kokusen_html",
        "url": "https://www.kokusen.go.jp/news/news.html",
        "hosts": ("www.kokusen.go.jp",),
        "include": r"副業|兼業|在宅|内職|フリーランス|投資|もうか|儲|稼|情報商材|ビジネス講座|副収入|"
                   r"スポットワーク|スキマ|アフィリエイト|ネットオークション|フリマ|転売|暗号資産|"
                   r"SNS|ＳＮＳ|マルチ|タスク|モニター|詐欺|悪質|ネット通販",
    },
    {
        "id": "caa", "name": "消費者庁", "type": "rss",
        "url": "https://www.caa.go.jp/news.rss",
        "hosts": ("www.caa.go.jp",),
        "include": r"副業|情報商材|詐欺|特定商取引|取引デジタルプラットフォーム|ステルスマーケティング|"
                   r"定期購入|消費者トラブル|注意喚起|マルチ|悪質|ネットオークション|フリマ|SNS|ＳＮＳ|"
                   r"投資|暗号資産|クーリング|不当表示|消費者契約法|フリーランス",
    },
    {
        "id": "fsa", "name": "金融庁", "type": "rss",
        "url": "https://www.fsa.go.jp/fsaNewsListAll_rss2.xml",
        "hosts": ("www.fsa.go.jp",),
        "include": r"NISA|ＮＩＳＡ|iDeCo|イデコ|つみたて|資産形成|資産運用|投資|暗号資産|詐欺|無登録|"
                   r"金融リテラシー|金融経済教育|SNS|ＳＮＳ|なりすまし|注意喚起",
    },
    {
        "id": "mhlw", "name": "厚生労働省", "type": "rss",
        "url": "https://www.mhlw.go.jp/stf/news.rdf",
        "hosts": ("www.mhlw.go.jp",),
        "include": r"副業|兼業|フリーランス|最低賃金|社会保険|雇用保険|労働時間|就業|テレワーク|在宅|"
                   r"年収の壁|パート|短時間労働|適用拡大|働き方|労働基準|個人事業",
    },
    {
        "id": "nta", "name": "国税庁", "type": "nta_html",
        "url": "https://www.nta.go.jp/information/news/index.htm",
        "hosts": ("www.nta.go.jp",),
        "include": r"確定申告|副業|雑所得|年末調整|インボイス|電子帳簿|フリーランス|暗号資産|"
                   r"基礎控除|チャットボット|個人事業",
    },
]

TOPICS = [
    ("caution", "注意喚起", r"詐欺|トラブル|注意|悪質|なりすまし|もうか|儲|情報商材|ビジネス講座|無登録|勧誘|マルチ"),
    ("tax", "税金", r"確定申告|所得税|雑所得|申告|年末調整|インボイス|電子帳簿|源泉|消費税|税制|税務"),
    ("money", "投資・お金", r"NISA|ＮＩＳＡ|iDeCo|イデコ|つみたて|資産形成|資産運用|投資|暗号資産|金融"),
    ("work", "働き方", r"副業|兼業|フリーランス|最低賃金|社会保険|雇用保険|労働|就業|テレワーク|在宅|年収の壁|パート"),
]
TOPIC_LABEL = {k: v for k, v, _ in TOPICS}
TOPIC_LABEL["other"] = "お知らせ"


def log(msg):
    print(msg, file=sys.stderr)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def decode(raw):
    for enc in ("utf-8", "cp932"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def clean(text):
    text = re.sub(r"<[^>]+>", "", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_date(text):
    text = (text or "").strip()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return date(int(m[1]), int(m[2]), int(m[3]))
    m = re.search(r"(\d{1,2}) (\w{3}) (\d{4})", text)
    if m:
        months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
        if m[2] in months:
            return date(int(m[3]), months.index(m[2]) + 1, int(m[1]))
    m = re.search(r"令和(\d+|元)年(\d{1,2})月(\d{1,2})日", text)
    if m:
        y = 2019 if m[1] == "元" else 2018 + int(m[1])
        return date(y, int(m[2]), int(m[3]))
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if m:
        return date(int(m[1]), int(m[2]), int(m[3]))
    return None


def safe_link(link, hosts):
    p = urlparse(link)
    return p.scheme == "https" and p.netloc in hosts


def parse_rss(src, raw):
    # 公的機関のフィードにエンティティ宣言は不要なので、あれば拒否する（XXE・展開攻撃の対策）
    if b"<!ENTITY" in raw:
        raise ValueError("feed contains entity declarations")
    root = ET.fromstring(raw)
    out = []
    for el in root.iter():
        if el.tag.split("}")[-1] != "item":
            continue
        d = {c.tag.split("}")[-1]: (c.text or "") for c in el}
        link = (d.get("link") or "").strip()
        if link.startswith("http://"):
            link = "https://" + link[len("http://"):]
        day = parse_date(d.get("date") or d.get("pubDate") or "")
        title = clean(d.get("title"))
        text = title + " " + clean(d.get("description"))
        out.append((title, link, day, text))
    return out


def parse_kokusen(src, raw):
    t = decode(raw)
    out = []
    for m in re.finditer(r'<li class="ichiran-li">\s*<a href="([^"]+)">(.*?)</a>\s*（(\d{4})年(\d{1,2})月(\d{1,2})日）', t, re.S):
        title = clean(m[2])
        link = urljoin(src["url"], m[1])
        out.append((title, link, date(int(m[3]), int(m[4]), int(m[5])), title))
    return out


def parse_nta(src, raw):
    t = decode(raw)
    out = []
    for m in re.finditer(r'<th scope="row">\s*([^<]+?)\s*</th>\s*<td>\s*<a href="([^"]+)"[^>]*>(.*?)</a>', t, re.S):
        day = parse_date(m[1])
        title = clean(m[3])
        if day:
            out.append((title, urljoin("https://www.nta.go.jp", m[2]), day, title))
    return out


PARSERS = {"rss": parse_rss, "kokusen_html": parse_kokusen, "nta_html": parse_nta}


def classify(title):
    for key, _, pat in TOPICS:
        if re.search(pat, title):
            return key
    return "other"


def collect():
    items = []
    for src in SOURCES:
        try:
            raw = fetch(src["url"])
            rows = PARSERS[src["type"]](src, raw)
        except Exception as e:  # 1つの取得元の失敗で全体を止めない
            log(f"[skip] {src['id']}: {e}")
            continue
        inc = re.compile(src["include"])
        n = 0
        for title, link, day, text in rows:
            if not title or not day or not safe_link(link, src["hosts"]):
                continue
            if not inc.search(text):
                continue
            items.append({
                "date": day.isoformat(),
                "title": title[:160],
                "url": link,
                "source": src["name"],
                "topic": classify(title),
            })
            n += 1
        log(f"[ok] {src['id']}: {len(rows)} rows, {n} matched")
    return items


def load_existing():
    if DATA.exists():
        try:
            return json.loads(DATA.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"updated": "", "items": []}


def merge(old_items, new_items):
    by_url = {i["url"]: i for i in old_items}
    for i in new_items:
        by_url[i["url"]] = i  # 最新の取得内容で上書き
    limit = (datetime.now(JST).date() - timedelta(days=MAX_AGE_DAYS)).isoformat()
    items = [i for i in by_url.values() if i["date"] >= limit]
    items.sort(key=lambda i: (i["date"], i["url"]), reverse=True)
    return items[:MAX_ITEMS]


def esc(s):
    return html.escape(s, quote=True)


def fmt(d):
    return d.replace("-", ".")


def render_list(items, limit=None):
    rows = []
    for i in (items[:limit] if limit else items):
        rows.append(
            f'        <li class="news-item" data-topic="{esc(i["topic"])}">\n'
            f'          <time datetime="{esc(i["date"])}">{fmt(i["date"])}</time>\n'
            f'          <div class="news-main">\n'
            f'            <a href="{esc(i["url"])}" target="_blank" rel="noopener">{esc(i["title"])}</a>\n'
            f'            <span class="news-meta"><span class="news-source">{esc(i["source"])}</span>'
            f'<span class="news-topic">{esc(TOPIC_LABEL.get(i["topic"], "お知らせ"))}</span></span>\n'
            f'          </div>\n'
            f'        </li>'
        )
    return "\n".join(rows)


def replace_block(path, name, content):
    p = ROOT / path
    raw = p.read_text(encoding="utf-8")
    cr, lf = chr(13), chr(10)
    crlf = (cr + lf) in raw
    s = raw.replace(cr + lf, lf)
    start, end = "<!-- %s:START -->" % name, "<!-- %s:END -->" % name
    i, j = s.find(start), s.find(end)
    if i < 0 or j < i:
        log(f"[warn] marker {name} not found in {path}")
        return False
    line_start = s.rfind(lf, 0, i) + 1
    indent = s[line_start:i]
    block = start + lf + content + lf + indent + end
    new = s[:i] + block + s[j + len(end):]
    if new == s:
        return False
    p.write_text(new.replace(lf, cr + lf) if crlf else new, encoding="utf-8", newline="")
    return True


def main():
    existing = load_existing()
    fresh = collect()
    if not fresh and not existing["items"]:
        log("取得できた項目がありません。既存データも空のため終了します。")
        return 1
    items = merge(existing["items"], fresh)
    changed = items != existing["items"]
    updated = existing.get("updated", "")
    if changed or not updated:
        updated = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    DATA.parent.mkdir(parents=True, exist_ok=True)
    payload = {"updated": updated, "items": items}
    new_text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if not DATA.exists() or DATA.read_text(encoding="utf-8") != new_text:
        DATA.write_text(new_text, encoding="utf-8", newline="\n")

    replace_block("news.html", "NEWS-LIST", render_list(items))
    replace_block("news.html", "NEWS-UPDATED", f'<span class="news-updated-at">{esc(updated)}</span>')
    replace_block("index.html", "NEWS-LATEST", render_list(items, 5))
    log(f"items={len(items)} changed={changed} updated={updated}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
