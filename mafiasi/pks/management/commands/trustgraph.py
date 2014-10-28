import os

from PIL import Image

from django.core.management.base import NoArgsCommand
from django.conf import settings

from mafiasi.pks.models import KeysigningParty
from mafiasi.pks.graph import generate_graph

class Command(NoArgsCommand):
    help = 'Generate the trust graph'

    def handle_noargs(self, **options):
        self._build_graph('global')
        for party in KeysigningParty.objects.all():
            key_fingerprints = []
            for participant in party.participants.all():
                for key in participant.keys.all():
                    key_fingerprints.append(key.fingerprint)
            graph_name = 'party{}'.format(party.pk)
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
        print 'Trust graph "{}" generated.'.format(graph_name)
