from pathlib import Path
import logging
import configparser
import tempfile
import tarfile
import zipfile

import requests

from flask import current_app
from flask.ext.script import Command, Option


class GetDeps(Command):
    """Install non-Python CSS/JS dependencies from deps.conf into App static/vendor"""

    option_list = (Option('--try-again', '-t', dest='try_again', required=False),)

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('deps.conf')
        self.headers = {'user-agent':'FlaskPlateBoiler-v0.1'}
        self.tempf = tempfile.TemporaryFile()
        self.chunk = 400
        self.encoding = 'utf-8'
        self.static_path = None
        self.dep_path = None
        self.ftype = None
        self.text_types = ['.js', '.css', '.scss', '.sass', '.less']

    def run(self, try_again=None):
        self.static_path = Path(current_app.static_folder, 'vendor')

        if not self.static_path.exists():
            self.static_path.mkdir()

        dep_queue = []

        if try_again:
            logging.info('Trying again: {}'.format(try_again))
            dep_queue.append(self.config[try_again.upper()])
        else:
            for dep_name in self.config['DEPS']:
                if self.config['DEPS'].getboolean(dep_name):
                    dep_queue.append(self.config[dep_name.upper()])

        for i in dep_queue:
            self.download(i)
            self.ftype = self.get_file_type(i)
            self.save_or_unpack(i)

        self.tempf.close()
        logging.info('You can now run config_deps to generate a YAML config file for flask-assets')


    def save_or_unpack(self, dep_config):
        """Route to appropriate function based on filetype """
        dest_dir = self.get_dest_path(dep_config)

        if self.ftype == 'text':
            self.save_as_text(dest_dir)

        if self.ftype == 'zip':
            self.unzip(dest_dir)

        if self.ftype == 'tar':
            self.unpack_tar(dest_dir)


    def get_dest_path(self, dep_config):
        """save in directory [dep_name] in static/vendor """
        dest_dir = self.static_path.joinpath(dep_config.name.lower())
        if not dest_dir.exists():
            dest_dir.mkdir()

        return dest_dir


    def download(self, dep_config):
        url = dep_config['URL']
        logging.info('Downloading... {}'.format(dep_config.name.capitalize()))

        try:
            req = requests.get(url, headers=self.headers, stream=True)
        except requests.exceptions.ConnectionError as err:
            logging.info('DOWNLOAD FAILED! {}'.format(url))
            logging.info(err)
            return None

        if req.status_code != 200:
            logging.info('DOWNLOAD FAILED! code:{} for:"{}"'.format(req.status_code, url))

        self.encoding = req.encoding

        for chunk in req.iter_content(self.chunk):
            self.tempf.write(chunk)


    def unpack_tar(self, dest_dir):
        """ unpack tarfile and save """
        try:
            self.tempf.seek(0)
            tball = tarfile.open(fileobj=self.tempf)

            for i in tball.getmembers():
                if i.name.startswith('..') is False and i.name.startswith('/') is False:
                    logging.info('Extracting.........{}'.format(i.name))
                    tball.extract(i, path=str(dest_dir))
            logging.info('Wrote... {}'.format(dest_dir))
        except Exception as e:
            logging.info('COULD NOT UNPACK TAR FILE')
            logging.info(e)

    
    def unzip(self, dest_dir):
        """ extract zip file 
        """
        try:
            self.tempf.seek(0)

            with zipfile.ZipFile(self.tempf) as zf:
                for i in zf.infolist():
                    if i.filename.startswith('..') is False and i.filename.startswith('/') is False:
                        zf.extract(i, path=str(dest_dir))
                        logging.info('Extracting.........{}'.format(i.filename))
                logging.info('Saved {}'.format(dest_dir))
        except Exception as e:
            logging.info('COULD NOT UNPACK ZIP FILE')
            logging.info(e)


    def save_as_text(self, dest_dir):
        dest_path = self.static_path.joinpath(dest_dir).joinpath(self.dep_path.name)

        with dest_path.open(mode='w') as fd:
            try:
                self.tempf.seek(0)
                fd.write(self.tempf.read().decode(self.encoding))
                logging.info('saved {}'.format(dest_path))
                return True
            except Exception as e:
                logging.info('FILE NOT SAVED!')
                logging.info(e)
                return False
    

    def get_file_type(self, dep_config):
        """ Determine filetype of source file by extension 
        """
        url = dep_config['URL']
        self.dep_path = Path(url)
        suff = self.dep_path.suffix

        if suff in self.text_types:
            return 'text'
        if suff == '.gz':
            return 'tar'
        if suff.endswith('.zip'):
            return 'zip'
