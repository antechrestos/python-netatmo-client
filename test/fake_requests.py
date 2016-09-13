import httplib
import os
from json import loads


class MockResponse(object):
    def __init__(self, url, status_code, text, headers=None):
        self.status_code = status_code
        self.url = url
        self.text = text
        self.headers = dict()
        self.is_redirect = status_code == httplib.SEE_OTHER
        if headers is not None:
            self.headers.update(headers)

    def check_data(self, **kwargs):
        pass

    def json(self, **kwargs):
        return loads(self.text, **kwargs)

    def __iter__(self):
        for b in self.text:
            yield b


def mock_response(url, method_name, check_data, status_code, headers, *path_parts):
    if len(path_parts) > 0:
        file_name = path_parts[len(path_parts) - 1]
        extension_idx = file_name.rfind('.')
        binary_file = extension_idx >= 0 and file_name[extension_idx:] == '.bin'
        with(open(os.path.join(os.path.dirname(__file__), 'fixtures', *path_parts),
                  'rb' if binary_file else 'r')) as f:
            response = MockResponse(url=url,
                                    status_code=status_code,
                                    text=f.read(),
                                    headers=headers)
    else:
        response = MockResponse(url, status_code, '')
    if check_data is not None:
        response.check_data = check_data

    def invocation(invoked_url, **kwargs):
        if invoked_url != url:
            raise AssertionError('%s and %s does not match' % (url, invoked_url))
        response.check_data(**kwargs)
        return response

    invocation.__name__ = method_name
    return invocation
