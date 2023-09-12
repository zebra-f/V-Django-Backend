from rest_framework.renderers import BrowsableAPIRenderer


class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):
    '''
    Custom renderer used for views that can't be handled by an HTML form.
    For example: list[str].
    '''
    
    def render_form_for_serializer(self, serializer):
        return ""