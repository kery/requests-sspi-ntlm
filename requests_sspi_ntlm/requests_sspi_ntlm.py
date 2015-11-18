import sspi
import base64
from requests.auth import AuthBase

class HttpNtlmAuth(AuthBase):
    def __init__(self, username=None, password=None, domain=""):
        if username is None:
            import win32api
            self.username = win32api.GetUserName()
        else:
            self.username = username
        self.password = password
        self.domain = domain

    def do_ntlm_auth(self, resp_auth_hdr, req_auth_hdr, resp, kwargs):
        if hasattr(resp.request.body, "seek"):
            content_length = int(resp.request.headers.get("Content-Length", "0"))
            if content_length > 0:
                resp.request.body.seek(-content_length, 1)
            else:
                resp.request.body.seek(0, 0)

        # Consume content and release the original connection
        # to allow our new request to reuse the same one.
        resp.content
        resp.raw.release_conn()
        new_req = resp.request.copy()

        # Prepare authorization header for the new request.
        ca = sspi.ClientAuth("NTLM", auth_info=
                             (self.username, self.domain, self.password))
        _, data = ca.authorize(None)
        new_req.headers[req_auth_hdr] = "NTLM %s" % base64.b64encode(data[0].Buffer)

        # A streaming response breaks authentication.
        #
        # This can be fixed by not streaming this request, which is safe
        # because the returned resp3 will still have stream=True set if
        # specified in kwargs. In addition, we expect this request to give us a
        # challenge and not the real content, so the content will be short
        # anyway.
        kwargs_nostream = dict(kwargs, stream=False)
        resp2 = resp.connection.send(new_req, **kwargs_nostream)

        # Consume content and release the original connection
        # to allow our new request to reuse the same one.
        resp2.content
        resp2.raw.release_conn()
        new_req = resp2.request.copy()

        challenge = resp2.headers[resp_auth_hdr]
        challenge = filter(lambda s: s.startswith("NTLM "),
                           challenge.split(","))[0].strip().split()[1]
        challenge = base64.b64decode(challenge)

        # Build response of challenge
        _, data = ca.authorize(challenge)
        new_req.headers[req_auth_hdr] = "NTLM %s" % base64.b64encode(data[0].Buffer)

        resp3 = resp2.connection.send(new_req, **kwargs)

        # Update the history
        resp3.history.append(resp)
        resp3.history.append(resp2)

        return resp3

    def response_hook(self, resp, **kwargs):
        if resp.status_code == 401:
            www_authenticate = resp.headers.get("www-authenticate", "").upper()
            if "NTLM" in www_authenticate:
                return self.do_ntlm_auth("www-authenticate", "Authorization",
                                         resp, kwargs)
        elif resp.status_code == 407:
            proxy_authenticate = resp.headers.get("proxy-authenticate", "").upper()
            if "NTLM" in proxy_authenticate:
                return self.do_ntlm_auth("proxy-authenticate", "Proxy-authorization",
                                         resp, kwargs)
        return resp

    def __call__(self, req):
        # NTLM authentication requires multiple exchanges between the
        # client and server. The server and any intervening proxies
        # must support persistent connections to successfully complete
        # the authentication.
        req.headers["Connection"] = "Keep-Alive"

        req.register_hook("response", self.response_hook)
        return req
