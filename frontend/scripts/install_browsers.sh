#!/usr/bin/env bash
set -e

# Install Playwright browser binaries
# Skip host requirement validation to avoid missing system packages in CI
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 npx playwright install
