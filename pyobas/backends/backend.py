import dataclasses
import json
from typing import TYPE_CHECKING, Any, BinaryIO, Dict, Optional, Union

import requests
from requests import PreparedRequest
from requests.auth import AuthBase
from requests.structures import CaseInsensitiveDict
from requests_toolbelt.multipart.encoder import MultipartEncoder  # type: ignore

from pyobas.backends import protocol


class Auth:
    def __init__(self, token: str):
        self.token = token


class TokenAuth(Auth, AuthBase):
    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


@dataclasses.dataclass
class SendData:
    content_type: str
    data: Optional[Union[Dict[str, Any], MultipartEncoder]] = None
    json: Optional[Union[Dict[str, Any], bytes]] = None

    def __post_init__(self) -> None:
        if self.json is not None and self.data is not None:
            raise ValueError(
                f"`json` and `data` are mutually exclusive. Only one can be set. "
                f"json={self.json!r}  data={self.data!r}"
            )


class RequestsResponse(protocol.BackendResponse):
    def __init__(self, response: requests.Response) -> None:
        self._response: requests.Response = response

    @property
    def response(self) -> requests.Response:
        return self._response

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def headers(self) -> CaseInsensitiveDict[str]:
        return self._response.headers

    @property
    def content(self) -> bytes:
        return self._response.content

    @property
    def reason(self) -> str:
        return self._response.reason

    def json(self) -> Any:
        return self._response.json()


class RequestsBackend(protocol.Backend):
    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self._client: requests.Session = session or requests.Session()

    @property
    def client(self) -> requests.Session:
        return self._client

    @staticmethod
    def prepare_send_data(
        files: Optional[Dict[str, Any]] = None,
        post_data: Optional[Union[Dict[str, Any], bytes, BinaryIO]] = None,
        raw: bool = False,
    ) -> SendData:
        if files is not None:
            json_data = {"input": (None, json.dumps(post_data), "application/json")}
            post_data = {**files, **json_data}
            multipart_encoder = MultipartEncoder(fields=post_data)
            return SendData(
                data=multipart_encoder, content_type=multipart_encoder.content_type
            )

        if raw and post_data:
            return SendData(data=post_data, content_type="application/octet-stream")

        if TYPE_CHECKING:
            assert not isinstance(post_data, BinaryIO)

        return SendData(json=post_data, content_type="application/json")

    def http_request(
        self,
        method: str,
        url: str,
        json: Optional[Union[Dict[str, Any], bytes]] = None,
        data: Optional[Union[Dict[str, Any], MultipartEncoder]] = None,
        params: Optional[Any] = None,
        timeout: Optional[float] = None,
        verify: Optional[Union[bool, str]] = True,
        stream: Optional[bool] = False,
        **kwargs: Any,
    ) -> RequestsResponse:
        """Make HTTP request

        Args:
            method: The HTTP method to call ('get', 'post', 'put', 'delete', etc.)
            url: The full URL
            data: The data to send to the server in the body of the request
            json: Data to send in the body in json by default
            timeout: The timeout, in seconds, for the request
            verify: Whether SSL certificates should be validated. If
                the value is a string, it is the path to a CA file used for
                certificate validation.
            stream: Whether the data should be streamed

        Returns:
            A requests Response object.
        """
        response: requests.Response = self._client.request(
            method=method,
            url=url,
            params=params,
            data=data,
            timeout=timeout,
            stream=stream,
            verify=verify,
            json=json,
            **kwargs,
        )
        return RequestsResponse(response=response)
