.. _templatetags:

.. highlight:: html+django

Require Media Template Tags
===========================

This document describes the template tags that Require Media offers.


``require``
-----------

Registers an external requirement with the current request context.

The tag is invoked with the following signature::

{% require [<group>] requirement [<depends> ...] %}

The optional ``group`` argument specifies a requirement group, such as
"css" or "js", the ``requirement`` argument specifies the desired
requirement, and all further arguments are interpreted as requirements
of the one currently being specified.

A simple example that causes ``jquery.js`` to be added to the list of
``js`` requirements for the current request::

    {% require js jquery.js %}

This more complicated example would add ``jquery-ui.js`` to the list of
``js`` requirements after ``jquery.js``::

    {% require js jquery-ui.js jquery.js %}


``require_inline``
------------------

Register a required inline asset, such as CSS or JavaScript.

There are two required arguments: ``name``, which is a name for the block,
and ``group``, which is a type identifier for the block.

All further arguments specify requirements the one being defined
depends upon.

A simple example::

    {% require_inline sidebar css %}

    #sidebar {
        color: #ff0;
    }

    {% end_require_inline %}

``render_requirements``
-----------------------

Renders required media assets for the current request context.

Accepts an optional positional argument to specify the asset group
to render.

The following example renders all CSS assets::

    {% render_requirements css %}

