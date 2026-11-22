# Security & Code Signing Policy

## Code Signing

Free code signing is provided by [SignPath.io](https://signpath.io/), using a certificate issued by the [SignPath Foundation](https://signpath.org/).

## Build Integrity & Provenance

- All official release artifacts (`DownHubService.exe`, `DownHub_Installer.exe`, and `extension.zip`) are built exclusively from this public GitHub repository (`wipodev/downhub`) via automated **GitHub Actions** workflows.
- No manually compiled or unsigned local binaries are uploaded to official GitHub Releases.
- Third-party bundled runtimes (`yt-dlp.exe`, `ffmpeg.exe`, and `deno.exe`) are downloaded directly from their official upstream release channels during the automated CI build process.

## Team Roles & Approval Policy

- **Project Owner & Release Approver:** WipoDev (`@wipodev`) — sole maintainer with commit and release approval permissions.
- **External Contributors:** Pull requests are reviewed manually before merging into `main`. Automated signing is restricted strictly to protected release workflows triggered by repository tags.

## Privacy Policy

- **100% Local Execution:** DownHub runs entirely on the user's local machine.
- **Zero Telemetry:** DownHub does not collect, store, or transmit personal data, browsing history, download logs, or usage analytics to any external server.
- **Network Connections:** Outbound network requests occur solely to fetch requested media streams (`yt-dlp`) and check for official component updates on GitHub (`wipodev/downhub` and `yt-dlp/yt-dlp`).

## Reporting a Vulnerability

If you discover a security vulnerability in DownHub, please report it privately via [GitHub Security Advisories](https://github.com/wipodev/downhub/security/advisories) or open an issue without disclosing exploit details publicly until a patch is released.
