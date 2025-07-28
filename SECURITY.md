# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in the Upstox Python Client, please follow these steps:

### 1. **DO NOT** create a public GitHub issue
Security vulnerabilities should be reported privately to avoid potential exploitation.

### 2. **Email us directly**
Send an email to `security@upstox.com` with the following information:

- **Subject**: `[SECURITY] Vulnerability in Upstox Python Client`
- **Description**: Detailed description of the vulnerability
- **Steps to reproduce**: Clear steps to reproduce the issue
- **Impact**: Potential impact of the vulnerability
- **Suggested fix**: If you have a suggested fix (optional)

### 3. **What to expect**
- You will receive an acknowledgment within 48 hours
- We will investigate the report and keep you updated
- If the vulnerability is confirmed, we will:
  - Create a fix
  - Release a security patch
  - Credit you in the release notes (if you wish)

### 4. **Responsible disclosure**
We follow responsible disclosure practices:
- We will not publicly disclose the vulnerability until a fix is ready
- We will work with you to coordinate the disclosure timeline
- We will credit you for finding the vulnerability (if you wish)

## Security Best Practices

### For Users

1. **Keep the library updated**: Always use the latest version
2. **Secure your API keys**: Never commit API keys to version control
3. **Use environment variables**: Store sensitive data in environment variables
4. **Validate inputs**: Always validate user inputs before passing to the API
5. **Handle errors properly**: Implement proper error handling in your applications

### For Contributors

1. **Follow secure coding practices**: Validate all inputs, use parameterized queries
2. **Review code for security issues**: Look for common vulnerabilities
3. **Test security scenarios**: Include security-focused tests
4. **Keep dependencies updated**: Regularly update dependencies for security patches

## Security Features

The Upstox Python Client includes several security features:

- **OAuth2 Authentication**: Secure token-based authentication
- **HTTPS Only**: All API calls use HTTPS
- **Token Validation**: Automatic token validation and refresh
- **Input Validation**: Comprehensive input validation
- **Error Handling**: Secure error handling without information leakage
- **Rate Limiting**: Built-in rate limiting to prevent abuse

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2) and will be clearly marked as security releases in the changelog.

## Contact

For security-related questions or concerns:
- Email: `security@upstox.com`
- GitHub: Create a private issue (for general security questions only)

## Acknowledgments

We thank all security researchers and contributors who help us maintain the security of this library. 