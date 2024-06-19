def add_authorization_header(id_token: str, headers: dict | None) -> dict:
    auth_header = {"Authorization": f"Bearer {id_token}"}
    if headers is not None:
        headers.update(auth_header)
        return headers
    return auth_header
