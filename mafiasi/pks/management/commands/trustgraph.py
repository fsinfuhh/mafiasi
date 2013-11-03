import os

from PIL import Image

from django.core.management.base import NoArgsCommand
from django.conf import settings

from mafiasi.pks.graph import generate_graph

class Command(NoArgsCommand):
    help = 'Generate the trust graph'

    def handle_noargs(self, **options):
        name = 'pks-graph-global'
        thumb_name = 'pks-graphthumb-global'
        svg_file = os.path.join(settings.MEDIA_ROOT, name + '.svg')
        png_file = os.path.join(settings.MEDIA_ROOT, name + '.png')
        thumb_file = os.path.join(settings.MEDIA_ROOT, thumb_name + '.png')
        generate_graph([svg_file, png_file])
        img = Image.open(png_file)
        img.thumbnail((150, 150), Image.ANTIALIAS)
        img.save(thumb_file)
        print 'Trust graph generated.'

