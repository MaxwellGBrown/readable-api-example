<%
  from readable_api.form import build_form
  from readable_api.resources.base import LeafResource
  import json

  def urlize(s):
    """Anchor found URLs."""
    parts = list(s.split("http://"))
    new_parts = list()
    for part in parts[1:]:
      end_idx = part.find('"')
      url = f"http://{part[:end_idx]}"
      new_part = f'<a href="{url}">{url}</a>{part[end_idx:]}'
      new_parts.append(new_part)
  
    parts[1:] = new_parts
    return "".join(parts) 

  # TODO These are part of their own things but rely on each other :(
  json_body = urlize(json.dumps(data, indent=4, default=str))
  content_length = len(json_body.encode())
%>
<html>
  <head>
    <link rel="icon" href="data:;base64,=">
  </head>
  <body>
    ${breadcrumb()}
    <h1>Readable API Example</h1>
    ${http_status()}
    ${response_headers()}
    ${response_body()}

    % if request.context.schema.get('type'):
      ${form(isinstance(request.context, LeafResource))}
    % endif
  </body>
</html>

<%def name="breadcrumb()">
  <%
    breadcrumbs = [request.context]
    this = request.context
    while this.__parent__ != None:
      breadcrumbs.insert(0, this.__parent__)
      this = this.__parent__
  %>
  <nav>
    % for resource in breadcrumbs:
      <a href="${request.resource_url(resource)}">${resource.__name__ if resource.__name__ else request.host}</a> /
    % endfor
  </nav>
</%def>

<%def name="http_status()">
  <h2>${request.response.status}</h2>
</%def>

<%def name="response_headers()">
  <h3>Response Headers</h3>
  <pre>
    % for header, value in request.response.headers.items():
      % if header.lower() == "content-length":
<b>${header}</b>: ${content_length}
      % else:
<b>${header}</b>: ${urlize(value) | n}
      % endif
    % endfor
  </pre>
</%def>

<%def name="response_body()">
  <h3>Response Body</h3>
  <pre id="response-body" style="max-height: 300px; overflow-y: scroll; border: solid black 2px;">
${json_body | n}
  </pre>
</%def>

<%def name="form(edit=False)">
  <%
     method = "POST" if not edit else "PUT"
     phrasing = f"Create New {request.context.__class__.__name__}" if not edit else f"Edit {request.context.__name__}"
  %>
  <h3>${phrasing}</h3>
  <form method="${method}" action="${request.resource_url(request.context)}">
    % for field in build_form(request.context):
      ${field.label} ${field()}
    % endfor
  </form>
</%def>
