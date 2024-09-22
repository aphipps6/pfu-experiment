from flask import Flask
from jinja2 import Environment, FileSystemLoader
import os

def jinja_render(template_name, template_values):
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=True
    )
    template = env.get_template(template_name)
    return template.render(template_values)