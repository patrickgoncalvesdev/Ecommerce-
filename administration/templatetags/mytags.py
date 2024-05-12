from django import template

register = template.Library()


@register.simple_tag
def add_query_params(request, **kwargs):
    """
    Takes a request and generates URL with given kwargs as query parameters
    e.g.
    1. {% add_query_params request key=value %} with request.path=='/ask/'
        => '/ask/?key=value'
    2. {% add_query_params request page=2 %} with request.path=='/ask/?key=value'
        => '/ask/?key=value&page=2'
    3. {% add_query_params request page=5 %} with request.path=='/ask/?page=2'
        => '/ask/?page=5'
    """
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    print(request.get_host())
    return request.build_absolute_uri("?" + updated.urlencode())


@register.simple_tag
def call_with_date_range_filter(obj, method_name, *args, **kwargs):
    method = getattr(obj, method_name)
    return method(
        filter={"created_at__date__range": [kwargs["start_date"], kwargs["end_date"]]}
    )
