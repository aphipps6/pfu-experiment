import jinja2
import os

def jinja_render(template_name, template_values):
    JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader((os.path.dirname(__file__), 'templates', 'static')),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True
    )
    template = JINJA_ENVIRONMENT.get_template(template_name)
    return template.render(template_values)
