def invite_view(backend_string, redirect):
    def index(request):
        backend = InviteBackend.load_backend_for(backend_string)
        form = backend.get_form(request)
        if form.is_valid():
            backend.process_form(request, form)
            return HttpResponseRedirect(redirect)
        return render_to_response([
            'invites/%s_selector.html',
            '%s_selector.html',
        ], { 'backend':backend, 'form':form })

def fulfill_view(request, invite_pk):
    invitation = get_object_or_404(Invitation, pk=int(invite_pk))
    if not request.user.logged_in:
        request.session[INVITATION_PK] = invitation.pk
        return HttpResponseRedirect(reverse('login')+'?next='+reverse(fulfill_view))
    else: 
        backend = InviteBackend.load_backend_for(invitation.backend)
        invitation = backend.attempt_to_fulfill(request.user, invitation)
        invitation.save()
        next = request.GET.get('next', '/dashboard/')
        return HttpResponseRedirect(next)
