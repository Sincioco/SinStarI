"""Readable review labels and illustrated credits, rendered with installed Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONTS = Path('C:/Windows/Fonts')
WHITE, GOLD, MUTED = '#f4f6fa', '#f1c878', '#bdc8d8'


def font(size, bold=False):
    return ImageFont.truetype(str(FONTS / ('segoeuib.ttf' if bold else 'segoeui.ttf')), size)


def lines(text, face, width):
    result = []
    for paragraph in text.split('\n'):
        line = ''
        for word in paragraph.split():
            if face.getlength(word) > width:
                # Long filenames/URLs are still shown in full.
                for character in word:
                    if face.getlength(line + character) > width:
                        result.append(line)
                        line = ''
                    line += character
                continue
            candidate = (line + ' ' + word).strip()
            if line and face.getlength(candidate) > width:
                result.append(line)
                line = word
            else:
                line = candidate
        result.append(line)
    return result


def text_block(draw, text, xy, width, size, fill=WHITE, bold=False):
    face = font(size, bold)
    x, y = xy
    for line in lines(text, face, width):
        draw.text((x, y), line, font=face, fill=fill, anchor='lt')
        y += round(size * 1.32)
    return y


def review_panel(blocks, width, maximum_height, opacity):
    """Fit a complete panel without clipping; shrink only when the copy needs it."""
    for reduction in range(9):
        fitted = [(text, max(18, size - reduction), color, bold) for text, size, color, bold in blocks if text]
        height = 40 + sum(len(lines(text, font(size, bold), width - 44)) * round(size * 1.32) + 9
                          for text, size, color, bold in fitted)
        if height <= maximum_height:
            break
    else:
        raise ValueError('Review panel is too tall; shorten the configured review notes.')
    panel = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), 14, fill=(6, 15, 31, round(255 * opacity)))
    y = 20
    for text, size, color, bold in fitted:
        y = text_block(draw, text, (22, y), width - 44, size, color, bold) + 9
    return panel


def overlay(entry, number, total, target, config):
    canvas = Image.new('RGBA', (1920, 1080))
    settings = config['settings']
    if settings.get('show_labels', True) is False:
        canvas.save(target)
        return
    notes = config.get('scene_notes', {}).get(entry['scene'], {})
    info = [
        ('Sin Star I · Story Video Sequence Review', 24, GOLD, True),
        (entry['chapter'], 34, WHITE, True),
        (entry['scene'] + ' — ' + entry['scene_title'], 27, WHITE, False),
        (Path(entry['file']).name, 21, MUTED, False),
        ('WHY THIS SCENE EXISTS', 20, GOLD, True),
        (notes.get('purpose', 'Review visual continuity and character performance.'), 23, WHITE, False),
    ]
    context = [('SCENE CONTEXT', 21, GOLD, True), (entry['context'], 26, WHITE, False)]
    opacity = settings.get('panel_opacity', .8)
    if settings.get('layout', 'overlay') == 'side-by-side':
        # The complete source frame stays on the left; review copy owns the right column.
        ImageDraw.Draw(canvas).rectangle((1344, 0, 1919, 1079), fill='#0c192b')
        left = review_panel(info, 552, 420, opacity)
        canvas.alpha_composite(left, (1356, 12))
        for label, key in [('CHARACTER DEVELOPMENT', 'character_development'),
                           ('REVELATION / WHAT CHANGES', 'revelation'),
                           ('CONNECTIONS AND LATER PAYOFFS', 'connections')]:
            context += [(label, 20, GOLD, True), (notes.get(key, ''), 22, WHITE, False)]
        top = 24 + left.height
        right = review_panel(context, 552, 1068 - top, opacity)
        canvas.alpha_composite(right, (1356, top))
    else:
        positions = {'scene_info': 'upper-left', 'scene_context': 'upper-right',
                     **config.get('panel_positions', {}), **entry.get('panel_positions', {})}
        if positions['scene_info'] == positions['scene_context']:
            raise ValueError('Scene panels need different corners: ' + entry['id'])
        for name, blocks, width in [('scene_info', info, 810), ('scene_context', context, 662)]:
            panel = review_panel(blocks, width, 470, opacity)
            corner = positions[name]
            if corner not in ('upper-left', 'upper-right', 'lower-left', 'lower-right'):
                raise ValueError('Unknown panel corner: ' + corner)
            x = 38 if corner.endswith('left') else 1882 - width
            y = 36 if corner.startswith('upper') else 1044 - panel.height
            canvas.alpha_composite(panel, (x, y))
        draw = ImageDraw.Draw(canvas)
        take = entry.get('take', '')
        badge = f'{number:03d} / {total:03d}' + (f'  ·  {take}' if take else '')
        draw.rounded_rectangle((755, 1032, 1165, 1077), 9, fill=(6, 15, 31, round(255 * opacity)))
        draw.text((775, 1043), badge, font=font(22), fill=WHITE, anchor='lt')
    canvas.save(target)


def poster(source, target):
    image = Image.open(source).convert('RGB')
    # Preserve the complete poster, including its title and original artwork.
    ImageOps.pad(image, (1920, 1080), color='#070e1b').save(target)


def credits(root, settings, target):
    canvas = ImageOps.fit(Image.open(root / settings['background']).convert('RGBA'), (1920, 1080))
    shade = Image.new('RGBA', canvas.size)
    draw = ImageDraw.Draw(shade)
    draw.rounded_rectangle((60, 48, 1090, 1027), 26, fill=(5, 14, 31, 204))
    canvas.alpha_composite(shade)
    logo = Image.open(root / settings['logo']).convert('RGBA')
    logo.thumbnail((270, 190), Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo, (100, 77))
    draw = ImageDraw.Draw(canvas)
    draw.text((407, 108), 'SIN STAR I', font=font(62, True), fill=WHITE, anchor='lt')
    draw.text((410, 191), 'A universe worth fighting for', font=font(28), fill=GOLD, anchor='lt')
    draw.line((100, 287, 1046, 287), fill='#527188', width=2)
    y = text_block(draw, settings['creator'], (100, 318), 943, 33, WHITE, True)
    y = text_block(draw, settings['statement'], (100, y + 24), 910, 27, MUTED)
    y = text_block(draw, 'OPEN SOURCE · BUILT WITH SMILE 2.0', (100, y + 28), 943, 22, GOLD, True)
    for label, value in settings['links']:
        y = text_block(draw, f'{label}  {value}', (100, y + 12), 943, 24)
    y = text_block(draw, 'Music: Starforge Horizon · Starforge March · Bloom',
                   (100, y + 24), 943, 23, GOLD)
    y = text_block(draw, 'Storyboard concept animation · LTX 2.5 · Game in development',
                   (100, y + 11), 943, 22, MUTED)
    if y > 1006:
        raise ValueError('Credits overflow; shorten the configured credit text')
    canvas.convert('RGB').save(target)
