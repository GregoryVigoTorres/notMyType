# this could benefit from testing
from pathlib import Path
import os.path
import logging
import configparser
import tempfile
import tarfile
import zipfile

import requests

from flask import current_app
from flask.ext.script import Command, Option
from flask.ext.assets import Bundle
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger()

class ConfigError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class GenAssetsConfig():
    """Generate a YAML file for assets"""
    def __init__(self):
        templ_path = os.path.dirname(__file__)
        loader = FileSystemLoader(templ_path)
        self.env = Environment(loader=loader)
        self.config = configparser.ConfigParser()
        self.config.read('deps.conf')
        self.static_dir = Path(current_app.static_folder, 'vendor')
        # Only include non-dev assets in assets.yml
        asset_defs = [i for name, i in self.config.items() if i.get('DEV')=='False']
        # generate list of dicts with yml fields to pass to template
        bundles = [self.gen_asset_dict(i) for i in asset_defs]
        yml = self.render_yml(bundles)
        self.write_yml(yml)


    def render_yml(self, bundles):
        templ = self.env.get_template('asset_config.template')
        yml = templ.render(bundles=bundles)
        return yml


    def write_yml(self, yml):
        """ 
            Append yml to assets.yml for app,
            or save in this directory
        """
        output_path = Path(current_app.config.get('APP_ROOT', os.path.dirname(__file__)), 'assets.yml')
        
        if not output_path.exists():
            output_path.touch()

        with output_path.open(mode='a') as fd:
            fd.write(yml)
        logger.info('Saved assets to: {}'.format(output_path))


    def find_contents(self, asset_def):
        """ 
            Use filenames in URLS,
            scan asset directory for included files 
        """
        asset_dir = self.static_dir.joinpath(asset_def.name.lower())
        include_fns = [asset_dir.joinpath(i.split('/')[-1]) for i in asset_def['URLS'].split()]
        # make sure the files are really there
        if not all([i.exists() for i in include_fns]):
            raise ConfigError('Some files are missing')

        contents = [str(i).replace(str(self.static_dir), 'vendor') for i in include_fns]
        return contents

    
    def gen_asset_dict(self, asset_def):
        d = {'name':asset_def.name.lower(),
             'filters':asset_def.get('FILTERS'),
             'output':asset_def.get('OUTPUT_NAME'),
             'contents':self.find_contents(asset_def)}
        return d


class GetDeps(Command):
    """Install non-Python CSS/JS dependencies from deps.conf into App static/vendor"""
    option_list = (Option('--try-again', '-t', dest='try_again', required=False),)

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('deps.conf')
        self.headers = {'user-agent':'FlaskPlateBoiler-v0.1'}
        self.tries = 3
        self.chunk = 400
        self.encoding = 'utf-8'
        self.static_path = None
        self.dep_path = None
        self.ftype = None
        self.text_types = ['js', 'map', 'css', 'scss', 'sass', 'less']
        self.tempf = tempfile.TemporaryFile()

    def run(self, try_again=None):
        # current_app needs context, available here
        self.static_path = Path(current_app.static_folder, 'vendor')

        if not self.static_path.exists():
            self.static_path.mkdir()

        for name, sec in self.config.items():
            # sec is section name
            if name == 'DEFAULT':
                continue
            logger.info('Getting {}'.format(name))
            try:
                urls = sec['URLS'].split()
            except KeyError as E:
                logger.warning('URLS required')

            # name is where deps are saved
            # don't confuse it with output name, which needs to have an extension and is not used here
            # Make sure dev deps are included with the right parent.
            if sec.getboolean('DEV'):
                _name = sec.get('INCLUDE_WITH')
                if _name:
                    name = _name

            name = name.lower()
            
            for url in urls:
                downloaded = self.download(url)
                if not downloaded:
                    continue
                ftype = self.get_file_type(url) 

                dest_dir = self.static_path.joinpath(name)
                self.save_or_unpack(ftype, dest_dir, url)

        self.tempf.close()

        do_asset_config = input('Generate assets.yml? y/n\n')
        if do_asset_config == 'y':
            GenAssetsConfig()


    def download(self, url):
        tries = 1

        while tries <= self.tries:
            logger.info('Downloading... {}'.format(url))
            tries += 1

            try:
                req = requests.get(url, headers=self.headers, stream=True)

                if req.status_code != 200:
                    logger.warning('DOWNLOAD FAILED! {}'.format(req.status_code))
                    raise requests.exceptions.RequestException

                if req.encoding:
                    self.encoding = req.encoding

                for chunk in req.iter_content(self.chunk):
                    self.tempf.write(chunk)
                return True

            except Exception as E:
                logger.warning('DOWNLOAD FAILED! {}'.format(url))
                logger.warning(E)


    def get_file_type(self, url):
        """ Determine filetype of source file by extension 
        """
        suff = url.split('.')[-1]

        if suff in self.text_types:
            return 'text'
        if suff == 'gz' or suff == 'bz':
            return 'tar'
        if suff.endswith('zip'):
            return 'zip'


    def save_or_unpack(self, ftype, dest_dir, url):
        """ Route to appropriate function based on filetype 
            Data should already be in self.tempf
        """
        fn = url.split('/')[-1]
        dest_path = dest_dir.joinpath(fn)
        
        if ftype == 'text':
            self.save_as_text(dest_path)
        elif ftype == 'zip':
            self.unzip(dest_path)
        elif ftype == 'tar':
            self.unpack_tar(dest_path)
        else:
            msg = 'Unknown file type: [{}]'.format(ftype)
            # This should probably be a different Exception...
            # Or maybe files should just be saved as text
            raise ConfigError(msg)


    def unpack_tar(self, dest_path):
        """ unpack tarfile and save 
        """
        try:
            self.tempf.seek(0)
            tball = tarfile.open(fileobj=self.tempf)

            for i in tball.getmembers():
                if i.name.startswith('..') is False and i.name.startswith('/') is False:
                    logger.info('Extracting... {}'.format(i.name))
                    tball.extract(i, path=str(dest_path))
            logger.info('Saved {}'.format(dest_path))
        except Exception as e:
            logger.warning('COULD NOT SAVE TAR FILE')
            logger.warning(e)

    
    def unzip(self, dest_path):
        """ extract zip file 
        """
        try:
            self.tempf.seek(0)
            with zipfile.ZipFile(self.tempf) as zf:
                for i in zf.infolist():
                    if i.filename.startswith('..') is False and i.filename.startswith('/') is False:
                        zf.extract(i, path=str(dest_path))
                        logger.info('Extracting.........{}'.format(i.filename))
                logger.info('Saved {}'.format(dest_path))
        except Exception as e:
            logger.warning('COULD NOT SAVE ZIP FILE')
            logger.warning(e)


    def save_as_text(self, dest_path):
        """ 
        dest_path needs to be a Path object
        """
        with dest_path.open(mode='w') as fd:
            try:
                self.tempf.seek(0)
                fd.write(self.tempf.read().decode(self.encoding))
                logger.info('saved {}'.format(dest_path))
                return True
            except Exception as e:
                logger.warning('FILE NOT SAVED!')
                logger.warning(e)
                return False
    

