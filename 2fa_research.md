# 2FA Integration Research

Several options exist for adding two-factor authentication to the project.

## TOTP Libraries
- **pyotp** – Small Python library for generating Time-based One-Time Passwords.
  - Supports RFC 6238 and works with Google Authenticator and similar apps.
  - Easy to integrate by storing a per-user secret and verifying the token on login.

## External Providers
- **Authy (Twilio)** – Provides APIs for SMS, voice or push-based 2FA.
  - Requires account with Twilio and network calls during authentication.
- **Duo Security** – Enterprise oriented 2FA service with Python SDK.
  - Handles push notifications and has user/device management features.

Using TOTP with `pyotp` is simple and does not require an external service, but
an external provider like Authy could offer additional channels such as SMS.
