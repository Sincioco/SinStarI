"""Export the approved embedded novel illustrations to the web reader."""
import base64, hashlib, json, re

def externalize(source, web):
    plan = json.loads((web / 'production/illustrations.json').read_text(encoding='utf-8'))
    paths = []
    for image in plan['images']:
        pattern = r'<figure\b[^>]*id="' + re.escape(image['id']) + r'"[^>]*>.*?</figure>'
        matches = list(re.finditer(pattern, source, re.S))
        if len(matches) != 1:
            raise ValueError('Expected one approved illustration: ' + image['id'])
        figure = matches[0].group()
        embedded = re.findall(r'src="(data:image/webp;base64,([^"]+))"', figure)
        if len(embedded) != 1:
            raise ValueError('Approved source illustration must be embedded: ' + image['id'])
        uri, encoded = embedded[0]
        payload = base64.b64decode(encoded, validate=True)
        if hashlib.sha256(payload).hexdigest() != image['sha256']:
            raise ValueError('Approved image checksum changed: ' + image['id'])
        target = (web / image['image']).resolve()
        if not target.is_relative_to(web.resolve()):
            raise ValueError('Illustration path must stay inside the web folder')
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != payload:
            target.write_bytes(payload)
        source = source.replace(figure, figure.replace(uri, './' + image['image']), 1)
        paths.append(image['image'])
    (web / 'storyboards.json').write_text(json.dumps({'images': paths}, indent=2) + '\n', encoding='utf-8')
    return source
