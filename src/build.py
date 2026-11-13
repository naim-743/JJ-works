#!/usr/bin/env python3
"""Builds the JJ Works static site (English + Bangla) into the repository root.

Usage:  python3 src/build.py
Edit content in src/data.py; edit look in assets/css/site.css.
"""
import os, sys, json, html
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from data import *  # noqa

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LANGS = ("en", "bn")
E = html.escape
BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

UI = {
    "nav_projects": ("Projects", "প্রকল্প"),
    "nav_services": ("Services", "সেবা"),
    "nav_process": ("Process", "কাজের ধাপ"),
    "nav_contact": ("Contact", "যোগাযোগ"),
    "menu": ("Menu", "মেনু"),
    "close": ("Close", "বন্ধ"),
    "other_lang": ("বাংলা", "English"),
    "other_lang_label": ("Read this page in Bangla", "Read this page in English"),
    "whatsapp": ("WhatsApp", "হোয়াটসঅ্যাপ"),
    "whatsapp_us": ("Message us on WhatsApp", "হোয়াটসঅ্যাপে মেসেজ দিন"),
    "see_projects": ("See our projects", "আমাদের প্রকল্প দেখুন"),
    "h1": ("One team designs it, engineers it and builds it.",
           "একই দল নকশা করে, কাঠামো ঠিক করে, নির্মাণ করে।"),
    "hero_p": ("JJ Works is a design and construction consultancy in Dhaka. We handle architectural, structural, interior and exterior work for homes and commercial buildings, from the first drawing to handover.",
               "জেজে ওয়ার্কস ঢাকার একটি ডিজাইন ও নির্মাণ পরামর্শক প্রতিষ্ঠান। বাড়ি ও বাণিজ্যিক ভবনের স্থাপত্য, কাঠামো, ইন্টেরিয়র ও এক্সটেরিয়রের কাজ আমরা প্রথম নকশা থেকে হস্তান্তর পর্যন্ত করি।"),
    "tb_title": ("JJ Works, design house", "জেজে ওয়ার্কস, ডিজাইন হাউস"),
    "tb_projects": ("Completed projects", "সম্পন্ন প্রকল্প"),
    "tb_areas": ("Working in", "কাজের এলাকা"),
    "tb_areas_v": ("Dhaka and Tangail", "ঢাকা ও টাঙ্গাইল"),
    "tb_codes": ("Codes followed", "অনুসৃত কোড"),
    "tb_codes_v": ("BNBC, RAJUK DAP 2022–2035", "বিএনবিসি, রাজউক ড্যাপ ২০২২–২০৩৫"),
    "tb_call": ("Call the engineer", "প্রকৌশলীকে ফোন করুন"),
    "story_h": ("Engineering first, so the design holds up.", "আগে প্রকৌশল, তাই নকশা টেকে।"),
    "story_p1": ("JJ Works brings interior, exterior, construction and consultancy services under one roof. Clients come to us with a plot or an idea and leave with a finished building.",
                 "জেজে ওয়ার্কস ইন্টেরিয়র, এক্সটেরিয়র, নির্মাণ ও পরামর্শ সেবা এক ছাদের নিচে দেয়। ক্লায়েন্টরা একটি প্লট বা একটি ভাবনা নিয়ে আসেন, ফিরে যান সম্পূর্ণ ভবন নিয়ে।"),
    "story_p2": ("The work is led by qualified civil and structural engineers with experience in RCC design, BOQ preparation and code compliance under BNBC and RAJUK DAP 2022–2035. Every building we design is meant to be built properly, not just to look good on paper.",
                 "কাজের নেতৃত্বে আছেন অভিজ্ঞ সিভিল ও স্ট্রাকচারাল প্রকৌশলী, যাঁদের আরসিসি ডিজাইন, বিওকিউ প্রস্তুতি এবং বিএনবিসি ও রাজউক ড্যাপ ২০২২–২০৩৫ অনুযায়ী কাজের অভিজ্ঞতা রয়েছে। আমাদের প্রতিটি নকশা শুধু কাগজে সুন্দর নয়, সঠিকভাবে নির্মাণের জন্য তৈরি।"),
    "services_h": ("What we do", "আমরা যা করি"),
    "projects_h": ("Completed projects", "সম্পন্ন প্রকল্প"),
    "projects_p": ("Homes, apartment buildings and commercial blocks across Dhaka and Tangail. Open a project to see more.",
                   "ঢাকা ও টাঙ্গাইলজুড়ে বাড়ি, অ্যাপার্টমেন্ট ভবন ও বাণিজ্যিক ভবন। বিস্তারিত দেখতে যেকোনো প্রকল্পে ক্লিক করুন।"),
    "filter_label": ("Show", "দেখান"),
    "filter_all": ("All", "সব"),
    "why_h": ("Why clients choose us", "কেন ক্লায়েন্টরা আমাদের বেছে নেন"),
    "process_h": ("How a project runs", "একটি প্রকল্প যেভাবে এগোয়"),
    "contact_h": ("Tell us about your project", "আপনার প্রকল্পের কথা বলুন"),
    "contact_p": ("Send the form and we will call you back, usually within one working day. For a faster answer, message us on WhatsApp.",
                  "ফর্মটি পাঠালে সাধারণত এক কর্মদিবসের মধ্যে আমরা ফোন করব। দ্রুত উত্তরের জন্য হোয়াটসঅ্যাপে মেসেজ দিন।"),
    "f_name": ("Your name", "আপনার নাম"),
    "f_phone": ("Phone number", "ফোন নম্বর"),
    "f_email": ("Email (optional)", "ইমেইল (ঐচ্ছিক)"),
    "f_location": ("Plot or site location", "প্লট বা সাইটের ঠিকানা"),
    "f_type": ("What do you need?", "আপনার কী প্রয়োজন?"),
    "f_type_opts": (["New building: design and construction", "Design and drawings only", "Interior design", "Exterior or facade", "Structural consultancy", "Something else"],
                    ["নতুন ভবন: নকশা ও নির্মাণ", "শুধু নকশা ও ড্রয়িং", "ইন্টেরিয়র ডিজাইন", "এক্সটেরিয়র বা ফাসাড", "কাঠামোগত পরামর্শ", "অন্য কিছু"]),
    "f_message": ("Tell us a little about it", "সংক্ষেপে বিস্তারিত লিখুন"),
    "f_message_ph": ("Plot size, number of floors, timeline…", "প্লটের আকার, তলার সংখ্যা, সময়সীমা…"),
    "f_send": ("Send enquiry", "অনুসন্ধান পাঠান"),
    "f_note": ("Your details go only to JJ Works.", "আপনার তথ্য শুধু জেজে ওয়ার্কসের কাছে যাবে।"),
    "f_subject": ("New enquiry from jjworks.bd", "jjworks.bd থেকে নতুন অনুসন্ধান"),
    "c_phone": ("Phone", "ফোন"),
    "c_offices": ("Offices", "অফিস"),
    "c_email": ("Email", "ইমেইল"),
    "c_map": ("Open in Google Maps", "গুগল ম্যাপে দেখুন"),
    "footer": ("JJ Works, a design house. Dhaka, Bangladesh.", "জেজে ওয়ার্কস, একটি ডিজাইন হাউস। ঢাকা, বাংলাদেশ।"),
    # project pages
    "p_back": ("All projects", "সব প্রকল্প"),
    "p_project": ("Project", "প্রকল্প"),
    "p_location": ("Location", "ঠিকানা"),
    "p_type": ("Type", "ধরন"),
    "p_status": ("Status", "অবস্থা"),
    "p_status_v": ("Completed", "সম্পন্ন"),
    "p_by": ("Designed and built by", "নকশা ও নির্মাণ"),
    "p_sheet": ("Sheet", "শিট"),
    "p_intro": ("{name} is a {type} project completed by JJ Works{loc}. Planning something similar? Tell us about your plot and we will explain how we would approach it.",
                "{name} জেজে ওয়ার্কসের সম্পন্ন একটি {type} প্রকল্প{loc}। এমন কিছু পরিকল্পনা করছেন? আপনার প্লটের কথা জানান, আমরা কীভাবে কাজটি করব তা বুঝিয়ে বলব।"),
    "p_loc_part": (" in {loc}", ", {loc}-এ"),
    "p_ask": ("Ask about a similar project", "এমন প্রকল্প নিয়ে জানতে চাই"),
    "p_form": ("Send an enquiry", "অনুসন্ধান ফর্ম"),
    "p_prev": ("Previous project", "আগের প্রকল্প"),
    "p_next": ("Next project", "পরের প্রকল্প"),
    "p_more": ("More projects", "আরও প্রকল্প"),
    "wa_text": ("Hello JJ Works, I found you on jjworks.bd and would like to discuss a project.",
                "আসসালামু আলাইকুম, jjworks.bd থেকে আপনাদের পেয়েছি। একটি প্রকল্প নিয়ে কথা বলতে চাই।"),
    "wa_text_p": ("Hello JJ Works, I saw {name} on jjworks.bd and would like to discuss a similar project.",
                  "আসসালামু আলাইকুম, jjworks.bd-তে {name} দেখেছি। এমন একটি প্রকল্প নিয়ে কথা বলতে চাই।"),
    # thanks
    "t_h": ("Thank you. We have your enquiry.", "ধন্যবাদ। আপনার অনুসন্ধান আমরা পেয়েছি।"),
    "t_p": ("We will call you back, usually within one working day. If it is urgent, message us on WhatsApp.",
            "সাধারণত এক কর্মদিবসের মধ্যে আমরা আপনাকে ফোন করব। জরুরি হলে হোয়াটসঅ্যাপে মেসেজ দিন।"),
    "t_home": ("Back to the home page", "হোম পেজে ফিরুন"),
    # meta
    "meta_title": ("JJ Works | Building design and construction in Dhaka",
                   "জেজে ওয়ার্কস | ঢাকায় ভবন নকশা ও নির্মাণ"),
    "meta_desc": ("JJ Works is a Dhaka design and construction consultancy: architectural and structural design, interiors, facades and full construction to BNBC and RAJUK DAP 2022–2035.",
                  "জেজে ওয়ার্কস ঢাকার ডিজাইন ও নির্মাণ পরামর্শক প্রতিষ্ঠান: স্থাপত্য ও কাঠামোগত নকশা, ইন্টেরিয়র, ফাসাড এবং বিএনবিসি ও রাজউক ড্যাপ অনুযায়ী সম্পূর্ণ নির্মাণ।"),
    "p_meta_desc": ("{name}, a {type} project by JJ Works{loc}. Design and construction consultancy in Dhaka.",
                    "{name}, জেজে ওয়ার্কসের একটি {type} প্রকল্প{loc}। ঢাকার ডিজাইন ও নির্মাণ পরামর্শক প্রতিষ্ঠান।"),
    "nf_h": ("This page does not exist.", "এই পেজটি পাওয়া যায়নি।"),
    "nf_p": ("The link may be old or mistyped. Go to the home page to see our projects and contact details.",
             "লিংকটি পুরোনো বা ভুল হতে পারে। আমাদের প্রকল্প ও যোগাযোগের তথ্য দেখতে হোম পেজে যান।"),
}


def t(key, lang):
    v = UI[key]
    return v[0] if lang == "en" else v[1]


def pick(pair, lang):
    return pair[0] if lang == "en" else pair[1]


def num(n, lang):
    s = str(n)
    return s if lang == "en" else s.translate(BN_DIGITS)


def lang_root(lang):
    return "" if lang == "en" else "bn/"


def page_url(lang, path):
    """Public URL of a page. path like '' or 'projects/x/'."""
    return f"{SITE_URL}/{lang_root(lang)}{path}"


def wa_link(text):
    return f"https://wa.me/{WHATSAPP}?text={quote(text)}"


def tel(p):
    return "tel:+88" + p.replace("-", "").replace(" ", "")


BADGE = open(os.path.join(ROOT, "images/brand/jjworks-badge.svg"), encoding="utf-8").read().replace(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">',
    '<svg class="brand-badge" viewBox="0 0 100 100" aria-hidden="true" focusable="false">')

ICON_WA = '<svg viewBox="0 0 24 24" aria-hidden="true" class="ico"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .1-1.3c0-.1-.2-.2-.4-.3Z"/></svg>'


def head(lang, depth, title, desc, path, og_image="images/og.jpg", jsonld=None):
    up = "../" * depth
    other = "bn" if lang == "en" else "en"
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{page_url(lang, path)}">
<link rel="alternate" hreflang="en" href="{page_url('en', path)}">
<link rel="alternate" hreflang="bn" href="{page_url('bn', path)}">
<link rel="alternate" hreflang="x-default" href="{page_url('en', path)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="JJ Works">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{page_url(lang, path)}">
<meta property="og:image" content="{SITE_URL}/{og_image}">
<meta property="og:locale" content="{'en_US' if lang == 'en' else 'bn_BD'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#15202B">
<link rel="icon" href="{up}favicon.ico" sizes="48x48">
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{up}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anek+Bangla:wdth,wght@75..100,500..700&family=Hind+Siliguri:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{up}assets/css/site.css">
{ld}
</head>
<body class="lang-{lang}">
<a class="skip" href="#main">{'Skip to content' if lang == 'en' else 'মূল অংশে যান'}</a>
"""


def header(lang, depth, path):
    up = "../" * depth
    home = up + lang_root(lang)
    # link to the same page in the other language
    if lang == "en":
        other_href = up + "bn/" + path
    else:
        other_href = up + path if depth else "../" + path
    other_href = other_href or "./"
    other = "bn" if lang == "en" else "en"
    return f"""<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="{home}" aria-label="JJ Works home">{BADGE}<span>JJ Works</span></a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">{t('menu', lang)}</button>
    <nav id="site-nav" class="site-nav" aria-label="{'Main' if lang == 'en' else 'প্রধান'}">
      <a href="{home}#projects">{t('nav_projects', lang)}</a>
      <a href="{home}#services">{t('nav_services', lang)}</a>
      <a href="{home}#process">{t('nav_process', lang)}</a>
      <a href="{home}#contact">{t('nav_contact', lang)}</a>
      <a class="lang-switch" href="{other_href}" hreflang="{other}" lang="{other}" title="{t('other_lang_label', lang)}">{t('other_lang', lang)}</a>
    </nav>
  </div>
</header>
<main id="main">
"""


def footer(lang, depth, wa_text=None):
    up = "../" * depth
    year = num(2026, lang)
    return f"""</main>
<footer class="site-footer">
  <div class="wrap foot">
    <p>© {year} {t('footer', lang)}</p>
    <p><a href="{tel(PEOPLE[0]['phones'][0])}">{num(PEOPLE[0]['phones'][0], lang)}</a> <span aria-hidden="true">/</span> <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  </div>
</footer>
<a class="wa-float" href="{wa_link(wa_text or t('wa_text', lang))}" target="_blank" rel="noopener" aria-label="{t('whatsapp_us', lang)}">{ICON_WA}<span>{t('whatsapp', lang)}</span></a>
<script src="{up}assets/js/site.js" defer></script>
</body>
</html>
"""


def img_tag(slug, alt, up, focus=None, eager=False, sizes="(max-width: 700px) 50vw, 25vw"):
    style = f' style="object-position:{focus}"' if focus else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture><source type="image/webp" srcset="{up}images/projects/{slug}.webp">'
            f'<img src="{up}images/projects/{slug}.jpg" alt="{E(alt)}" width="640" height="780" {load} decoding="async"{style}></picture>')


def alt_for(p, lang):
    slug, name, loc, typ, _ = p
    n = pick(name, lang)
    ty = pick(TYPES[typ], lang)
    if lang == "en":
        return f"Exterior of {n}, a {ty.lower()} building by JJ Works" + (f" in {loc[0]}" if loc else "")
    return f"{n}-এর বাইরের দৃশ্য, জেজে ওয়ার্কসের {ty} ভবন" + (f", {loc[1]}" if loc else "")


def org_jsonld(lang):
    return {
        "@context": "https://schema.org",
        "@type": "GeneralContractor",
        "name": "JJ Works",
        "url": page_url(lang, ""),
        "image": f"{SITE_URL}/images/og.jpg",
        "logo": f"{SITE_URL}/images/brand/jjworks-badge-1024.png",
        "email": EMAIL,
        "telephone": "+88" + PEOPLE[0]["phones"][0].replace("-", ""),
        "founder": {"@type": "Person", "name": "Engr. Md. Abu Naim Mia", "jobTitle": "Managing Partner"},
        "areaServed": ["Dhaka", "Tangail"],
        "address": [
            {"@type": "PostalAddress", "streetAddress": "House 105, Park Road, Mohakhali DOHS", "addressLocality": "Dhaka", "addressCountry": "BD"},
            {"@type": "PostalAddress", "streetAddress": "308 Mujahidnagar, Rayerbag Road", "addressLocality": "Dhaka", "addressCountry": "BD"},
        ],
        "knowsAbout": [s[0][0] for s in SERVICES],
    }


def contact_section(lang, up):
    opts = "".join(f"<option>{E(o)}</option>" for o in t("f_type_opts", lang))
    phones = "".join(
        f'<li><span class="who">{E(pick(p["name"], lang))}</span>'
        + "".join(f' <a href="{tel(ph)}">{num(ph, lang)}</a>' for ph in p["phones"]) + "</li>"
        for p in PEOPLE)
    offices = "".join(
        f'<li>{E(pick(o, lang))} <a class="map" href="https://www.google.com/maps/search/?api=1&query={quote(o[0])}" target="_blank" rel="noopener">{t("c_map", lang)}</a></li>'
        for o in OFFICES)
    nxt = page_url(lang, "thanks/")
    return f"""<section class="contact" id="contact" aria-labelledby="contact-h">
  <div class="wrap contact-grid">
    <div class="contact-intro">
      <h2 id="contact-h">{t('contact_h', lang)}</h2>
      <p>{t('contact_p', lang)}</p>
      <a class="btn btn-wa" href="{wa_link(t('wa_text', lang))}" target="_blank" rel="noopener">{ICON_WA}{t('whatsapp_us', lang)}</a>
      <dl class="contact-list">
        <dt>{t('c_phone', lang)}</dt><dd><ul>{phones}</ul></dd>
        <dt>{t('c_offices', lang)}</dt><dd><ul>{offices}</ul></dd>
        <dt>{t('c_email', lang)}</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
      </dl>
    </div>
    <form class="enquiry" action="{FORM_ACTION}" method="POST">
      <input type="hidden" name="_subject" value="{E(t('f_subject', lang))}">
      <input type="hidden" name="_next" value="{nxt}">
      <input type="hidden" name="_template" value="table">
      <input type="hidden" name="language" value="{'English' if lang == 'en' else 'Bangla'}">
      <input type="hidden" name="project_seen" id="f-project" value="">
      <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <label>{t('f_name', lang)}<input name="name" required autocomplete="name"></label>
      <label>{t('f_phone', lang)}<input name="phone" type="tel" required autocomplete="tel" inputmode="tel" pattern="[0-9+ \\-]{{8,}}"></label>
      <label>{t('f_email', lang)}<input name="email" type="email" autocomplete="email"></label>
      <label>{t('f_location', lang)}<input name="location"></label>
      <label class="full">{t('f_type', lang)}<select name="need">{opts}</select></label>
      <label class="full">{t('f_message', lang)}<textarea name="message" id="f-message" rows="4" placeholder="{E(t('f_message_ph', lang))}"></textarea></label>
      <div class="full form-foot">
        <button class="btn btn-primary" type="submit">{t('f_send', lang)}</button>
        <small>{t('f_note', lang)}</small>
      </div>
    </form>
  </div>
</section>
"""


def project_card(p, lang, up, href_prefix, heading="h3"):
    slug, name, loc, typ, focus = p
    locs = f'<span class="card-loc">{E(pick(loc, lang))}</span>' if loc else ""
    return f"""<li class="card" data-type="{typ}">
  <a href="{href_prefix}projects/{slug}/">
    <div class="card-img">{img_tag(slug, alt_for(p, lang), up, focus)}</div>
    <{heading} class="card-name">{E(pick(name, lang))}</{heading}>
    <span class="card-meta">{E(pick(TYPES[typ], lang))}</span>{locs}
  </a>
</li>"""


def home(lang):
    depth = 0 if lang == "en" else 1
    up = "../" * depth
    n = len(PROJECTS)
    cards = "\n".join(project_card(p, lang, up, "") for p in PROJECTS)
    filters = f'<button type="button" class="chip" aria-pressed="true" data-filter="all">{t("filter_all", lang)} <span>{num(n, lang)}</span></button>'
    for k, v in TYPES.items():
        c = sum(1 for p in PROJECTS if p[3] == k)
        filters += f'<button type="button" class="chip" aria-pressed="false" data-filter="{k}">{E(pick(v, lang))} <span>{num(c, lang)}</span></button>'
    services = "".join(f"<li><h3>{E(pick(s[0], lang))}</h3><p>{E(pick(s[1], lang))}</p></li>" for s in SERVICES)
    reasons = "".join(f"<li><h3>{E(pick(r[0], lang))}</h3><p>{E(pick(r[1], lang))}</p></li>" for r in REASONS)
    steps = "".join(f'<li><span class="step-n">{num(i + 1, lang)}</span><h3>{E(pick(s[0], lang))}</h3><p>{E(pick(s[1], lang))}</p></li>' for i, s in enumerate(PROCESS))
    main_phone = PEOPLE[0]["phones"][0]
    out = head(lang, depth, t("meta_title", lang), t("meta_desc", lang), "", jsonld=org_jsonld(lang))
    out += header(lang, depth, "")
    out += f"""<section class="hero">
  <div class="hero-text">
    <h1>{t('h1', lang)}</h1>
    <p>{t('hero_p', lang)}</p>
    <div class="hero-actions">
      <a class="btn btn-wa" href="{wa_link(t('wa_text', lang))}" target="_blank" rel="noopener">{ICON_WA}{t('whatsapp_us', lang)}</a>
      <a class="btn btn-ghost" href="#projects">{t('see_projects', lang)}</a>
    </div>
  </div>
  <div class="hero-visual">
    <picture><source type="image/webp" srcset="{up}images/building-exterior.webp"><img src="{up}images/building-exterior.jpg" alt="{'A residential building by JJ Works' if lang == 'en' else 'জেজে ওয়ার্কসের একটি আবাসিক ভবন'}" width="920" height="1080" fetchpriority="high"></picture>
  </div>
</section>

<section class="story" aria-labelledby="story-h">
  <div class="wrap story-grid">
    <h2 id="story-h">{t('story_h', lang)}</h2>
    <div class="story-body">
      <p>{t('story_p1', lang)}</p>
      <p>{t('story_p2', lang)}</p>
    </div>
    <figure class="story-img"><picture><source type="image/webp" srcset="{up}images/building-entrance.webp"><img src="{up}images/building-entrance.jpg" alt="{'Entrance of a JJ Works building' if lang == 'en' else 'জেজে ওয়ার্কসের একটি ভবনের প্রবেশপথ'}" width="1400" height="788" loading="lazy" decoding="async"></picture></figure>
  </div>
</section>

<section class="projects" id="projects" aria-labelledby="projects-h">
  <div class="wrap">
    <div class="sec-head">
      <h2 id="projects-h">{t('projects_h', lang)}</h2>
      <p>{t('projects_p', lang)}</p>
    </div>
    <div class="filters" role="group" aria-label="{t('filter_label', lang)}">{filters}</div>
    <ul class="cards" id="project-list">
{cards}
    </ul>
  </div>
</section>

<section class="services" id="services" aria-labelledby="services-h">
  <div class="wrap">
    <h2 id="services-h">{t('services_h', lang)}</h2>
    <ul class="service-list">{services}</ul>
  </div>
</section>

<section class="why" aria-labelledby="why-h">
  <div class="wrap why-grid">
    <h2 id="why-h">{t('why_h', lang)}</h2>
    <ul class="reason-list">{reasons}</ul>
  </div>
</section>

<section class="process" id="process" aria-labelledby="process-h">
  <div class="wrap">
    <h2 id="process-h">{t('process_h', lang)}</h2>
    <ol class="steps">{steps}</ol>
  </div>
</section>
"""
    out += contact_section(lang, up)
    out += footer(lang, depth)
    write(lang_root(lang) + "index.html", out)


def project_page(i, lang):
    p = PROJECTS[i]
    slug, name, loc, typ, focus = p
    path = f"projects/{slug}/"
    depth = 2 if lang == "en" else 3
    up = "../" * depth
    home_href = up + lang_root(lang)
    n = pick(name, lang)
    ty = pick(TYPES[typ], lang)
    loc_s = pick(loc, lang) if loc else ""
    loc_part = t("p_loc_part", lang).format(loc=loc_s) if loc else ""
    ty_in = ty.lower() if lang == "en" else ty
    intro = t("p_intro", lang).format(name=n, type=ty_in, loc=loc_part)
    desc = t("p_meta_desc", lang).format(name=n, type=ty_in, loc=loc_part)
    title = f"{n} | JJ Works"
    prev_p = PROJECTS[i - 1]
    next_p = PROJECTS[(i + 1) % len(PROJECTS)]
    related = [q for q in PROJECTS if q[3] == typ and q[0] != slug][:3]
    if len(related) < 3:
        related += [q for q in PROJECTS if q[0] != slug and q not in related][: 3 - len(related)]
    rel_cards = "\n".join(project_card(q, lang, up, home_href, "h3") for q in related)
    wa_t = t("wa_text_p", lang).format(name=n)
    sheet = f"{num(i + 1, lang)} / {num(len(PROJECTS), lang)}"
    rows = f'<tr><th scope="row">{t("p_project", lang)}</th><td>{E(n)}</td></tr>'
    if loc:
        rows += f'<tr><th scope="row">{t("p_location", lang)}</th><td>{E(loc_s)}</td></tr>'
    rows += f'<tr><th scope="row">{t("p_type", lang)}</th><td>{E(ty)}</td></tr>'
    rows += f'<tr><th scope="row">{t("p_status", lang)}</th><td>{t("p_status_v", lang)}</td></tr>'
    rows += f'<tr><th scope="row">{t("p_by", lang)}</th><td>JJ Works</td></tr>'
    rows += f'<tr><th scope="row">{t("p_sheet", lang)}</th><td>{sheet}</td></tr>'
    ld = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": n,
        "about": ty,
        "image": f"{SITE_URL}/images/projects/{slug}.jpg",
        "url": page_url(lang, path),
        "creator": {"@type": "Organization", "name": "JJ Works", "url": SITE_URL},
        **({"locationCreated": {"@type": "Place", "name": loc_s}} if loc else {}),
    }
    out = head(lang, depth, title, desc, path, og_image=f"images/projects/{slug}.jpg", jsonld=ld)
    out += header(lang, depth, path)
    out += f"""<article class="project">
  <div class="wrap">
    <nav class="crumbs" aria-label="{'Breadcrumb' if lang == 'en' else 'অবস্থান'}"><a href="{home_href}#projects">{t('p_back', lang)}</a></nav>
    <div class="project-grid">
      <figure class="project-img">{img_tag(slug, alt_for(p, lang), up, focus, eager=True)}</figure>
      <div class="project-info">
        <h1>{E(n)}</h1>
        <p class="lede">{E(intro)}</p>
        <table class="titleblock titleblock-sheet">
          <tbody>{rows}</tbody>
        </table>
        <div class="hero-actions">
          <a class="btn btn-wa" href="{wa_link(wa_t)}" target="_blank" rel="noopener">{ICON_WA}{t('p_ask', lang)}</a>
          <a class="btn btn-ghost" href="{home_href}?project={quote(n)}#contact">{t('p_form', lang)}</a>
        </div>
      </div>
    </div>
    <nav class="pager" aria-label="{t('p_more', lang)}">
      <a rel="prev" href="../{prev_p[0]}/"><small>{t('p_prev', lang)}</small>{E(pick(prev_p[1], lang))}</a>
      <a rel="next" href="../{next_p[0]}/"><small>{t('p_next', lang)}</small>{E(pick(next_p[1], lang))}</a>
    </nav>
  </div>
</article>
<section class="projects related" aria-labelledby="more-h">
  <div class="wrap">
    <h2 id="more-h">{t('p_more', lang)}</h2>
    <ul class="cards cards-3">
{rel_cards}
    </ul>
  </div>
</section>
"""
    out += footer(lang, depth, wa_t)
    write(lang_root(lang) + path + "index.html", out)


def thanks(lang):
    depth = 1 if lang == "en" else 2
    up = "../" * depth
    out = head(lang, depth, f"{t('t_h', lang)} | JJ Works", t("t_p", lang), "thanks/")
    out = out.replace("<meta name=\"description\"", '<meta name="robots" content="noindex">\n<meta name="description"', 1)
    out += header(lang, depth, "thanks/")
    out += f"""<section class="message-page"><div class="wrap">
  <h1>{t('t_h', lang)}</h1>
  <p>{t('t_p', lang)}</p>
  <div class="hero-actions">
    <a class="btn btn-primary" href="{up}{lang_root(lang)}">{t('t_home', lang)}</a>
    <a class="btn btn-wa" href="{wa_link(t('wa_text', lang))}" target="_blank" rel="noopener">{ICON_WA}{t('whatsapp_us', lang)}</a>
  </div>
</div></section>
"""
    out += footer(lang, depth)
    write(lang_root(lang) + "thanks/index.html", out)


def not_found():
    # Served from any URL, so it uses absolute paths.
    out = head("en", 0, "Page not found | JJ Works", t("nf_p", "en"), "")
    out = out.replace('href="favicon', 'href="/favicon').replace('href="apple-touch', 'href="/apple-touch').replace('href="assets/', 'href="/assets/')
    out = out.replace("<meta name=\"description\"", '<meta name="robots" content="noindex">\n<meta name="description"', 1)
    out += header("en", 0, "").replace('href="#', 'href="/#').replace('href="bn/"', 'href="/bn/"').replace('href=""', 'href="/"')
    out += f"""<section class="message-page"><div class="wrap">
  <h1>{t('nf_h', 'en')}</h1>
  <p>{t('nf_p', 'en')}</p>
  <p lang="bn">{t('nf_h', 'bn')} {t('nf_p', 'bn')}</p>
  <div class="hero-actions"><a class="btn btn-primary" href="/">Go to the home page</a><a class="btn btn-ghost" href="/bn/" lang="bn">হোম পেজ</a></div>
</div></section>
"""
    out += footer("en", 0).replace('src="assets/', 'src="/assets/')
    write("404.html", out)


def sitemap():
    paths = [""] + [f"projects/{p[0]}/" for p in PROJECTS]
    items = []
    for path in paths:
        for lang in LANGS:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{page_url(l, path)}"/>' for l in LANGS)
            items.append(f"<url><loc>{page_url(lang, path)}</loc>{alts}</url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(items) + "\n</urlset>\n")
    write("sitemap.xml", xml)
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")


def write(rel, content):
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    for lang in LANGS:
        home(lang)
        thanks(lang)
        for i in range(len(PROJECTS)):
            project_page(i, lang)
    not_found()
    sitemap()
    print(f"Built {2 + 2 + 2 * len(PROJECTS) + 1} pages.")
