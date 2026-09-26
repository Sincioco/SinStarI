"""Keep LTX's two sampling stages aligned and crop to the requested export size."""


def sampling_size(width, height):
    return ((width + 63) // 64 * 64, (height + 63) // 64 * 64)


def crop_output(graph, ui, width, height):
    padded_width, padded_height = sampling_size(width, height)
    if (width, height) == (padded_width, padded_height):
        return
    values = dict(width=width, height=height,
                  x=(padded_width - width) // 2, y=(padded_height - height) // 2)
    graph['101:902'] = dict(class_type='ImageCrop',
        inputs=dict(image=['101:449', 0], **values),
        _meta=dict(title=f'Final {width} x {height} — Center Crop'))
    graph['101:451']['inputs']['images'] = ['101:902', 0]
    group = next(g for g in ui['definitions']['subgraphs']
                 if any(n['id'] == 449 for n in g['nodes']))
    link_id = max(group['state']['lastLinkId'], max(link['id'] for link in group['links'])) + 1
    # Preserve the existing decode link; insert the crop before video/audio assembly.
    link = next(link for link in group['links'] if link['id'] == 711)
    link.update(target_id=902, target_slot=0)
    group['links'].append(dict(id=link_id, origin_id=902, origin_slot=0,
                              target_id=451, target_slot=0, type='IMAGE'))
    create = next(n for n in group['nodes'] if n['id'] == 451)
    create['inputs'][0]['link'] = link_id
    inputs = [dict(name='image', type='IMAGE', link=711)]
    inputs += [dict(name=key, type='INT', widget=dict(name=key), link=None) for key in values]
    group['nodes'].append(dict(id=902, type='ImageCrop', pos=[5100, 6100], size=[280, 210],
        flags={}, order=46, mode=0, inputs=inputs,
        outputs=[dict(name='IMAGE', type='IMAGE', links=[link_id])],
        properties={'Node name for S&R': 'ImageCrop', 'cnr_id': 'comfy-core'},
        widgets_values=list(values.values()), widgets_values_named=values,
        title=f'Final {width} x {height} — Center Crop'))
    group['state'].update(lastNodeId=max(902, group['state']['lastNodeId']), lastLinkId=link_id)
    shot = next(n for n in ui['nodes'] if n['id'] == 101)
    shot['title'] += f' | {width} x {height} Output'
