def convert_to_http_cookie(list_cookie: list[str]) -> str:
    cookie: str = ''
    for line in list_cookie:
        values = line.split('\t')
        if any(x in value for x in ['/'] for value in [values[-1], values[-2]]):
            continue
        cookie = cookie + f'{values[-2]}={values[-1]}; '
    return cookie