from pathlib import Path
import os.path
import logging
from itertools import groupby

from jinja2 import Environment, FileSystemLoader
from flask import current_app
from flask.ext.assets import Bundle
from flask.ext.script import Command, Option


class GenDepConfig(Command):
    """Generate a YAML file for assets"""
    def __init__(self):
        self.static_dir = Path('.')
        self.asset_types = ['.js', '.css', '.scss', '.sass', '.less']
        # CSS filters may required external dependencies to actually work
        self.filter_map = {'js':'rjsmin', 
                           'scss':'scss,cssmin', 
                           'sass':'sass,cssmin', 
                           'less':'less,cssmin',
                           'css':'cssmin'}

        templ_path = os.path.dirname(__file__)
        loader = FileSystemLoader(templ_path)
        self.env = Environment(loader=loader)


    def run(self):
        self.static_dir = Path(current_app.static_folder, 'vendor')
        asset_dirs = self.find_asset_dirs()
        # use the template instead 
        all_bundles = '#AUTOMATICALLY GENERATED FILE\n#You may need to make changes\n'

        all_assets = []

        for i in asset_dirs:
            all_assets.append(self.get_assets_by_type(i))

        rendered_config = self.render_config(all_assets)
        output_path = Path(current_app.config.get('APP_ROOT', os.path.dirname(__file__)), 'assets.yml')

        with output_path.open(mode='w') as fd:
            fd.write(rendered_config)
        logging.info('Wrote: {}'.format(output_path))


    def find_asset_dirs(self):
        """ explore static/vendor for assets """
        assets = []
        for i in self.static_dir.iterdir():
            if i.is_dir():
                asset = {'NAME':i.name, 'PATH':i}
                assets.append(asset)
        return assets


    def get_assets_by_type(self, asset_dir):
        ext_key = lambda i: i.suffix
        files = sorted(asset_dir['PATH'].rglob('*'), key=ext_key)
        assets = {'contents':{}}

        for k, g in groupby(files, ext_key):
            if k in self.asset_types:
                assets['contents'][k.lstrip('.')] = list(g)

        assets.update(asset_dir)
        return assets

    
    def gen_sass_script(self, asset, defs):
        """This exists to deal with webassets being seemingly unable to build some 
        SCSS things (like Bootstrap) without modifying relative @import paths.
        It produces a shell type script that sould be run directly."""
        cmd = 'sass {}'
        args = ''
        asset_type = defs['filters'].split(',')[0]
        if asset_type == 'scss':
            args += ' --scss'
        asset_paths = set([i.parent for i in Path(asset['PATH']).rglob('*.'+asset_type) if not i.is_dir() and 'test' not in str(i)])
        base_dir = min(asset_paths, key=lambda i: len(str(i)))
        watch = '{}:{}'.format(base_dir, self.static_dir)
        args += ' --stop-on-error --watch '+watch

        script_name = defs['name']+'.sass'
        script_path = self.static_dir.joinpath(script_name)
        with script_path.open(mode='w') as fd:
            fd.write('#! /bin/bash\n')
            fd.write(cmd.format(args))
        
        logging.info('Wrote: {}'.format(script_path))
        logging.info('Your source files or the script may need modification in order to work.')


    def gen_asset_config(self, asset):
        """ Get filter and inspect contents for asset """
        bundle_defs = []
        for k, v in asset['contents'].items():
            minified = [str(i).replace(str(self.static_dir), 'vendor') for i in v if '.min' in i.suffixes]
            if minified:
                name = '{}-{}-min'.format(asset['NAME'], k)
                output = '{}.min.{}'.format(asset['NAME'], k)
                # filters = self.filter_map.get(k, '')
                contents = sorted(minified)
                defs = {'name':name,
                        'output':output,
                        'filters':'', # don't apply filters to minified assets
                        'contents':contents}
                bundle_defs.append(defs)

            non_minified = [str(i).replace(str(self.static_dir), 'vendor') for i in v if '.min' not in i.suffixes]
            if non_minified:
                if k in['sass', 'scss', 'less']:
                    output = '{}.css'.format(asset['NAME'])
                    is_sass = True

                else:
                    output = '{}.{}'.format(asset['NAME'], k)
                    is_sass = False
               
                filters = self.filter_map.get(k, '')
                name = '{}-{}'.format(asset['NAME'], k)
                contents = sorted(non_minified)
                defs = {'name':name,
                        'output':output,
                        'filters':filters,
                        'contents':contents}
                bundle_defs.append(defs)

                if is_sass:
                    sass_script = self.gen_sass_script(asset, defs)
                    # DO SOMETHING WITH THIS SCRIPT!

        return bundle_defs


    def render_config(self, assets):
        all_bundles = ''
        templ = self.env.get_template('asset_config.template')
       
        bundles = []

        for i in assets:
            bundles.extend(self.gen_asset_config(i))
    
        rendr = templ.render(bundles=bundles)
        return rendr

