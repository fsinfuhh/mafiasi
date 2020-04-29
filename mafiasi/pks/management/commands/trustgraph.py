import os

from PIL import Image

from django.core.management.base import BaseCommand
from django.conf import settings

from mafiasi.pks.models import KeysigningParty
from mafiasi.pks.graph import generate_graph


# monkey-patch max image size to prevent decompression bomb errors on our very large trust graph
Image.MAX_IMAGE_PIXELS *= 2


class Command(BaseCommand):
    help = 'Generate the trust graph'

    def add_arguments(self, parser):
        parser.add_argument('graph', nargs='*')

    def handle(self, *args, **options):
        graphs = options['graph']
        if not graphs or 'global' in graphs:
            self._build_graph('global')
        
        for party in KeysigningParty.objects.all():
            graph_name = 'party{}'.format(party.pk)
            if graphs and graph_name not in graphs:
                continue
            key_fingerprints = []
            for participant in party.participants.all():
                for key in participant.keys.all():
                    key_fingerprints.append(key.fingerprint)
            self._build_graph(graph_name, key_fingerprints)
    
    def _build_graph(self, graph_name, restrict_keys=None):
        name = 'pks-graph-{}'.format(graph_name)
        thumb_name = 'pks-graphthumb-{}'.format(graph_name)
        svg_file = os.path.join(settings.MEDIA_ROOT, name + '.svg')
        png_file = os.path.join(settings.MEDIA_ROOT, name + '.png')
        thumb_file = os.path.join(settings.MEDIA_ROOT, thumb_name + '.png')
        generate_graph([svg_file, png_file], restrict_keys=restrict_keys)
        img = Image.open(png_file)
        img.thumbnail((150, 150), Image.ANTIALIAS)
        img.save(thumb_file)
        print('Trust graph "{}" generated.'.format(graph_name))
