.. c2cgeoportal documentation master file, created by
   sphinx-quickstart on Mon Nov 28 10:01:14 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

c2cgeoportal documentation
==========================

Content:

.. toctree::
   :maxdepth: 1

   administrator/index
   integrator/index
   developer/index

*Administrator* is the person who manages an application built with
c2cgeoportal. *Integrator* is the person who builds the c2cgeoportal
application, and does the initial setup. *Developer* is the person who
produces code for c2cgeoportal itself.

The c2cgeoportal project is composed of two software components: NGEO (a JS
library based on `OpenLayers <https://openlayers.org>`_ and
`AngularJS <https://angularjs.org/>`_), and c2cgeoportal, a Python library
for the Pyramid web framework. So c2cgeoportal applications are Pyramid
applications with user interfaces based on OpenLayers and AngularJS.

The `Demo <https://geomapfish-demo-${major_version.replace('.', '-')}.camptocamp.com/>`_
application shows a WebGIS built with c2cgeoportal.
The `Demo alternative UI <https://geomapfish-demo-${major_version.replace('.', '-')}.camptocamp.com/desktop_alt>`_ shows the same WebGIS with different user interface functionalities.
To test the editing functionality, you can use the username 'demo' with the password 'demo'.

The
`ngeo (client) documentation can be found here <https://camptocamp.github.io/ngeo/${major_version}/apidoc/>`_.
