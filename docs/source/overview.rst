.. _overview:

.. highlight:: html+django

Require Media Overview
======================

This document gives a brief overview of using Require Media in a Django
project.

Using Require Media in a Project
--------------------------------

Once the Require Media package is installed you can enable its use in your
Django project by  adding ``require_media`` to your ``INSTALLED_APPS`` and
adding ``'django.core.context_processors.request'`` to your
``TEMPLATE_CONTEXT_PROCESSORS`` setting. Doing so allows you to use the
template tags provided by Require Media by loading the ``require_media_tags``
library in your templates.

Declaring Requirements in Templates
-----------------------------------

In order to declare a static media requirement in a template, you must load the
``require_media_tags`` library in each template where you will declare a
requirement like so::

    {% load require_media_tags %}

After the library is loaded, you may declare dependencies with the ``require``
or ``require_inline`` template tags.

Using the ``require`` Template Tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's consider a simple example. Suppose you've written a template for
displaying user messages in a jQuery UI modal dialog. Your template looks
something like::

    {% if messages %}
    <ul id="user-messages">
        {% for message in messages %}
        <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
        {% endfor %}
    </ul>
    <script>
    $("#user-messages").dialog({modal: true});    
    </script>
    {% endif %}

This template obviously requires that the jQuery and jQuery UI JavaScript
libraries, and perhaps some extra CSS stylesheets be included in the ``HEAD``
element of the final document. This presents problems if we want to use the
``include`` tag to load this template only if the user has messages to display.

Wouldn't it be wonderful if we could specify in this messages template that it
requires ``jquery.js``, ``jquery-ui.js`` and ``jquery-ui.css`` and load these
libraries in the rendered document's ``HEAD`` or elsewhere?

We're in luck! The ``require`` tag allows us to specify these requirements so
that we can render them wherever is most appropriate. So let's modify our
template to use it::
    
    {% load require_media_tags %}
    {% require js jquery.js %}
    {% require js jquery-ui.js jquery.js %}
    {% require css jquery-ui.css %}
    {% if messages %}
    <ul id="user-messages">
        {% for message in messages %}
        <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
        {% endfor %}
    </ul>
    <script>
    $("#user-messages").dialog({modal: true});    
    </script>
    {% endif %}

Now these external static requirements have been registered with our
requirements registry and are ready to be rendered wherever we want.

Let's take a look at what this tag actually does. The first argument specifies
a "requirements group" name. This is the name that we can use to group
requirements to let the library know how to render these items. For instance,
``"js"`` is a natural name to use to group JavaScript requirements to let the
library know these requirements should be rendered as ``SCRIPT`` tags. In fact
this is what happens in the default set-up: dependencies ending in ``.js``
are grouped under the name ``"js"`` and rendered as ``SCRIPT`` tags, and
requirements ending in ``.css`` are grouped under the name ``"css"`` and
rendered as ``LINK`` tags.

The second argument specified the requirement URL. By default if this is given
as a fully qualified URL, then it is rendered as-is, otherwise it is rendered
relative to the location specified by ``MEDIA_URL`` in your settings.

The remaining arguments specifies any dependencies the requirement being
declared has. In the example, we know that ``jquery-ui.js`` depends upon
``jquery.js``, so we declare that dependency so that these requirements will be
rendered in the correct order.


Rendering Requirements with the ``render_requirements`` Template Tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have the requirements declared, let's make sure they get rendered
in our base template::

    {% load require_media_tags %}
    <html>
      <head>
        <title>{% block title %}{% endblock %}</title>
        {% render_requirements css %}
        {% render_requirements js %}
      </head>
      <body>
        {% include "messages.html" %}
      </body>
    </html>

Assuming our ``MEDIA_URL`` is ``"/media/"``, this will result in the following
being rendered::

    <html>
      <head>
        <title>...</title>
        <link rel="stylesheet" type="text/css" href="/media/jquery-ui.css">
        <script src="/media/js/jquery.js"></script>
        <script src="/media/js/jquery-ui.js"></script>
      </head>
      <body>
        ...
      </body>
    </html>

In fact, we can change the order of how these requirements are declared and
as long as their dependencies are specified they will be rendered in the
correct order. 

.. admonition:: Important

    The ``render_requirements`` tag should only appear in a base template.
    This ensures all declared requirements get registered before the
    ``render_requirements`` is forced to return output.


Using the ``require_inline`` Template Tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's say we want to improve the rendering speed of our page by moving the
``SCRIPT`` tags to the bottom of our document. To do this we need a way to
render our inline JavaScript after ``jquery.js`` is loaded. The
``require_inline`` tag allows us to do just this. Let's use it in our
``messages.html`` template::

    {% load require_media_tags %}
    {% require js jquery.js %}
    {% require js jquery-ui.js jquery.js %}
    {% require css jquery-ui.css %}

    <ul id="user-messages">
        {% for message in messages %}
        <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
        {% endfor %}
    </ul>

    {% require_inline messages_dialog js jquery-ui.js %}
    $("#user-messages").dialog({modal: true});    
    {% end_require_inline %}

Let's examine this ``require_inline`` block. The first argument to the start
tag specifies a name for the requirement that can be used as a ``depends``
argument for other requirement declarations. The second argument specifies
the requirement group, and the remaining arguments specify dependencies
this block has, as in the ``require`` declarations.

Now let's rework our ``base.html`` template to render these requirements in
the appropriate places::

    {% load require_media_tags %}
    <html>
      <head>
        <title>{% block title %}{% endblock %}</title>
        {% render_requirements css %}
      </head>
      <body>
        {% if messages %}
          {% include "messages.html" %}
        {% endif %}

        {% block content %}{% endblock %}        

        {% render_requirements js %}
      </body>
    </html>

Suppose some view renders a template that extends this template and the user
has a ``SUCCESS`` message. The rendered template would then look something
like::

    <html>
      <head>
        <title>...</title>
        <link rel="stylesheet" type="text/css" href="/media/jquery-ui.css">
      </head>
      <body>
        <ul id="user-messages">
          <li class="success">Successfully rendered requirements!</li>
        </ul>
        ...
        <script src="/media/js/jquery.js"></script>
        <script src="/media/js/jquery-ui.js"></script>
        <script>$("#user-messages").dialog({modal: true});</script>
      </body>
    </html>

The user should be greeted by a modal dialog telling him/her that our
requirements were successfully rendered!

What Now?
---------

For further usage information see the :ref:`API documentation <api>` and the
:ref:`template tag documentation<templatetags>`.
