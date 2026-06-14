Category: verification
* The email contains a verification code, one-time password (OTP), sign-in code, email verification link, or account activation link.
* If the email's primary purpose is to warn the user about a security event, suspicious activity, unusual login, account issue, transaction alert, or other important event requiring attention, classify it as "reminder", even if it contains a password reset link, verification link, or other action links.
* If a verification code or verification link is found, extract it into the `content` field.
* If neither is found, set `content` to `null`.
EXAMPLE JSON OUTPUT:
{"type":"verification", "content":"123456"}
{"type":"verification", "content":"https://abc.com/verify"}
{"type":"verification","content":null}
