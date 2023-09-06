import json


class TransportException(Exception):
    """Base class for all transport exceptions."""

    def __init__(self, resp, content, uri=None):
        self.resp = resp
        if not isinstance(content, bytes):
            raise TypeError("HTTP content should be bytes")
        self.content = content
        self.uri = uri
        self.error_details = ""
        # self.reason = self._get_reason()

    @property
    def status_code(self):
        """Return the HTTP status code from the response content."""
        return self.resp.status

    def _get_reason(self):
        """Calculate the reason for the error from the response content."""
        reason = None
        try:
            try:
                data = json.loads(self.content.decode("utf-8"))
            except json.JSONDecodeError:
                # In case it is not json
                data = self.content.decode("utf-8")
            if isinstance(data, dict):
                reason = data["error"]["message"]
                error_detail_keyword = next(
                    (
                        kw
                        for kw in ["detail", "details", "errors", "message"]
                        if kw in data["error"]
                    ),
                    "",
                )
                if error_detail_keyword:
                    self.error_details = data["error"][error_detail_keyword]
            elif isinstance(data, list) and len(data) > 0:
                first_error = data[0]
                reason = first_error["error"]["message"]
                if "details" in first_error["error"]:
                    self.error_details = first_error["error"]["details"]
            else:
                self.error_details = data
        except (ValueError, KeyError, TypeError):
            pass
        if reason is None:
            reason = ""
        return reason.strip()

    # def __repr__(self):
    #     if self.error_details:
    #        return '<HttpError %s when requesting %s returned "%s". Details: "%s">' % (
    #             self.resp.status,
    #             self.uri,
    #             self.reason,
    #             self.error_details,
    #         )
    #     elif self.uri:
    #         return '<HttpError %s when requesting %s returned "%s">' % (
    #             self.resp.status,
    #             self.uri,
    #             self.reason,
    #         )
    #     else:
    #         return '<HttpError %s "%s">' % (self.resp.status, self.reason)

    # __str__ = __repr__
