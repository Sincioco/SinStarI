"""Truthful, stable discovery metadata for the single-page book reader."""
import html
import json

CANONICAL = 'https://sinstar.sincioco.com/BookOne/'
TITLE = 'Sin Star: Book One - Novel & Audiobook by Louiery R. Sincioco'
DESCRIPTION = ('Read and listen to Sin Star: Book One, a science-fantasy novel by '
               'Louiery R. Sincioco (Sin), with synchronized narration and offline audio downloads.')
IMAGE = CANONICAL + 'images/01-panel-01-1.webp'
IMAGE_ALT = 'Young Arin with his parents aboard a spacecraft, from Sin Star: Book One.'

def metadata_html():
    book = {
        '@context':'https://schema.org', '@type':'Book', '@id':CANONICAL+'#book',
        'url':CANONICAL, 'name':'Sin Star: Book One', 'description':DESCRIPTION,
        'author':{'@type':'Person','name':'Louiery R. Sincioco','alternateName':'Sin',
                  'url':'https://sincioco.com/'},
        'inLanguage':'en', 'genre':'Science fantasy', 'isAccessibleForFree':True,
        'bookFormat':'https://schema.org/EBook', 'image':IMAGE
    }
    tags = [f'<title>{html.escape(TITLE)}</title>',
            f'<link rel="canonical" href="{CANONICAL}">']
    for key, value in [('description',DESCRIPTION),('author','Louiery R. Sincioco (Sin)'),
                       ('twitter:card','summary_large_image'),('twitter:title',TITLE),
                       ('twitter:description',DESCRIPTION),('twitter:image',IMAGE),
                       ('twitter:image:alt',IMAGE_ALT)]:
        tags.append(f'<meta name="{key}" content="{html.escape(value,quote=True)}">')
    for key, value in [('og:type','book'),('og:site_name','Sin Star'),('og:title',TITLE),
                       ('og:description',DESCRIPTION),('og:url',CANONICAL),
                       ('og:image',IMAGE),('og:image:type','image/webp'),
                       ('og:image:width','766'),('og:image:height','508'),
                       ('og:image:alt',IMAGE_ALT),('book:author','https://sincioco.com/')]:
        tags.append(f'<meta property="{key}" content="{html.escape(value,quote=True)}">')
    # JSON-LD is a non-executable HTML data block; keep the existing CSP intact.
    tags.append('<script type="application/ld+json">'+json.dumps(book,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+'</script>')
    return '\n'.join(tags)
