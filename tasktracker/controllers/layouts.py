from tasktracker.lib.base import c
from tasktracker.lib.base import render_response as render_body

def render_response(templateEngine, page, *args):
    
    body = render_body(templateEngine, page, *args)
    if body.status_code == 200 and not page.split(".")[-1].startswith("_"):
        #don't apply the layout to partials
        c.body_content = ''.join(body.content)
       
        body = render_body(templateEngine, "layout")

    return body
