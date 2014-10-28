from __future__ import division

import os
from binascii import hexlify
from cgi import escape as escape_html
import xml.etree.ElementTree as ET

import gpgme
import pygraphviz
import networkx

MAX_CLIQUE_COLORS = ['deeppink', 'darkviolet', 'blue', 'forestgreen']

def generate_graph(filenames, filter_invalid=True, restrict_keys=None,
                   prog='neato'):
    ctx = gpgme.Context()
    ctx.keylist_mode = gpgme.KEYLIST_MODE_SIGS
    
    if restrict_keys is None:
        keys = ctx.keylist()
    else:
        keys = ctx.keylist(restrict_keys)

    key_list = []
    for key in keys:
        try:
            subkey = key.subkeys[0]
        except IndexError:
            continue
        if filter_invalid and (subkey.expired or subkey.revoked):
            continue
        key_list.append(key)
    
    graph_dict = _build_signature_graph(key_list)
    cliques = _find_max_cliques(graph_dict)
    signature_stats = _build_signature_stats(graph_dict)
    
    # Calculate labels and unconnected nodes
    labels = {}
    unconnected_nodes = []
    for key in key_list:
        keyid = key.subkeys[0].keyid
        name = key.uids[0].name
        labels[keyid] = u'<{0}<BR/><FONT POINT-SIZE="10">{1}</FONT>>'.format(
                escape_html(name), keyid)

        not_connected = (signature_stats['sigcount'][keyid] == 0 and
                         signature_stats['signedbycount'][keyid] == 0)
        if not_connected:
            unconnected_nodes.append(keyid)
    
    # Map keyids to their cliques
    clique_map = {}
    for clique_no, clique in enumerate(cliques):
        for keyid in clique:
            clique_map.setdefault(keyid, []).append(clique_no)

    
    # Start building the graph 
    flipped_edges = set()
    g = pygraphviz.AGraph(directed=True,
                          overlap='scale',
                          splines=True,
                          nodesep=0.2,
                          outputMode='edgesfirst')
    g.node_attr['style']='filled'
    
    for keyid in graph_dict:
        red, green, blue = _get_color(signature_stats, keyid)
        luminance = 0.299 * red + 0.587 * green + 0.114 * blue
        attrs = {
            'id': keyid,
            'label': labels[keyid],
            'fillcolor': _hex_color(red, green, blue),
            'fontcolor': '#eeeeee' if luminance < 0.55 else '#000000'
        }
        if keyid in clique_map:
            clique_no = clique_map[keyid][0]
            color = MAX_CLIQUE_COLORS[clique_no % len(MAX_CLIQUE_COLORS)]
            attrs['penwidth'] = 2
            attrs['color'] = color
        g.add_node(keyid, **attrs)
    
    # Add edges for signatures
    for signed_keyid, signer_keyids in graph_dict.items():
        for signer_keyid in signer_keyids:
            if (signer_keyid, signed_keyid) in flipped_edges:
                continue
            edge_id = '{0}_{1}'.format(signer_keyid, signed_keyid)
            both_signed = signed_keyid in graph_dict[signer_keyid]
            direction = 'both' if both_signed else 'forward'
            attrs = {
                'id': edge_id,
                'dir': direction
            }
            
            same_clique = -1
            if signer_keyid in clique_map and signed_keyid in clique_map:
                for clique_a in clique_map[signer_keyid]:
                    for clique_b in clique_map[signed_keyid]:
                        if clique_a == clique_b:
                            same_clique = clique_a

            if same_clique != -1:
                color = MAX_CLIQUE_COLORS[same_clique % len(MAX_CLIQUE_COLORS)]
                attrs['penwidth'] = 2
                attrs['color'] = color
            
            g.add_edge(signer_keyid, signed_keyid, **attrs)
            if both_signed:
                flipped_edges.add((signed_keyid, signer_keyid))
    
    # Draw invisible edges around unconnected nodes for better styling
    if prog == 'dot':
        for keyid_a, keyid_b in zip(unconnected_nodes, unconnected_nodes[1:]):
            g.add_edge(keyid_a, keyid_b, style='invis')

    g.layout(prog)

    for filename in filenames:
        g.draw(filename)

        if filename.endswith('.svg'):
            _annotate_svg(filename)

def _build_signature_graph(key_list):
    graph = {}
    for key in key_list:
        try:
            keyid = key.subkeys[0].keyid
        except IndexError:
            continue
        graph[keyid] = set()

    for key in key_list:
        signature_keyids = _get_signature_keyids(key)
        for signer_keyid in signature_keyids:
            try:
                signed_keyid = key.subkeys[0].keyid
                if signer_keyid not in graph:
                    continue
                if signed_keyid == signer_keyid:
                    continue
                graph[signed_keyid].add(signer_keyid)
            except (IndexError, KeyError):
                continue
    return graph

def _get_signature_keyids(key):
    return_sigs = set()
    for uid in key.uids:
        for sig in uid.signatures:
            if sig.expired or sig.revoked or sig.invalid:
                continue
            return_sigs.add(sig.keyid)
    return return_sigs

def _find_max_cliques(graph_dict):
    graph = networkx.Graph()
    directed_edges = set()
    for signed_keyid, signer_keyids in graph_dict.items():
        graph.add_node(signed_keyid)
        for signer_keyid in signer_keyids:
            directed_edges.add((signer_keyid, signed_keyid))
    
    for edge_from, edge_to in directed_edges:
        if (edge_to, edge_from) in directed_edges:
            graph.add_edge(edge_from, edge_to)

    clique_nos = {}
    for clique in networkx.find_cliques(graph):
        clique_nos.setdefault(len(clique), []).append(clique)

    return clique_nos[max(clique_nos)] if clique_nos else []

def _build_signature_stats(graph_dict):
    stats = {
        'maxsignedbycount': 0,
        'maxsigcount': 0,
        'maxratio': 0.0,
        'signedbycount': {},
        'sigcount': {}
    }
    signedbycount = stats['signedbycount']
    sigcount = stats['sigcount']
    
    for keyid in graph_dict:
        sigcount[keyid] = 0

    for signed_keyid, signature_keyids in graph_dict.items():
        signedbycount[signed_keyid] = len(signature_keyids)
        for signer_keyid in signature_keyids:
            sigcount[signer_keyid] += 1

    if signedbycount:
        stats['maxsignedbycount'] = max(signedbycount.values())
    if sigcount:
        stats['maxsigcount'] = max(sigcount.values())
    
    ratios = [signedbycount[keyid] / sigcount[keyid] for keyid in graph_dict
              if sigcount[keyid] != 0]
    if ratios:
        stats['maxratio'] = max(ratios)

    return stats

def _get_color(signature_stats, keyid):
    # Magic colors code inspired by sig2dot tool from signing-party
    sigcount = signature_stats['sigcount']
    signedbycount = signature_stats['signedbycount']
    maxratio = signature_stats['maxratio']
    maxsigcount = signature_stats['maxsigcount']
    maxsignedbycount = signature_stats['maxsignedbycount']

    red, green, blue = 0, 1/3, 1/3
    red = sigcount[keyid] / maxsigcount if maxsigcount else 0
    if sigcount[keyid] and maxratio != 0:
        green = ((signedbycount[keyid] / sigcount[keyid] / maxratio * 0.75) *
                 2/3 + 1/3)
    if signedbycount[keyid] and maxsignedbycount != 0:
        blue = (signedbycount[keyid] / maxsignedbycount) * 2/3 + 1/3
    
    return red, green, blue

def _hex_color(red, green, blue):
    color = ''.join(chr(int(round(x * 255))) for x in (red, green, blue))
    return '#' + hexlify(color)

def _annotate_svg(filename):
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree = ET.parse(filename)
    root = tree.getroot()
    defs_tag = tree.find('defs')
    if defs_tag is None:
        defs_tag = ET.Element('defs')
        root.insert(0, defs_tag)
    script_tag = ET.Element('script', {'type': 'text/javascript'})
    with open(os.path.join(os.path.dirname(__file__), 'graph_svg.js')) as js:
        script_tag.text = js.read()
    defs_tag.insert(0, script_tag)
    tree.write(filename, encoding='utf-8')
