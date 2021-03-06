
.. _internationalization:

====================
Internationalization
====================

In the file ``<package>.mk``, define the supported languages with (default):

.. code:: make

   LANGUAGES ?= en fr de

In the file ``vars.yaml``, define the default locale:

.. code:: yaml

   vars:
        ...
        default_locale_name: fr

In the file ``language_mapping``, define any desired locale variants, for example:

.. code:: make

   fr=fr-ch

Build your application.

The files to translate are:

* ``geoportal/<package>_geoportal/locale/<lang>/LC_MESSAGES/<package>-client.po`` for the ngeo client

.. note::

   All the ``#, fuzzy`` strings should be verified and the line should be removed
   (if the line is not removed, the localisation will not be used).

To update your ``po`` files, you should proceed as follows.

.. code:: bash

    make update-po

.. note::

   You should run this command when you change something in the following:

     * layer in mapfile (new or modified)
     * layer in administration (new or modified)
     * raster layer in the vars file (new or modified)
     * print template
     * full-text search
     * application (JavaScript and HTML files)
     * layer enumeration
     * some metadata as disclaimer
     * editable layer (database structure, data or enumerations)

.. note::

   In mapfiles, attributes added by mapserver substitution will not be collected
   for translation.

~~~~~~~~~~~~~~~~~~~~~~
Collect custom strings
~~~~~~~~~~~~~~~~~~~~~~

If the standard system can not collect some strings, you can add them manually in
one of your JavaScript application controllers:

.. code:: javascript

    /** @type {angular.gettext.gettextCatalog} */
    const gettextCatalog = $injector.get('gettextCatalog');
    gettextCatalog.getString('My previously not collected string');
