
class InviteBackendException(Exception):
    pass

class InviteBackend(object):
    def fulfill_invite(self, invitation):
        pass

    def get_form(self, request):
        pass

    def process_form(self, request, form):
        pass

    @classmethod
    def load_backend_for(invitation):
        get_module_and_target = lambda x: x.rsplit('.', 1)
        module, target = get_module_and_target(invitation.backend)
        module = import_module(module)
        target = getattr(module, target)
        return target()
