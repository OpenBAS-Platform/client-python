from typing import TYPE_CHECKING, Any, BinaryIO, Dict, List, Optional, Union
from urllib import parse

import requests

from pyobas import exceptions, utils
from pyobas._version import __version__  # noqa: F401

REDIRECT_MSG = (
    "pyobas detected a {status_code} ({reason!r}) redirection. You must update "
    "your OpenBVAS URL to the correct URL to avoid issues. The redirection was from: "
    "{source!r} to {target!r}"
)


class OpenBAS:
    def __init__(
        self,
        url: str,
        token: str,
        timeout: Optional[float] = None,
        per_page: Optional[int] = None,
        pagination: Optional[str] = None,
        order_by: Optional[str] = None,
        ssl_verify: Union[bool, str] = True,
        **kwargs: Any,
    ) -> None:

        if url is None or len(url) == 0:
            raise ValueError("An URL must be set")
        if token is None or len(token) == 0 or token == "ChangeMe":
            raise ValueError("A TOKEN must be set")

        self.url = url
        self.timeout = timeout
        #: Headers that will be used in request to OpenBAS
        self.headers = {
            "User-Agent": "pyobas/" + __version__,
            "Authorization": "Bearer " + token,
        }
        #: Whether SSL certificates should be validated
        self.ssl_verify = ssl_verify

        # Import backends
        from pyobas import backends

        self.backend = backends.RequestsBackend(**kwargs)
        self._auth = backends.TokenAuth(token)
        self.session = self.backend.client

        self.per_page = per_page
        self.pagination = pagination
        self.order_by = order_by

        # Import all apis
        from pyobas import apis

        self.me = apis.MeManager(self)
        self.organization = apis.OrganizationManager(self)
        self.injector = apis.InjectorManager(self)
        self.collector = apis.CollectorManager(self)
        self.inject = apis.InjectManager(self)
        self.document = apis.DocumentManager(self)
        self.kill_chain_phase = apis.KillChainPhaseManager(self)
        self.attack_pattern = apis.AttackPatternManager(self)
        self.team = apis.TeamManager(self)
        self.endpoint = apis.EndpointManager(self)
        self.user = apis.UserManager(self)
        self.inject_expectation = apis.InjectExpectationManager(self)
        self.payload = apis.PayloadManager(self)
        self.security_platform = apis.SecurityPlatformManager(self)

    @staticmethod
    def _check_redirects(result: requests.Response) -> None:
        # Check the requests history to detect 301/302 redirections.
        # If the initial verb is POST or PUT, the redirected request will use a
        # GET request, leading to unwanted behaviour.
        # If we detect a redirection with a POST or a PUT request, we
        # raise an exception with a useful error message.
        if not result.history:
            return

        for item in result.history:
            if item.status_code not in (301, 302):
                continue
            # GET methods can be redirected without issue
            if item.request.method == "GET":
                continue
            target = item.headers.get("location")
            raise exceptions.RedirectError(
                REDIRECT_MSG.format(
                    status_code=item.status_code,
                    reason=item.reason,
                    source=item.url,
                    target=target,
                )
            )

    def _build_url(self, path: str) -> str:
        """Returns the full url from path.

        If path is already a url, return it unchanged. If it's a path, append
        it to the stored url.

        Returns:
            The full URL
        """
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.url}/api{path}"

    def _get_session_opts(self) -> Dict[str, Any]:
        return {
            "headers": self.headers.copy(),
            "auth": self._auth,
            "timeout": self.timeout,
            "verify": self.ssl_verify,
        }

    def http_request(
        self,
        verb: str,
        path: str,
        query_data: Optional[Dict[str, Any]] = None,
        post_data: Optional[Union[Dict[str, Any], bytes, BinaryIO]] = None,
        raw: bool = False,
        streamed: bool = False,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Make an HTTP request to the OpenBAS server.

        Args:
            verb: The HTTP method to call ('get', 'post', 'put', 'delete')
            path: Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            query_data: Data to send as query parameters
            post_data: Data to send in the body (will be converted to
                              json by default)
            raw: If True, do not convert post_data to json
            streamed: Whether the data should be streamed
            files: The files to send to the server
            timeout: The timeout, in seconds, for the request
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            A requests result object.

        Raises:
            OpenBASHttpError: When the return code is not 2xx
        """
        query_data = query_data or {}
        raw_url = self._build_url(path)

        # parse user-provided URL params to ensure we don't add our own duplicates
        parsed = parse.urlparse(raw_url)
        params = parse.parse_qs(parsed.query)
        utils.copy_dict(src=query_data, dest=params)

        url = parse.urlunparse(parsed._replace(query=""))

        if "query_parameters" in kwargs:
            utils.copy_dict(src=kwargs["query_parameters"], dest=params)
            for arg in ("per_page", "page"):
                if arg in kwargs:
                    params[arg] = kwargs[arg]
        else:
            utils.copy_dict(src=kwargs, dest=params)

        opts = self._get_session_opts()

        verify = opts.pop("verify")
        opts_timeout = opts.pop("timeout")
        # If timeout was passed into kwargs, allow it to override the default
        if timeout is None:
            timeout = opts_timeout

        # We need to deal with json vs. data when uploading files
        send_data = self.backend.prepare_send_data(files, post_data, raw)
        opts["headers"]["Content-type"] = send_data.content_type

        # cur_retries = 0
        while True:
            # noinspection PyTypeChecker
            result = self.backend.http_request(
                method=verb,
                url=url,
                json=send_data.json,
                data=send_data.data,
                params=params,
                timeout=timeout,
                verify=verify,
                stream=streamed,
                **opts,
            )

            self._check_redirects(result.response)

            if 200 <= result.status_code < 300:
                return result.response

            error_message = result.content
            try:
                error_json = result.json()
                for k in ("message", "error"):
                    if k in error_json:
                        error_message = error_json[k]
            except (KeyError, ValueError, TypeError):
                pass

            if result.status_code == 401:
                raise exceptions.OpenBASAuthenticationError(
                    response_code=result.status_code,
                    error_message=error_message,
                    response_body=result.content,
                )

            raise exceptions.OpenBASHttpError(
                response_code=result.status_code,
                error_message=error_message,
                response_body=result.content,
            )

    def http_get(
        self,
        path: str,
        query_data: Optional[Dict[str, Any]] = None,
        streamed: bool = False,
        raw: bool = False,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], requests.Response]:
        query_data = query_data or {}
        result = self.http_request(
            "get", path, query_data=query_data, streamed=streamed, **kwargs
        )
        content_type = utils.get_content_type(result.headers.get("Content-Type"))

        if content_type == "application/json" and not streamed and not raw:
            try:
                json_result = result.json()
                return json_result
            except Exception as e:
                raise exceptions.OpenBASParsingError(
                    error_message="Failed to parse the server message"
                ) from e
        else:
            return result

    def http_head(
        self, path: str, query_data: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> "requests.structures.CaseInsensitiveDict[Any]":
        query_data = query_data or {}
        result = self.http_request("head", path, query_data=query_data, **kwargs)
        return result.headers

    def http_post(
        self,
        path: str,
        query_data: Optional[Dict[str, Any]] = None,
        post_data: Optional[Dict[str, Any]] = None,
        raw: bool = False,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], requests.Response]:
        query_data = query_data or {}
        post_data = post_data or {}
        result = self.http_request(
            "post",
            path,
            query_data=query_data,
            post_data=post_data,
            files=files,
            raw=raw,
            **kwargs,
        )
        content_type = utils.get_content_type(result.headers.get("Content-Type"))

        try:
            if content_type == "application/json":
                json_result = result.json()
                return json_result
        except Exception as e:
            raise exceptions.OpenBASParsingError(
                error_message="Failed to parse the server message"
            ) from e
        return result

    def http_put(
        self,
        path: str,
        query_data: Optional[Dict[str, Any]] = None,
        post_data: Optional[Union[Dict[str, Any], bytes, BinaryIO]] = None,
        raw: bool = False,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], requests.Response]:
        query_data = query_data or {}
        post_data = post_data or {}
        result = self.http_request(
            "put",
            path,
            query_data=query_data,
            post_data=post_data,
            files=files,
            raw=raw,
            **kwargs,
        )
        try:
            json_result = result.json()
            if TYPE_CHECKING:
                assert isinstance(json_result, dict)
            return json_result
        except Exception as e:
            raise exceptions.OpenBASParsingError(
                error_message="Failed to parse the server message"
            ) from e

    def http_patch(
        self,
        path: str,
        *,
        query_data: Optional[Dict[str, Any]] = None,
        post_data: Optional[Union[Dict[str, Any], bytes]] = None,
        raw: bool = False,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], requests.Response]:
        query_data = query_data or {}
        post_data = post_data or {}

        result = self.http_request(
            "patch",
            path,
            query_data=query_data,
            post_data=post_data,
            raw=raw,
            **kwargs,
        )
        try:
            json_result = result.json()
            if TYPE_CHECKING:
                assert isinstance(json_result, dict)
            return json_result
        except Exception as e:
            raise exceptions.OpenBASParsingError(
                error_message="Failed to parse the server message"
            ) from e

    def http_delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.http_request("delete", path, **kwargs)

    def http_list(
        self,
        path: str,
        query_data: Optional[Dict[str, Any]] = None,
        *,
        iterator: Optional[bool] = None,
        **kwargs: Any,
    ) -> Union["OpenBASList", List[Dict[str, Any]]]:
        query_data = query_data or {}

        url = self._build_url(path)

        page = kwargs.get("page")

        if iterator and page is None:
            # Generator requested
            return OpenBASList(self, url, query_data, **kwargs)

        # pagination requested, we return a list
        bas_list = OpenBASList(self, url, query_data, get_next=False, **kwargs)
        items = list(bas_list)
        return items


class OpenBASList:
    """Generator representing a list of remote objects.

    The object handles the links returned by a query to the API, and will call
    the API again when needed.
    """

    def __init__(
        self,
        openbas: OpenBAS,
        url: str,
        query_data: Dict[str, Any],
        get_next: bool = True,
        **kwargs: Any,
    ) -> None:
        self._openbas = openbas

        # Preserve kwargs for subsequent queries
        self._kwargs = kwargs.copy()

        self._query(url, query_data, **self._kwargs)
        self._get_next = get_next

        # Remove query_parameters from kwargs, which are saved via the `next` URL
        self._kwargs.pop("query_parameters", None)

    def _query(
        self, url: str, query_data: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> None:
        query_data = query_data or {}
        result = self._openbas.http_request("get", url, query_data=query_data, **kwargs)
        try:
            next_url = result.links["next"]["url"]
        except KeyError:
            next_url = None

        self._next_url = next_url
        self._current_page: Optional[str] = result.headers.get("X-Page")
        self._prev_page: Optional[str] = result.headers.get("X-Prev-Page")
        self._next_page: Optional[str] = result.headers.get("X-Next-Page")
        self._per_page: Optional[str] = result.headers.get("X-Per-Page")
        self._total_pages: Optional[str] = result.headers.get("X-Total-Pages")
        self._total: Optional[str] = result.headers.get("X-Total")

        try:
            self._data: List[Dict[str, Any]] = result.json()
        except Exception as e:
            raise exceptions.OpenBASParsingError(
                error_message="Failed to parse the server message"
            ) from e

        self._current = 0

    @property
    def current_page(self) -> int:
        """The current page number."""
        if TYPE_CHECKING:
            assert self._current_page is not None
        return int(self._current_page)

    @property
    def prev_page(self) -> Optional[int]:
        """The previous page number.

        If None, the current page is the first.
        """
        return int(self._prev_page) if self._prev_page else None

    @property
    def next_page(self) -> Optional[int]:
        """The next page number.

        If None, the current page is the last.
        """
        return int(self._next_page) if self._next_page else None

    @property
    def per_page(self) -> Optional[int]:
        """The number of items per page."""
        return int(self._per_page) if self._per_page is not None else None

    @property
    def total_pages(self) -> Optional[int]:
        """The total number of pages."""
        if self._total_pages is not None:
            return int(self._total_pages)
        return None

    @property
    def total(self) -> Optional[int]:
        """The total number of items."""
        if self._total is not None:
            return int(self._total)
        return None

    def __iter__(self) -> "OpenBASList":
        return self

    def __len__(self) -> int:
        if self._total is None:
            return 0
        return int(self._total)

    def __next__(self) -> Dict[str, Any]:
        return self.next()

    def next(self) -> Dict[str, Any]:
        try:
            item = self._data[self._current]
            self._current += 1
            return item
        except IndexError:
            pass

        if self._next_url and self._get_next is True:
            self._query(self._next_url, **self._kwargs)
            return self.next()

        raise StopIteration
