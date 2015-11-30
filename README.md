# requests-sspi-ntlm
HTTP NTLM authentication using SSPI module for requests library. Supporting complete the authorization without login information even username. In this case, current user will be used for authorization.

## Usage

```python
import requests
from requests_sspi_ntlm import HttpNtlmAuth

session = requests.Session()
session.auth = HttpNtlmAuth()
session.get("http://ntlm_protected_site.com")
```

## Installation

```
python setup.py install
```

## Requirements

* requests
* pywin32

## Reference

[requests-ntlm](https://github.com/requests/requests-ntlm)
