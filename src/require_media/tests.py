from django.utils import unittest, importlib
from django.test import TestCase as DjangoTestCase
from django.test.client import RequestFactory
from django.conf import settings as project_settings
from django.core.exceptions import MiddlewareNotUsed
from django import template

from require_media.conf import settings
from require_media import manager
from require_media import renderers
from require_media import utils

request_factory = RequestFactory()

class RequirementTestCase(unittest.TestCase):
    def test_initialization(self):
        requirement = manager.Requirement("jquery.js")
        self.assertEquals("jquery.js", requirement.name)
        self.assertFalse(requirement.group)
        self.assertEquals([], requirement.depends_on)

        self.assertFalse(requirement.is_inline())

        requirement = manager.Requirement("jquery.js", "js")
        self.assertEquals("jquery.js", requirement.name)
        self.assertEquals("js", requirement.group)
        self.assertEquals([], requirement.depends_on)

        self.assertFalse(requirement.is_inline())

        requirement = manager.Requirement("jquery-ui.js", "js", ["jquery.js"])
        self.assertEquals("jquery-ui.js", requirement.name)
        self.assertEquals("js", requirement.group)
        self.assertEquals(["jquery.js"], requirement.depends_on)

        self.assertFalse(requirement.is_inline())

    def test_is_qualified_url(self):
        requirement = manager.Requirement("jquery.js")
        self.assertFalse(requirement.is_qualified_url())
        
        requirement = manager.Requirement("this is a test")
        self.assertFalse(requirement.is_qualified_url())
        
        requirement = manager.Requirement("example.com/url/example.js")
        self.assertFalse(requirement.is_qualified_url())

        requirement = manager.Requirement("http://example.com/url/example.js")
        self.assertTrue(requirement.is_qualified_url())


class InlineRequirementTestCase(unittest.TestCase):
    def test_initialization(self):
        requirement = manager.InlineRequirement("test", "var foo = null;")
        self.assertEquals("test", requirement.name)
        self.assertEquals("var foo = null;", requirement.content)
        self.assertFalse(requirement.group)
        self.assertEquals([], requirement.depends_on)

        self.assertTrue(requirement.is_inline())

        requirement = manager.InlineRequirement("test", "var foo = null;", "js")
        self.assertEquals("test", requirement.name)
        self.assertEquals("var foo = null;", requirement.content)
        self.assertEquals("js", requirement.group)
        self.assertEquals([], requirement.depends_on)

        self.assertTrue(requirement.is_inline())

        requirement = manager.InlineRequirement("test", "var foo = null;", "js", ["jquery.js"])
        self.assertEquals("test", requirement.name)
        self.assertEquals("var foo = null;", requirement.content)
        self.assertEquals("js", requirement.group)
        self.assertEquals(["jquery.js"], requirement.depends_on)

        self.assertTrue(requirement.is_inline())

    def test_is_qualified_url(self):
        requirement = manager.InlineRequirement("test", "var foo = null;")
        self.assertFalse(requirement.is_qualified_url())

        requirement = manager.InlineRequirement("jquery.js", "var foo = null;")
        self.assertFalse(requirement.is_qualified_url())

        requirement = manager.InlineRequirement("http://example.com/url/example.js", "var foo = null;")
        self.assertFalse(requirement.is_qualified_url())


class RequirementManagerTestCase(unittest.TestCase):
    def test_determine_requirement_group(self):
        groups = ["css", "js"]
        self.assertEquals("js", utils.determine_requirement_group("jquery.js", groups))
        self.assertEquals("js", utils.determine_requirement_group("http://example.com/url/example.js", groups))
        self.assertEquals("js", utils.determine_requirement_group("http://example.com/url/example.js?query=string&example", groups))
        self.assertEquals(None, utils.determine_requirement_group("var a = null;", groups))
        self.assertEquals("css", utils.determine_requirement_group("reset.css", groups))
        self.assertEquals("css", utils.determine_requirement_group("http://example.com/css/reset.css", groups))
        self.assertEquals("css", utils.determine_requirement_group("http://example.com/css/reset.css?query=string&example", groups))
        self.assertEquals(None, utils.determine_requirement_group("h1 { background: #fff; }", groups))

    def test_add_external_group(self):
        requirement_manager = manager.RequirementManager()
        requirement_manager.add_external("jquery.js", "cool")
        requirements = requirement_manager.requirements
        self.assertEquals(1, len(requirements))
        requirement = requirements[0]
        self.assertTrue(isinstance(requirement, manager.Requirement))
        self.assertEquals("jquery.js", requirement.name)
        self.assertEquals("cool", requirement.group)
        self.assertEquals(0, len(requirement.depends_on))

    def test_add_external_depends(self):
        requirement_manager = manager.RequirementManager()
        requirement_manager.add_external("jquery-ui.js", "js", ["jquery.js"])
        requirements = requirement_manager.requirements
        self.assertEquals(1, len(requirements))
        requirement = requirements[0]
        self.assertTrue(isinstance(requirement, manager.Requirement))
        self.assertEquals("jquery-ui.js", requirement.name)
        self.assertEquals("js", requirement.group)
        self.assertEquals(1, len(requirement.depends_on))
        self.assertEquals("jquery.js", requirement.depends_on[0])

    def test_add_inline(self):
        requirement_manager = manager.RequirementManager()
        requirement_manager.add_inline("foo", "a { color: #a0a; }", "css")
        requirements = requirement_manager.requirements
        self.assertEquals(1, len(requirements))
        requirement = requirements[0]
        self.assertTrue(isinstance(requirement, manager.InlineRequirement))
        self.assertEquals("foo", requirement.name)
        self.assertEquals("a { color: #a0a; }", requirement.content)
        self.assertEquals("css", requirement.group)
        self.assertEquals(0, len(requirement.depends_on))

    def test_sort_requirements(self):
        m = manager.RequirementManager()
        m.add_external("jquery.ui.accordion.js", depends_on=["jquery.ui.core.js", "jquery.effects.scale.js"])
        m.add_external("jquery.effects.scale.js", depends_on=["jquery.js", "jquery.effects.core.js"])
        m.add_external("jquery.ui.core.js", depends_on=["jquery.js"])
        m.add_external("jquery.js")
        m.add_external("jquery.effects.core.js", depends_on=["jquery.js"])
        ordered = m.get_sorted_requirements()
        names = [requirement.name for requirement in ordered]
        should_be = ["jquery.js", "jquery.ui.core.js", "jquery.effects.core.js", "jquery.effects.scale.js", "jquery.ui.accordion.js"]
        self.assertEquals(should_be, names)


class RequirementRendererTestCase(unittest.TestCase):
    def test_get_renderer(self):
        renderer = renderers.get_renderer("js")
        self.assertTrue(renderer)
        self.assertEquals(renderers.javascript_requirement_renderer, renderer)

        renderer = renderers.get_renderer("css")
        self.assertTrue(renderer)
        self.assertEquals(renderers.css_requirement_renderer, renderer)

        renderer = renderers.get_renderer("vbscript")
        self.assertEquals(None, renderer)


class RequestMiddlewareTestCase(DjangoTestCase):
    def get_request(self):
        request = request_factory.get("/")
        self.apply_middleware(request)
        return request

    def get_middleware(self):
        request_middleware = []
        for middleware_path in project_settings.MIDDLEWARE_CLASSES:
            try:
                dot = middleware_path.rindex(".")
                mw_module, mw_classname = middleware_path[:dot], middleware_path[dot+1:]
                mod = importlib.import_module(mw_module)
                mw_class = getattr(mod, mw_classname)
                mw_instance = mw_class()
                if hasattr(mw_instance, "process_request"):
                    request_middleware.append(mw_instance.process_request)
            except (ValueError, ImportError, AttributeError, MiddlewareNotUsed):
                continue
        return request_middleware

    def apply_middleware(self, request):
        request_middleware = self.get_middleware()
        for middleware in request_middleware:
            middleware(request)


class RequireMediaMiddlewareTestCase(RequestMiddlewareTestCase):
    def test_middleware_does_not_error(self):
        response = self.client.get("/example1/")
        self.assertEquals(200, response.status_code)

    def test_middleware_adds_manager(self):
        request = self.get_request()
        requirement_manager = getattr(request, settings.REQUEST_ATTR_NAME, None)
        self.assertTrue(requirement_manager)
        self.assertTrue(isinstance(requirement_manager, manager.RequirementManager))


class RequireTagTestCase(RequestMiddlewareTestCase):
    def test_simple_with_group(self):
        request = self.get_request()
        t = template.Template("{% load require_media_tags %}{% require js jquery.js %}")
        rendered = t.render(template.RequestContext(request))
        self.assertEquals("", rendered)
        requirement_manager = getattr(request, settings.REQUEST_ATTR_NAME, None)
        self.assertEquals(1, len(requirement_manager.requirements))
        self.assertTrue("jquery.js" in requirement_manager.graph)
        self.assertEquals("js", requirement_manager.requirements[0].group)

    def test_simple_no_group(self):
        request = self.get_request()
        t = template.Template("{% load require_media_tags %}{% require jquery.js %}")
        rendered = t.render(template.RequestContext(request))
        self.assertEquals("", rendered)
        requirement_manager = getattr(request, settings.REQUEST_ATTR_NAME, None)
        self.assertEquals(1, len(requirement_manager.requirements))
        self.assertTrue("jquery.js" in requirement_manager.graph)
        self.assertEquals("js", requirement_manager.requirements[0].group)

    def test_no_args(self):
        self.assertRaises(template.TemplateSyntaxError, template.Template, "{% load require_media_tags %}{% require %}")
        
    def test_group_only(self):
        self.assertRaises(template.TemplateSyntaxError, template.Template, "{% load require_media_tags %}{% require js %}")

    def test_depends_simple(self):
        request = self.get_request()
        t = template.Template("{% load require_media_tags %}{% require jquery-ui.js jquery.js %}")
        rendered = t.render(template.RequestContext(request))
        self.assertEquals("", rendered)
        requirement_manager = getattr(request, settings.REQUEST_ATTR_NAME, None)
        self.assertEquals(1, len(requirement_manager.requirements))
        self.assertTrue("jquery-ui.js" in requirement_manager.graph)
        self.assertEquals("js", requirement_manager.requirements[0].group)
        self.assertEquals(1, len(requirement_manager.requirements[0].depends_on))
        self.assertEquals("jquery.js", requirement_manager.requirements[0].depends_on[0])

    def test_requirement_alias(self):
        request = self.get_request()
        t = template.Template("{% load require_media_tags %}{% require jquery.min.js %}")
        rendered = t.render(template.RequestContext(request))
        self.assertEquals("", rendered)
        requirement_manager = getattr(request, settings.REQUEST_ATTR_NAME, None)
        self.assertEquals(1, len(requirement_manager.requirements))
        self.assertTrue("jquery.js" in requirement_manager.graph)
        self.assertEquals("js", requirement_manager.requirements[0].group)
        self.assertEquals(0, len(requirement_manager.requirements[0].depends_on))

    def test_requirement_group_alias(self):
        request = self.get_request()
        t = template.Template("{% load require_media_tags %}{% require jquery jquery.min.js %}")
        rendered = t.render(template.RequestContext(request))
        self.assertEquals("", rendered)
        requirement_manager = getattr(request, settings.REQUEST_ATTR_NAME, None)
        self.assertEquals(1, len(requirement_manager.requirements))
        self.assertTrue("jquery.js" in requirement_manager.graph)
        self.assertEquals("js", requirement_manager.requirements[0].group)
        self.assertEquals(0, len(requirement_manager.requirements[0].depends_on))


class RequireInlineTagTestCase(RequestMiddlewareTestCase):
    def test_simple(self):
        request = self.get_request()
        t = template.Template("{% load require_media_tags %}{% require_inline sidebar css %}#sidebar { float: left; }{% end_require_inline %}")
        rendered = t.render(template.RequestContext(request))
        self.assertEquals(u"", rendered)
        requirement_manager = getattr(request, settings.REQUEST_ATTR_NAME, None)
        self.assertEquals(1, len(requirement_manager.requirements))
        requirement = requirement_manager.requirements[0]
        self.assertEquals("sidebar", requirement.name)
        self.assertEquals("css", requirement.group)
        self.assertEquals("#sidebar { float: left; }", requirement.content[0].render(None))
        self.assertEquals(0, len(requirement.depends_on))

    def test_depends(self):
        request = self.get_request()
        t = template.Template(u'{% load require_media_tags %}{% require_inline sidebar js jquery.js %}$("#sidebar").hide();{% end_require_inline %}')
        rendered = t.render(template.RequestContext(request))
        self.assertEquals(u"", rendered)
        requirement_manager = getattr(request, settings.REQUEST_ATTR_NAME, None)
        self.assertEquals(1, len(requirement_manager.requirements))
        requirement = requirement_manager.requirements[0]
        self.assertEquals("sidebar", requirement.name)
        self.assertEquals("js", requirement.group)
        self.assertEquals(u'$("#sidebar").hide();', requirement.content[0].render(None))
        self.assertEquals(1, len(requirement.depends_on))
        self.assertEquals("jquery.js", requirement.depends_on[0])

    def test_no_args(self):
        self.assertRaises(template.TemplateSyntaxError, template.Template, "{% load require_media_tags %}{% require_inline %}")

    def test_no_group(self):
        self.assertRaises(template.TemplateSyntaxError, template.Template, "{% load require_media_tags %}{% require_inline foo %}")

    def test_no_end(self):
        self.assertRaises(template.TemplateSyntaxError, template.Template, "{% load require_media_tags %}{% require_inline foo js %}")


class RenderRequirementsTagTestCase(RequestMiddlewareTestCase):
    def test_simple(self):
        request = self.get_request()
        t = template.Template("{% load require_media_tags %}{% require jquery-ui.js jquery.js jquery-ui.css %}{% require jquery-ui.css %}{% require jquery.js %}{% render_requirements css %}{% render_requirements js %}")
        rendered = t.render(template.RequestContext(request))
        self.assertEquals(u'<link rel="stylesheet" type="text/css" href="/media/css/jquery-ui.css"><script src="/media/js/jquery.js"></script><script src="/media/js/jquery-ui.js"></script>', rendered)
    
    def test_render_no_request(self):
        t = template.Template("{% load require_media_tags %}{% require jquery-ui.js jquery.js jquery-ui.css %}{% require jquery-ui.css %}{% require jquery.js %}{% render_requirements css %}{% render_requirements js %}")
        rendered = t.render(template.Context({}))
        self.assertEquals(u'', rendered)

    def test_render_no_group(self):
        request = self.get_request()
        t = template.Template("{% load require_media_tags %}{% require jquery-ui.js jquery.js jquery-ui.css %}{% require jquery-ui.css %}{% require jquery.js %}{% render_requirements %}")
        rendered = t.render(template.RequestContext(request))
        expected = u'<script src="/media/js/jquery.js"></script><link rel="stylesheet" type="text/css" href="/media/css/jquery-ui.css"><script src="/media/js/jquery-ui.js"></script>'
        self.assertEquals(expected, rendered)
        
    def test_render_before_require(self):
        request = self.get_request()
        t = template.Template("{% load require_media_tags %}{% render_requirements css %}{% render_requirements js %}{% require jquery-ui.js jquery.js jquery-ui.css %}{% require jquery-ui.css %}{% require jquery.js %}")
        rendered = t.render(template.RequestContext(request))
        self.assertEquals(u'<link rel="stylesheet" type="text/css" href="/media/css/jquery-ui.css"><script src="/media/js/jquery.js"></script><script src="/media/js/jquery-ui.js"></script>', rendered)

    def test_render_unknown_group(self):
        request = self.get_request()
        t = template.Template("{% load require_media_tags %}{% require jquery-ui.js jquery.js jquery-ui.css %}{% require jquery-ui.css %}{% require jquery.js %}{% render_requirements js_head %}")
        rendered = t.render(template.RequestContext(request))
        self.assertEquals(u"", rendered)

    def test_render_inline_simple(self):
        request = self.get_request()
        t = template.Template(u'{% load require_media_tags %}{% require_inline sidebar js %}$("#sidebar").hide();{% end_require_inline %}{% render_requirements js %}')
        rendered = t.render(template.RequestContext(request))
        self.assertEquals(u'<script>$("#sidebar").hide();</script>', rendered)

    def test_render_inline_no_request(self):
        request = self.get_request()
        t = template.Template(u'{% load require_media_tags %}{% require_inline sidebar js %}$("#sidebar").hide();{% end_require_inline %}{% render_requirements js %}')
        rendered = t.render(template.Context({}))
        self.assertEquals(u'', rendered)

    def test_render_inline_before_require(self):
        request = self.get_request()
        t = template.Template(u'{% load require_media_tags %}{% render_requirements js %}{% require_inline sidebar js %}$("#sidebar").hide();{% end_require_inline %}')
        rendered = t.render(template.RequestContext(request))
        self.assertEquals(u'<script>$("#sidebar").hide();</script>', rendered)
        
    def test_render_qualified_url(self):
        request = self.get_request()
        t = template.Template(u'{% load require_media_tags %}{% require http://openlayers.org/api/OpenLayers.js %}{% render_requirements js %}')
        rendered = t.render(template.RequestContext(request))
        self.assertEquals(u'<script src="http://openlayers.org/api/OpenLayers.js"></script>', rendered)

    def test_render_multiple_groups(self):
        request = self.get_request()
        t = template.Template(u'{% load require_media_tags %}{% require http://openlayers.org/api/OpenLayers.js %}{% require css layout.css %}{% render_requirements js css %}')
        rendered = t.render(template.RequestContext(request))
        self.assertEquals(u'<script src="http://openlayers.org/api/OpenLayers.js"></script><link rel="stylesheet" type="text/css" href="/media/css/layout.css">', rendered)
