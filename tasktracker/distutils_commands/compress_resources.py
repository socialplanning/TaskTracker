from distutils.cmd import Command
from distutils.errors import *
from distutils import log
import pkg_resources
import os
import glob
import random
import mimetypes
import urllib2
import urllib

class compress_resources(Command):
    description = 'Compress Javascript and CSS files into smaller/combined forms'
    user_options = [
        ('resource-dirs=', 'r', 'Relative directory where resources are located'),
        ('resource-files=', None, 'Filenames to include (in order they should be included)'),
        ('combined-name=', None, 'Names of combined files'),
        ('extensions=', None, 'Extensions to compress (default .js and .css)'),
        ('compress-js', None, 'Compress Javascript using ShrinkSafe'),
        ]
    boolean_options = ['compress-js']

    shrinksafe_url = 'http://alex.dojotoolkit.org/shrinksafe/shrinksafe.php'

    def initialize_options(self):
        self.resource_dirs = []
        self.resource_files = []
        self.extensions = ['.js', '.css']
        self.combined_name = 'combined'
        self.compress_js = False
        
    def finalize_options(self):
        if (isinstance(self.resource_files, basestring)
            and len(self.resource_files.splitlines()) > 1):
            log.debug('Splitting resource_files by line')
            self.resource_files = [
                line.strip() for line in self.resource_files.splitlines()
                if line.strip()]
        else:
            self.ensure_string_list('resource_files')
        self.ensure_string_list('resource_dirs')
        self.ensure_string_list('extensions')
        self.ensure_string('combined_name')
        
    def run(self):
        for dir in self.resource_dirs:
            for ext in self.extensions:
                self.compress_dir(dir, ext)
    
    comment_styles = {
        '.js': '/* From %(filename)s: */',
        '.css': '/* From %(filename)s: */',
        }
    
    def compress_dir(self, dir, ext):
        filenames = []
        for name in self.resource_files:
            if name.startswith('#'):
                continue
            if not os.path.splitext(name)[1]:
                name += ext
            if not name.endswith(ext):
                continue
            globbed = glob.glob(os.path.join(dir, name))
            globbed.sort()
            filenames.extend(globbed)
        if not filenames:
            return
        combined_fn = self.combined_name + ext
        combined_fn = os.path.join(dir, combined_fn)
        if combined_fn in filenames:
            filenames.remove(combined_fn)
        content = []
        for fn in filenames:
            comment = self.comment_styles[ext] % {'filename': fn}
            content.append(comment + '\n\n')
            f = open(fn, 'rb')
            content.append(f.read())
            f.close()
            content.append('\n\n\n\n')
        content = ''.join(content)
        need_write = True
        if os.path.exists(combined_fn):
            f = open(combined_fn, 'rb')
            existing = f.read()
            f.close()
            if content == existing:
                status = 'no change'
                need_write = False
            else:
                status = 'content changed'
        else:
            status = 'created'
        if need_write:
            f = open(combined_fn, 'wb')
            f.write(content)
            f.close()
        log.info('%s: %iKb (%s)' % (combined_fn, len(content)/1024, status))
        if self.compress_js and ext == '.js':
            compress_fn = os.path.join(dir, 'compressed.js')
            if (not os.path.exists(compress_fn)
                or os.path.getmtime(compress_fn) < os.path.getmtime(combined_fn)):
                compress_js = self.compress_javascript(content)
                f = open(compress_fn, 'wb')
                f.write(compress_js)
                f.close()
                log.info('%s: compressed to %iKb (%i%%)',
                         compress_fn, len(compress_js)/1024,
                         100*len(compress_js)/len(content))
            else:
                log.debug('%s: skipping recreation (seems up-to-date)' % compress_fn)

    def compress_javascript(self, content):
        result = self.submit_file_upload(
            self.shrinksafe_url,
            {'stripnewlines': '1',
             'shrinkfile[]': ('content.js', content)})
        return result
        
    http_boundary = '----' + str(random.random()) + str(random.random())
        
    def submit_file_upload(self, url, fields):
        content_type, body = self._encode_data(fields)
        req = urllib2.Request(url)
        req.add_header('Content-Type', content_type)
        req.add_data(body)
        res = urllib2.urlopen(req)
        return res.read()

    def _encode_data(self, fields):
        data = []
        for fieldname, value in fields.items():
            data.append('--' + self.http_boundary)
            header = 'Content-Disposition: form-data; name="%s"' % fieldname
            if isinstance(value, tuple):
                header += '; filename="%s"' % value[0]
            data.append(header)
            if isinstance(value, tuple):
                data.append('Content-Type: %s' % self._get_content_type(value[0]))
                value = value[1]
            data.append('')
            data.append(value)
        data.append('--' + self.http_boundary)
        data.append('')
        body = '\r\n'.join(data)
        content_type = 'multipart/form-data; boundary=%s' % self.http_boundary
        return content_type, body
    
    def _get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

                
        