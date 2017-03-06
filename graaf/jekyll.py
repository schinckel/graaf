from __future__ import unicode_literals

import os
import codecs

import yaml
import markdown

from .base import Generator


md = markdown.Markdown()


class JekyllGenerator(Generator):
    '''
    Generator to support Jekyll files.


    These files begin with a YAML document, followed by Markown content:

    ---
    title: Document title
    date: YYYY-mm-dd HH:MM:SS
    tags: [tag1, tag2]
    layout: template-name
    ---

    Markdown content goes here.

    '''
    extensions = ['.md', '.markdown']

    def process(self, root, dest_dir, filename, processor):
        basename, ext = os.path.splitext(filename)

        config = []

        with codecs.open(os.path.join(root, filename), 'r', 'utf-8') as fin:
            lines = iter(fin)

            line = next(lines)

            # If the markdown file starts with '---\n', then we extract the config data from
            # this YAML header, until we hit the next '---\n' Note that this is slightly less
            # strict, as it would support '---   \t\n', for instance.
            if line.rsplit() == ['---']:
                line = next(lines)

                try:
                    while line.rsplit() != ['---']:
                        config.append(line)
                        line = next(lines)
                except StopIteration:
                    return False

            config = yaml.load(''.join(config))
            content = ''.join(lines)

        config['content'] = md.reset().convert(content)

        with codecs.open(os.path.join(dest_dir, basename + '.html'), 'w', 'utf-8') as fout:
            tmpl = processor.templates['%(layout)s.html' % config]
            fout.write(tmpl.render(config))

        return True
