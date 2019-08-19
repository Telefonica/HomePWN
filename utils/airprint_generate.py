# https://github.com/tjfontaine/airprint-generate/blob/master/airprint-generate.py

"""
Copyright (c) 2010 Timothy J Fontaine <tjfontaine@atxconsulting.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import urllib.parse as urlparse
import cups, os, optparse, re
import os.path
from io import StringIO

from xml.dom.minidom import parseString
from xml.dom import minidom

import sys

try:
    import lxml.etree as etree
    from lxml.etree import Element, ElementTree, tostring
except:
    try:
        from xml.etree.ElementTree import Element, ElementTree, tostring
        etree = None
    except:
        try:
            from elementtree import Element, ElementTree, tostring
            etree = None
        except:
            raise 'Failed to find python libxml or elementtree, please install one of those.'

XML_TEMPLATE = """<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
<name replace-wildcards="yes"></name>
<service>
	<type>_ipp._tcp</type>
	<subtype>_universal._sub._ipp._tcp</subtype>
	<port>631</port>
	<txt-record>txtvers=1</txt-record>
	<txt-record>qtotal=1</txt-record>
	<txt-record>Transparent=T</txt-record>
	<txt-record>URF=none</txt-record>
</service>
</service-group>"""

#TODO XXX FIXME
#<txt-record>ty=AirPrint Ricoh Aficio MP 6000</txt-record>
#<txt-record>Binary=T</txt-record>
#<txt-record>Duplex=T</txt-record>
#<txt-record>Copies=T</txt-record>


DOCUMENT_TYPES = {
    # These content-types will be at the front of the list
    'application/pdf': True,
    'application/postscript': True,
    'application/vnd.cups-raster': True,
    'application/octet-stream': True,
    'image/urf': True,
    'image/png': True,
    'image/tiff': True,
    'image/png': True,
    'image/jpeg': True,
    'image/gif': True,
    'text/plain': True,
    'text/html': True,

    # These content-types will never be reported
    'image/x-xwindowdump': False,
    'image/x-xpixmap': False,
    'image/x-xbitmap': False,
    'image/x-sun-raster': False,
    'image/x-sgi-rgb': False,
    'image/x-portable-pixmap': False,
    'image/x-portable-graymap': False,
    'image/x-portable-bitmap': False,
    'image/x-portable-anymap': False,
    'application/x-shell': False,
    'application/x-perl': False,
    'application/x-csource': False,
    'application/x-cshell': False,
}

class AirPrintGenerate(object):
    def __init__(self, host=None, user=None, port=None, verbose=False,
        directory=None, prefix='AirPrint-', adminurl=False):
        self.host = host
        self.user = user
        self.port = port
        self.verbose = verbose
        self.directory = directory
        self.prefix = prefix
        self.adminurl = adminurl
        
        if self.user:
            cups.setUser(self.user)
    
    def generate(self):
        if not self.host:
            conn = cups.Connection()
        else:
            if not self.port:
                self.port = 631
            conn = cups.Connection(self.host, self.port)
            
        printers = conn.getPrinters()
        
        for p, v in printers.items():
            if v['printer-is-shared']:
                attrs = conn.getPrinterAttributes(p)
                uri = urlparse.urlparse(v['printer-uri-supported'])

                tree = ElementTree()
                tree.parse(StringIO(XML_TEMPLATE.replace('\n', '').replace('\r', '').replace('\t', '')))

                name = tree.find('name')
                name.text = 'AirPrint %s @ %%h' % (p)

                service = tree.find('service')

                port = service.find('port')
                port_no = None
                if hasattr(uri, 'port'):
                  port_no = uri.port
                if not port_no:
                    port_no = self.port
                if not port_no:
                    port_no = cups.getPort()
                port.text = '%d' % port_no

                if hasattr(uri, 'path'):
                  rp = uri.path
                else:
                  rp = uri[2]
                
                re_match = re.match(r'^//(.*):(\d+)(/.*)', rp)
                if re_match:
                  rp = re_match.group(3)
                
                #Remove leading slashes from path
                #TODO XXX FIXME I'm worried this will match broken urlparse
                #results as well (for instance if they don't include a port)
                #the xml would be malform'd either way
                rp = re.sub(r'^/+', '', rp)
                
                path = Element('txt-record')
                path.text = 'rp=%s' % (rp)
                service.append(path)

                desc = Element('txt-record')
                desc.text = 'note=%s' % (v['printer-info'])
                service.append(desc)

                product = Element('txt-record')
                product.text = 'product=(GPL Ghostscript)'
                service.append(product)

                state = Element('txt-record')
                state.text = 'printer-state=%s' % (v['printer-state'])
                service.append(state)

                ptype = Element('txt-record')
                ptype.text = 'printer-type=%s' % (hex(v['printer-type']))
                service.append(ptype)

                pdl = Element('txt-record')
                fmts = []
                defer = []

                for a in attrs['document-format-supported']:
                    if a in DOCUMENT_TYPES:
                        if DOCUMENT_TYPES[a]:
                            fmts.append(a)
                    else:
                        defer.append(a)

                if 'image/urf' not in fmts:
                    sys.stderr.write('image/urf is not in mime types, %s may not be available on ios6 (see https://github.com/tjfontaine/airprint-generate/issues/5)%s' % (p, os.linesep))

                fmts = ','.join(fmts+defer)

                dropped = []

                # TODO XXX FIXME all fields should be checked for 255 limit
                while len('pdl=%s' % (fmts)) >= 255:
                    (fmts, drop) = fmts.rsplit(',', 1)
                    dropped.append(drop)

                if len(dropped) and self.verbose:
                    sys.stderr.write('%s Losing support for: %s%s' % (p, ','.join(dropped), os.linesep))

                pdl.text = 'pdl=%s' % (fmts)
                service.append(pdl)

                if self.adminurl:
                    admin = Element('txt-record')
                    admin.text = 'adminurl=%s' % (v['printer-uri-supported'])
                    service.append(admin)
                
                fname = '%s%s.service' % (self.prefix, p)
                
                if self.directory:
                    fname = os.path.join(self.directory, fname)
                
                f = open(fname, 'w')

                if etree:
                    tree.write(f, pretty_print=True, xml_declaration=True, encoding="UTF-8")
                else:
                    xmlstr = tostring(tree.getroot())
                    doc = parseString(xmlstr)
                    dt= minidom.getDOMImplementation('').createDocumentType('service-group', None, 'avahi-service.dtd')
                    doc.insertBefore(dt, doc.documentElement)
                    doc.writexml(f)
                f.close()
                
                if self.verbose:
                    sys.stderr.write('Created: %s%s' % (fname, os.linesep))