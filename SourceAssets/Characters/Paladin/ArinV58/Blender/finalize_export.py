"""Keep native part order and sockets tied to the v5.8 equipment export."""
import json
import struct
from pathlib import Path


def finalize_export(path):
    path = Path(path)
    data = path.read_bytes()
    size = struct.unpack_from('<I', data, 12)[0]
    document = json.loads(data[20:20+size])
    nodes = document['nodes']
    # The native cooker bakes mesh-node bind transforms into vertices. Skinned
    # positions already use armature bind space, so cancel the root's static
    # translation on mesh nodes to avoid applying it twice. Animation is intact.
    roots = document['scenes'][document.get('scene', 0)]['nodes']
    for index in roots:
        root = nodes[index]
        assert not any(key in root for key in ('rotation','scale','matrix'))
        offset = root.get('translation', [0,0,0])
        for child in root.get('children', []):
            node = nodes[child]
            if 'skin' in node:
                assert not any(key in node for key in ('rotation','scale','matrix'))
                node['translation'] = [-value for value in offset]
    # The cooker traverses children in order. Visit the skeleton's Shield and
    # Sword before the body, without changing transforms, indices or animation.
    for node in nodes:
        if 'children' in node:
            node['children'].sort(key=lambda index: nodes[index].get('name') == 'Body')
    order = []
    def visit(index):
        node = nodes[index]
        if 'mesh' in node:
            order.append(node['name'])
        for child in node.get('children', []):
            visit(child)
    for root in document['scenes'][document.get('scene', 0)]['nodes']:
        visit(root)
    assert order == ['Shield', 'Sword', 'Body'], order
    encoded = json.dumps(document, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    tail = data[20+size:]
    path.write_bytes(struct.pack('<III', 0x46546c67, 2, 20+len(encoded)+len(tail))
                     + struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + tail)
    return document


if __name__ == '__main__':
    finalize_export(Path(__file__).resolve().parents[1]/'arin-v5.8-animation-checkpoint.glb')
