#!/usr/bin/env python3
"""
Generate structured data from the same CMS content that renders mattadam.art.

The legacy template contains hand-maintained JSON-LD. This script deliberately
removes every JSON-LD block from generated HTML and replaces it with structured
data derived from content.json and work.json. The template is therefore no
longer an editorial source of truth for schema copy.

Usage:
  python3 structured_data.py          rewrite generated HTML in place
  python3 structured_data.py --check validate that generated HTML matches CMS data
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(ROOT, *a)

LD_RE = re.compile(
    r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>\s*',
    re.I | re.S,
)
TAG_RE = re.compile(r'<[^>]+>')
SPACE_RE = re.compile(r'\s+')

PERSON_ID = 'https://mattadam.art/#person'
HOME_ID = 'https://mattadam.art/#website'
WORK_ID = 'https://mattadam.art/work/#page'

SAME_AS = [
    'https://www.instagram.com/mattadam___',
    'https://www.complex.com/style/a/mike-destefano/meet-emerging-photographer-whose-captured-travis-scott-juice-wrld-kanye-west-matt-adam-interview',
    'https://www.vanityfair.com/style/2020/11/matt-adam-photographer-to-the-stars-is-an-artist',
    'https://www.altpress.com/matt-adam-photo-gallery-unwrap-and-steal/',
    'https://www.imdb.com/title/tt27842581/',
]

# ── WHERE HE ACTUALLY WORKS ─────────────────────────────────────────────
#
# "Los Angeles" appeared only inside a prose sentence. That is a string an
# engine has to read and infer from. As structured properties it becomes a
# fact it can act on, which is what "artist in Los Angeles"-shaped questions
# are answered from · entity data is consulted long before body copy is.
#
# City level deliberately. There is no street address here and none should be
# added: this file is published to a public page on every build.
LOS_ANGELES = {
    '@type': 'Place',
    'name': 'Los Angeles',
    'address': {
        '@type': 'PostalAddress',
        'addressLocality': 'Los Angeles',
        'addressRegion': 'CA',
        'addressCountry': 'US',
    },
}


def occupations(roles):
    """Each role as an Occupation tied to Los Angeles.

    jobTitle already says "Photographer" and homeLocation already says
    "Los Angeles", but nothing joined the two. hasOccupation does: it states
    that the photography happens HERE, which is the exact shape of the
    question being asked. Built from the same CMS roles as jobTitle, so it
    can never claim a role the site does not.
    """
    return [
        {
            '@type': 'Occupation',
            'name': role,
            'occupationLocation': {'@type': 'City', 'name': 'Los Angeles'},
        }
        for role in roles
    ]


# Schema types are structural metadata only. Names and descriptions come from
# CMS-controlled visible content below.
HOME_WORK_TYPES = {
    'legends': 'Photograph',
    'wdty': 'CreativeWork',
    'unwrap-steal': 'CreativeWork',
    'skinny': 'VisualArtwork',
    'paintings': 'VisualArtwork',
}


def clean_text(value):
    if value is None:
        return ''
    value = str(value)
    value = re.sub(r'<br\s*/?>', ' ', value, flags=re.I)
    value = TAG_RE.sub(' ', value)
    value = html.unescape(value)
    return SPACE_RE.sub(' ', value).strip()


def load_json(name):
    with open(P(name), encoding='utf-8') as f:
        return json.load(f)


def block_by_id(blocks, block_id):
    return next((b for b in blocks if b.get('id') == block_id), None)


def block_description(block):
    if not block:
        return ''
    for item in block.get('body') or []:
        if item.get('fact'):
            return clean_text(item['fact'])
    return clean_text(block.get('aria') or block.get('label'))


def home_graph(content):
    blocks = content['blocks']
    roles = block_by_id(blocks, 'architect') or {}
    about = block_by_id(blocks, 'about') or {}
    faq = block_by_id(blocks, 'faq') or {}

    job_titles = [clean_text(x) for x in roles.get('roles', []) if clean_text(x)]

    person = {
        '@type': 'Person',
        '@id': PERSON_ID,
        'name': 'Matt Adam',
        'url': 'https://mattadam.art/',
        'image': 'https://mattadam.art/og.png',
        'jobTitle': job_titles,
        'description': clean_text(about.get('lede')),
        'homeLocation': LOS_ANGELES,
        'workLocation': LOS_ANGELES,
        'sameAs': SAME_AS,
    }
    if job_titles:
        person['hasOccupation'] = occupations(job_titles)

    works = []
    for block_id, schema_type in HOME_WORK_TYPES.items():
        block = block_by_id(blocks, block_id)
        if not block:
            continue
        works.append({
            '@type': schema_type,
            '@id': f'https://mattadam.art/#{block_id}',
            'name': clean_text(block.get('label') or block.get('aria') or block_id),
            'description': block_description(block),
            'creator': {'@id': PERSON_ID},
            'url': f'https://mattadam.art/#{block_id}',
        })

    faq_entities = []
    for item in faq.get('items', []):
        q = clean_text(item.get('q'))
        a = clean_text(item.get('a'))
        if not q or not a:
            continue
        faq_entities.append({
            '@type': 'Question',
            'name': q,
            'acceptedAnswer': {'@type': 'Answer', 'text': a},
        })

    website = {
        '@type': 'WebSite',
        '@id': HOME_ID,
        'url': 'https://mattadam.art/',
        'name': 'Matt Adam',
        'about': {'@id': PERSON_ID},
    }

    webpage = {
        '@type': 'ProfilePage',
        '@id': 'https://mattadam.art/#page',
        'url': 'https://mattadam.art/',
        'name': 'Matt Adam | Make It Undeniable',
        'mainEntity': {'@id': PERSON_ID},
        'isPartOf': {'@id': HOME_ID},
    }
    if works:
        webpage['hasPart'] = [{'@id': x['@id']} for x in works]

    graph = [person, website, webpage] + works
    if faq_entities:
        graph.append({
            '@type': 'FAQPage',
            '@id': 'https://mattadam.art/#faq',
            'mainEntity': faq_entities,
        })
    return {'@context': 'https://schema.org', '@graph': graph}


def work_graph(content):
    hero = content.get('hero') or {}
    about = content.get('about') or {}
    sections = content.get('sections') or []

    # Same @id as the homepage, so this is the same entity · it must not
    # describe him as located anywhere else, or say less about it.
    person = {
        '@type': 'Person',
        '@id': PERSON_ID,
        'name': 'Matt Adam',
        'url': 'https://mattadam.art/',
        'homeLocation': LOS_ANGELES,
        'workLocation': LOS_ANGELES,
        'sameAs': SAME_AS,
    }
    if clean_text(about.get('copy')):
        person['description'] = clean_text(about.get('copy'))

    items = []
    for pos, section in enumerate(sections, 1):
        name = clean_text(section.get('title'))
        if not name:
            continue
        item = {
            '@type': 'ListItem',
            'position': pos,
            'name': name,
            'url': f'https://mattadam.art/work/#{section.get("id", "")}',
        }
        intro = clean_text(section.get('intro'))
        if intro:
            item['description'] = intro
        items.append(item)

    work_list = {
        '@type': 'ItemList',
        '@id': 'https://mattadam.art/work/#work-list',
        'name': 'Matt Adam - Selected Work',
        'itemListElement': items,
    }

    page = {
        '@type': 'CollectionPage',
        '@id': WORK_ID,
        'url': 'https://mattadam.art/work/',
        'name': 'Work - Matt Adam',
        'description': clean_text(hero.get('statement')),
        'about': {'@id': PERSON_ID},
        'mainEntity': {'@id': work_list['@id']},
        'isPartOf': {'@id': HOME_ID},
    }

    return {'@context': 'https://schema.org', '@graph': [person, page, work_list]}


def script_for(data):
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    # Prevent any future CMS copy from accidentally closing the script element.
    payload = payload.replace('</script>', '<\\/script>')
    return '<script type="application/ld+json">\n' + payload + '\n</script>\n'


def patch_html(source, data):
    stripped = LD_RE.sub('', source)
    if '</head>' not in stripped:
        raise ValueError('generated HTML has no </head>')
    return stripped.replace('</head>', script_for(data) + '</head>', 1)


def json_ld_blocks(source):
    blocks = []
    for m in re.finditer(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        source,
        re.I | re.S,
    ):
        blocks.append(json.loads(m.group(1).replace('<\\/script>', '</script>')))
    return blocks


def expected_faq(content):
    faq = block_by_id(content['blocks'], 'faq') or {}
    return [
        (clean_text(i.get('q')), clean_text(i.get('a')))
        for i in faq.get('items', [])
        if clean_text(i.get('q')) and clean_text(i.get('a'))
    ]


def actual_faq(data):
    for node in data.get('@graph', []):
        if node.get('@type') == 'FAQPage':
            return [
                (
                    clean_text(i.get('name')),
                    clean_text((i.get('acceptedAnswer') or {}).get('text')),
                )
                for i in node.get('mainEntity', [])
            ]
    return []


def validate_page(path, expected_data, faq_content=None):
    with open(path, encoding='utf-8') as f:
        source = f.read()
    blocks = json_ld_blocks(source)
    if len(blocks) != 1:
        raise ValueError(f'{path}: expected exactly one JSON-LD block, found {len(blocks)}')
    if blocks[0] != expected_data:
        raise ValueError(f'{path}: JSON-LD does not match CMS-derived structured data')
    if faq_content is not None:
        want = expected_faq(faq_content)
        got = actual_faq(blocks[0])
        if got != want:
            raise ValueError(f'{path}: FAQ JSON-LD does not match visible CMS FAQ content')


def process(path, data, check=False, faq_content=None):
    if not os.path.exists(path):
        raise ValueError(f'missing generated page: {path}')
    with open(path, encoding='utf-8') as f:
        current = f.read()
    expected = patch_html(current, data)
    if check:
        if expected != current:
            raise ValueError(f'{path}: structured data is stale; run python3 structured_data.py')
        validate_page(path, data, faq_content=faq_content)
        return
    with open(path, 'w', encoding='utf-8') as f:
        f.write(expected)
    validate_page(path, data, faq_content=faq_content)


def main():
    check = '--check' in sys.argv
    home_content = load_json('content.json')
    work_content = load_json('work.json')

    try:
        process(P('index.html'), home_graph(home_content), check=check, faq_content=home_content)
        process(P('work', 'index.html'), work_graph(work_content), check=check)
    except (ValueError, json.JSONDecodeError) as exc:
        sys.exit('structured data validation failed:\n  - ' + str(exc))

    mode = '--check OK' if check else 'updated'
    print(f'structured data {mode}: homepage + /work derive from CMS content')


if __name__ == '__main__':
    main()
