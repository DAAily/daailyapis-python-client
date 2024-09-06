# USER CREDENTIALS ENV KEYS
DAAILY_USER_EMAIL_ENV = "DAAILY_USER_EMAIL"
DAAILY_USER_UID_ENV = "DAAILY_USER_UID"
DAAILY_USER_API_KEY_ENV = "DAAILY_USER_API_KEY"

# ENV KEY ERROR MESSAGE
MISSING_ENV_USER_CREDENTIALS_MESSAGE = (
    "User credentials should be set via the environment."
)

# SALLY URL & ENDPOINTS
SALLY_BASE_URL = "https://sally.daaily.com/api/v3"
REFRESH_ENDPOINT = "tokens/get-token-with-refresh-token"
TOKEN_ENDPOINT = "tokens/get-token"

# TOKEN REFRESHING
REFRESH_THRESHOLD_SECS = 30
MISSING_REFRESH_TOKEN_MESSAGE = (
    "Required refresh token should be set within the Sally client."
)
