class RequestHeaderKey:
    CONTENT_TYPE = 'Content-type'
    ACCEPT = 'Accept'
    AUTHORIZATION = 'Authorization'


class RequestHeaderValue:
    APPLICATION_JSON = 'application/json'
    APPLICATION_CSV = 'application/csv'
    APPLICATION_ANY = '*/*'


class JwtKey:
    USER_TYPE = 'user_type'
    USER_ACCOUNT = 'user_account'
