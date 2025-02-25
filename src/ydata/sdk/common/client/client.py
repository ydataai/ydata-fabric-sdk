from contextlib import suppress
from os import environ
from typing import Dict, Optional, Union

from httpx import Client as httpClient
from httpx import HTTPStatusError, Response, Timeout
from httpx import codes as http_codes
from httpx._types import RequestContent
from typeguard import typechecked

from ydata.sdk.common.client.parser import LinkExtractor
from ydata.sdk.common.client.singleton import SingletonClient
from ydata.sdk.common.config import DEFAULT_URL, TOKEN_VAR
from ydata.sdk.common.exceptions import ClientHandshakeError, ResponseError
from ydata.sdk.common.types import Project

codes = http_codes

HELP_TEXT = f"""
Fabric SDK requires an account with a valid token.

In case you do not have an account, please contact YData at https://ydata.ai/contact-us.
To obtain the token, please, login to https://{environ.get("YDATA_BASE_URL", DEFAULT_URL)}.
The token is available on the homepage once you are connected.

The easiest way to have the client created is to define the token in an environment variable '{TOKEN_VAR}' as follows:\n\n\

    ```
    import os
    os.environ["{TOKEN_VAR}"] = <your_token>
    ```

See the documentation for further help: https://docs.fabric.ydata.ai/latest/sdk/
"""


@typechecked
class Client(metaclass=SingletonClient):
    """Main Client class used to abstract the connection to the backend.

    A normal user should not have to instanciate a [`Client`][ydata.sdk.common.client.Client] by itself.
    However, in the future it will be useful for power-users to manage projects and connections.

    Args:
        credentials (Optional[dict]): (optional) Credentials to connect
        project (Optional[Project]): (optional) Project to connect to. If not specified, the client will connect to the default user's project.
    """

    codes = codes

    DEFAULT_PROJECT: Optional[Project] = environ.get("DEFAULT_PROJECT", None)

    def __init__(self, credentials: Optional[Union[str, Dict]] = None, project: Optional[Project] = None, set_as_global: bool = False):
        self._base_url = environ.get("YDATA_BASE_URL", DEFAULT_URL).removesuffix('/')
        self._verify_ssl = bool(int(environ.get('YDATA_VERIFY_SSL', 1)))
        self._headers = {'Authorization': credentials}

        if self._verify_ssl is False:
            self._http_client = httpClient(
                headers=self._headers, timeout=Timeout(10, read=None), verify=self._verify_ssl)
        else:
            self._http_client = httpClient(
                headers=self._headers, timeout=Timeout(10, read=None))

        self._handshake()

        self._default_project = project or Client.DEFAULT_PROJECT or self._get_default_project(
            credentials)
        if set_as_global:
            self.__set_global()

    @property
    def project(self) -> Project:
        return Client.DEFAULT_PROJECT or self._default_project

    @project.setter
    def project(self, value: Project):
        self._default_project = value

    def post(
        self, endpoint: str, content: Optional[RequestContent] = None, data: Optional[Dict] = None,
        json: Optional[Dict] = None, project: Optional[Project] = None, files: Optional[Dict] = None,
        raise_for_status: bool = True
    ) -> Response:
        """POST request to the backend.

        Args:
            endpoint (str): POST endpoint
            content (Optional[RequestContent])
            data (Optional[dict]): (optional) multipart form data
            json (Optional[dict]): (optional) json data
            files (Optional[dict]): (optional) files to be sent
            raise_for_status (bool): raise an exception on error

        Returns:
            Response object
        """
        url_data = self.__build_url(
            endpoint, data=data, json=json, files=files, project=project)
        response = self._http_client.post(**url_data)

        if response.status_code != Client.codes.OK and raise_for_status:
            self.__raise_for_status(response)

        return response

    def patch(
        self, endpoint: str, content: Optional[RequestContent] = None, data: Optional[Dict] = None,
        json: Optional[Dict] = None, project: Optional[Project] = None, files: Optional[Dict] = None,
        raise_for_status: bool = True
    ) -> Response:
        """PATCH request to the backend.

        Args:
            endpoint (str): POST endpoint
            content (Optional[RequestContent])
            data (Optional[dict]): (optional) multipart form data
            json (Optional[dict]): (optional) json data
            files (Optional[dict]): (optional) files to be sent
            raise_for_status (bool): raise an exception on error

        Returns:
            Response object
        """
        url_data = self.__build_url(
            endpoint, data=data, json=json, files=files, project=project)
        response = self._http_client.patch(**url_data, content=content)

        if response.status_code != Client.codes.OK and raise_for_status:
            self.__raise_for_status(response)

        return response

    def get(
        self, endpoint: str, params: Optional[Dict] = None, project: Optional[Project] = None,
        cookies: Optional[Dict] = None, raise_for_status: bool = True
    ) -> Response:
        """GET request to the backend.

        Args:
            endpoint (str): GET endpoint
            cookies (Optional[dict]): (optional) cookies data
            raise_for_status (bool): raise an exception on error

        Returns:
            Response object
        """
        url_data = self.__build_url(endpoint, params=params,
                                    cookies=cookies, project=project)
        response = self._http_client.get(**url_data)

        if response.status_code != Client.codes.OK and raise_for_status:
            self.__raise_for_status(response)

        return response

    def get_static_file(
        self, endpoint: str, project: Optional[Project] = None, raise_for_status: bool = True
    ) -> Response:
        """Retrieve a static file from the backend.

        Args:
            endpoint (str): GET endpoint
            raise_for_status (bool): raise an exception on error

        Returns:
            Response object
        """
        from urllib.parse import urlparse
        url_data = self.__build_url(endpoint, project=project)
        url_parse = urlparse(self._base_url)
        url_data['url'] = f"""{
            url_parse.scheme}://{url_parse.netloc}/static-content{endpoint}"""
        response = self._http_client.get(**url_data)

        if response.status_code != Client.codes.OK and raise_for_status:
            self.__raise_for_status(response)

        return response

    def _handshake(self):
        """Client handshake.

        It is used to determine is the client can connect with its
        current authorization token.
        """
        response = self.get('/profiles', params={}, raise_for_status=False)
        if response.status_code == Client.codes.FOUND:
            parser = LinkExtractor()
            parser.feed(response.text)
            raise ClientHandshakeError(auth_link=parser.link)

    def _get_default_project(self, token: str):
        response = self.get('/profiles/me', params={}, cookies={'access_token': token})
        data: Dict = response.json()
        return data['myWorkspace']

    def __build_url(self, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None,
                    json: Optional[Dict] = None, project: Optional[Project] = None, files: Optional[Dict] = None,
                    cookies: Optional[Dict] = None) -> Dict:
        """Build a request for the backend.

        Args:
            endpoint (str): backend endpoint
            params (Optional[dict]): URL parameters
            data (Optional[Project]): (optional) multipart form data
            json (Optional[dict]): (optional) json data
            files (Optional[dict]): (optional) files to be sent
            cookies (Optional[dict]): (optional) cookies data

        Returns:
            dictionary containing the information to perform a request
        """
        _params = params if params is not None else {
            'ns': project or self._default_project
        }

        url_data = {
            'url': f"""{self._base_url}/{endpoint.removeprefix("/")}""",
            'headers': self._headers,
            'params': _params,
        }

        if data is not None:
            url_data['data'] = data

        if json is not None:
            url_data['json'] = json

        if files is not None:
            url_data['files'] = files

        if cookies is not None:
            url_data['cookies'] = cookies

        return url_data

    def __set_global(self) -> None:
        """Sets a client instance as global."""
        # If the client is stateful, close it gracefully!
        Client.GLOBAL_CLIENT = self

    def __raise_for_status(self, response: Response) -> None:
        """Raise an exception if the response is not OK.

        When an exception is raised, we try to convert it to a ResponseError which is
        a wrapper around a backend error. This usually gives enough context and provides
        nice error message.

        If it cannot be converted to ResponseError, it is re-raised.

        Args:
            response (Response): response to analyze
        """
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            with suppress(Exception):
                e = ResponseError(**response.json())
            raise e
