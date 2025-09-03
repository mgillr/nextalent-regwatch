#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nextalent Regulatory Radar collector
- Reads sources from regwatch.yml (official regulators + EU/US/UK institutions)
- Auto-discovers RSS/Atom feeds on landing pages
- Parses items, filters by recency, classifies by keywords
- Outputs (to ./out):
    regwatch.json                 (Lovable schema)
    regwatch-YYYY-MM-DD.json      (dated snapshot for fallback)
    widget.js                     (data + renderer; optional embed)
    index.html                    (standalone fallback page)
"""
import os, sys, json, traceback, re
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import urllib.parse as up

import requests
from bs4 import BeautifulSoup
import feedparser
import yaml

UTC = timezone.utc

# ---------- Utils ----------
def now_utc() -> datetime:
    return datetime.now(tz=UTC)

def iso_z(dt: datetime) -> str:
    # ISO8601 Zulu
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

# ---------- Config ----------
def load_config(path="regwatch.yml") -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError("regwatch.yml not found")
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg.setdefault("window_hours", 36)
    cfg.setdefault("max_items", 50)
    cfg.setdefault("sources", {})
    cfg.setdefault("keywords", {})
    return cfg

# ---------- Feed discovery ----------
def discover_feeds(url: str) -> List[str]:
    """Return list of feed URLs discovered on a landing page."""
    found = []
    try:
        r = requests.get(url, timeout=25)
        r.raise_for_status()
    except Exception:
        return found
    soup = BeautifulSoup(r.text, "html.parser")
    # <link rel="alternate" type="application/rss+xml" href="...">
    for link in soup.find_all("link", rel=lambda x: x and "alternate" in x.lower()):
        t = (link.get("type") or "").lower()
        href = (link.get("href") or "").strip()
        if "rss" in t or "atom" in t or href.endswith(".xml"):
            found.append(up.urljoin(url, href))
    # visible anchors containing rss/xml/feed
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        label = (a.get_text() or "").strip().lower()
        if "rss" in label or href.lower().endswith((".rss",".xml","/rss","/feed")):
            found.append(up.urljoin(url, href))
    # dedupe
    out, seen = [], set()
    for f in found:
        if f.startswith("http") and f not in seen:
            out.append(f); seen.add(f)
    return out

def harvest_all_sources(sources: Dict[str, List[str]]) -> Dict[str, List[str]]:
    feed_map: Dict[str, List[str]] = {}
    for section, urls in sources.items():
        feeds = []
        for u in urls:
            if u.lower().endswith((".xml",".rss","/feed")):
                feeds.append(u)
            else:
                feeds.extend(discover_feeds(u))
        # dedupe
        seen = set(); dedup = []
        for f in feeds:
            if f not in seen:
                dedup.append(f); seen.add(f)
        feed_map[section] = dedup
    return feed_map

# ---------- Feed parsing ----------
def parse_feed(url: str) -> List[dict]:
    d = feedparser.parse(url)
    out = []
    for e in d.entries:
        # pick any available timestamp
        pub = None
        for key in ("published_parsed","updated_parsed","created_parsed"):
            t = getattr(e, key, None)
            if t:
                pub = datetime(*t[:6], tzinfo=UTC); break
        title = getattr(e, "title", "").strip() or "(no title)"
        link = getattr(e, "link", url)
        # clean summary text
        summary_html = getattr(e, "summary", "") or ""
        summary = BeautifulSoup(summary_html, "html.parser").get_text(" ", strip=True)
        source_title = d.feed.get("title") or up.urlparse(url).netloc
        out.append({
            "title": title,
            "url": link,
            "summary": summary,
            "published": pub,
            "source": source_title,
            "feed": url
        })
    return out

# ---------- Classification / filtering ----------
def classify(item: dict, keywords: Dict[str, List[str]], fallback="crossIndustry") -> str:
    text = f"{item['title']} {item['summary']}".lower()
    source = item['source'].lower()
    
    # Source-based hints
    source_hints = {
        "nasa": "space",
        "esa": "space",
        "fcc": "space",
        "easa": "aviation",
        "faa": "aviation",
        "ema": "pharma",
        "fda": "pharma",
        "nhtsa": "automotive"
    }
    
    # Check for source hints
    initial_hint = None
    for src_key, section in source_hints.items():
        if src_key in source:
            initial_hint = section
            break
    
    # Improved keyword matching with word boundaries
    best_section, best_hits = initial_hint or fallback, 0
    
    for section, kws in keywords.items():
        hits = 0
        for kw in kws:
            kw_lower = kw.lower()
            # Use word boundary matching for short keywords
            if len(kw_lower) <= 3:
                pattern = r'\b' + re.escape(kw_lower) + r'\b'
                if re.search(pattern, text):
                    hits += 1
            # For longer keywords, simple containment is fine
            elif kw_lower in text:
                hits += 1
        
        if hits > best_hits:
            best_section, best_hits = section, hits
    
    # If no keywords matched but we have a source hint, use that
    if best_hits == 0 and initial_hint:
        best_section = initial_hint
    
    return best_section

def build_digest(items: List[dict], cfg: dict) -> dict:
    window = int(cfg["window_hours"])
    cutoff = now_utc() - timedelta(hours=window)
    fresh = [it for it in items if it["published"] and it["published"] >= cutoff]
    if not fresh:
        # fallback to latest N across everything
        items_sorted = sorted(items, key=lambda x: x["published"] or datetime(1970,1,1,tzinfo=UTC), reverse=True)
        fresh = items_sorted[: int(cfg["max_items"])]

    # classify
    keywords = cfg["keywords"]
    sections: Dict[str, List[dict]] = {k: [] for k in cfg["sources"].keys()}
    sections.setdefault("crossIndustry", [])
    for it in fresh:
        sec = classify(it, keywords, fallback="crossIndustry")
        sections.setdefault(sec, []).append(it)

    # sort and trim each section
    for k in list(sections.keys()):
        arr = sorted(sections[k], key=lambda x: x["published"] or datetime(1970,1,1,tzinfo=UTC), reverse=True)[:12]
        # normalize fields for output
        sections[k] = [
            {
                "title": x["title"],
                "url": x["url"],
                "source": x["source"],
                "date": (x["published"].date().isoformat() if x["published"] else ""),
                "summary": x["summary"]
            } for x in arr
        ]

    return {
        "lastUpdated": iso_z(now_utc()),
        "sections": {k: v for k, v in sections.items() if v}  # drop empty
    }

# ---------- Writers ----------
def write_json(digest: dict, out_dir="out"):
    ensure_dir(out_dir)
    path = os.path.join(out_dir, "regwatch.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=2)

def write_snapshot(digest: dict, out_dir="out"):
    ensure_dir(out_dir)
    day = datetime.now(tz=UTC).date().isoformat()
    path = os.path.join(out_dir, f"regwatch-{day}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=2)

def write_widget_js(digest: dict, out_dir="out"):
    ensure_dir(out_dir)
    data = json.dumps(digest, ensure_ascii=False)
    js = f"""(()=>{{
  const DATA = {data};
  function esc(s){{return (s||"").replace(/[&<>"]/g, c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}})[c]||c);}}
  function titleMap(k){{return ({{aviation:"Aviation",space:"Space",pharma:"Pharma & MedTech",automotive:"Automotive / EV / Clean energy",crossIndustry:"Cross‑industry"}})[k]||k;}}
  function render(id) {{
    const root = document.getElementById(id||"regwatch-root"); if(!root) return;
    const wrap = document.createElement("div"); wrap.className="regwatch";
    const h1 = document.createElement("h1"); h1.textContent="Daily Regulatory Brief"; wrap.appendChild(h1);
    const meta = document.createElement("div"); meta.style.opacity=".7"; meta.style.margin="0 0 1rem";
    meta.textContent="Updated " + new Date(DATA.lastUpdated).toUTCString(); wrap.appendChild(meta);
    const order = ["crossIndustry","automotive","pharma","aviation","space"];
    for(const k of order){{
      const arr = (DATA.sections||{{}})[k]; if(!arr||!arr.length) continue;
      const h2=document.createElement("h2"); h2.textContent=titleMap(k); wrap.appendChild(h2);
      const ul=document.createElement("ul"); ul.style.margin=".2rem 0 1rem 1.2rem";
      for(const it of arr){{
        const li=document.createElement("li"); li.style.margin=".4rem 0"; li.style.lineHeight="1.3";
        li.innerHTML = "<strong>"+esc(it.title)+"</strong> — "+esc(it.date)+" — "+esc(it.source)+"<br><a href='"+esc(it.url)+"' target='_blank' rel='noopener'>"+esc(it.url)+"</a>";
        ul.appendChild(li);
      }}
      wrap.appendChild(ul);
    }}
    root.innerHTML=""; root.appendChild(wrap);
    // JSON-LD
    try {{
      const items = Object.values(DATA.sections||{{}}).flat().map((it,i)=>({{"@type":"ListItem","position":i+1,"url":it.url,"name":it.title}}));
      const ld = {{"@context":"https://schema.org","@type":"ItemList","name":"Nextalent Daily Regulatory Brief","dateCreated":DATA.lastUpdated,"itemListElement":items}};
      const tag=document.createElement("script"); tag.type="application/ld+json"; tag.textContent=JSON.stringify(ld); document.head.appendChild(tag);
    }} catch(_e){{}}
  }}
  window.NextalentRegwatch={{data:DATA,render}};
  if(!document.currentScript || document.currentScript.dataset.autorender!=="false"){{
    if(document.readyState!=="loading") render(); else document.addEventListener("DOMContentLoaded",()=>render());
  }}
}})();"""
    with open(os.path.join(out_dir, "widget.js"), "w", encoding="utf-8") as f:
        f.write(js)

def write_fallback_html(out_dir="out"):
    ensure_dir(out_dir)
    html = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nextalent | Daily Regulatory Brief</title>
</head>
<body>
<main id="regwatch-root"></main>
<script src="widget.js" defer></script>
<noscript>Please enable JavaScript to view the daily brief.</noscript>
</body></html>"""
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ---------- Main ----------
def main():
    cfg = load_config()
    feed_map = harvest_all_sources(cfg["sources"])
    all_items = []
    for section, feeds in feed_map.items():
        for url in feeds:
            try:
                all_items.extend(parse_feed(url))
            except Exception as e:
                print(f"[warn] feed error {url}: {e}", file=sys.stderr)
    if not all_items:
        print("No items fetched.");  # still produce empty structure
    digest = build_digest(all_items, cfg)
    write_json(digest)
    write_snapshot(digest)
    write_widget_js(digest)
    write_fallback_html()
    print("Generated in ./out")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)