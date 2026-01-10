SMTP Email setup

1) Recommended: set environment variables (do NOT commit secrets):

- EMAIL_BACKEND=smtp
- DEFAULT_FROM_EMAIL=you@example.com
- EMAIL_HOST=smtp.gmail.com
- EMAIL_PORT=587
- EMAIL_HOST_USER=your-email@gmail.com
- EMAIL_HOST_PASSWORD=<your_app_password>
- EMAIL_USE_TLS=True
- EMAIL_USE_SSL=False

2) If using Gmail:
- Enable 2-Step Verification on your Google account.
- Create an App Password (Mail) and use it as `EMAIL_HOST_PASSWORD`.
- Do NOT use your regular account password.

3) Testing locally:
- With the above env vars set, Django will send via SMTP.
- To view messages instead in console, set `EMAIL_BACKEND=console`.

4) Example (Windows CMD):

setx EMAIL_BACKEND smtp
setx EMAIL_HOST_USER your-email@gmail.com
setx EMAIL_HOST_PASSWORD your_app_password
setx DEFAULT_FROM_EMAIL your-email@gmail.com
setx EMAIL_USE_TLS True

After setting env vars, restart the dev server.
