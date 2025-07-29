# SLSA Configuration Directory

This directory contains the SLSA (Supply Chain Levels for Software Artifacts) configuration files for the RoboBackup Tool project.

## Directory Structure

```
.slsa/
├── README.md                    # This file
├── slsa-config.yaml            # Main SLSA configuration
├── build-attestation.yaml      # Build attestation template
├── security-policy.yaml        # Security policy configuration
└── verification.yaml           # Verification configuration
```

## Configuration Files

### `slsa-config.yaml`
Main SLSA configuration file that defines:
- Project information and version
- Build process configuration
- Security requirements and scans
- Provenance settings
- Verification requirements
- Release security gates
- Compliance frameworks (SLSA Level 2, OWASP, NIST)

### `build-attestation.yaml`
Template for build attestations that defines:
- SLSA provenance structure
- Build artifact definitions
- Security scan integration
- Dependency analysis integration
- Verification requirements

### `security-policy.yaml`
Security policy configuration that defines:
- Vulnerability management thresholds
- Dependency management rules
- Code security requirements
- Access control policies
- Compliance framework mappings
- Monitoring and reporting settings
- Incident response procedures

### `verification.yaml`
Verification configuration that defines:
- Provenance verification steps
- Artifact integrity checks
- Security scan verification
- Dependency analysis verification
- Compliance verification
- Verification tools and outputs

## SLSA Level 2 Compliance

This project implements SLSA Level 2 compliance, which includes:

### Build Process
- ✅ Tamper-resistant build process
- ✅ Security verification integration
- ✅ Provenance generation
- ✅ Artifact verification

### Security Verification
- ✅ Bandit static analysis
- ✅ Safety vulnerability scanning
- ✅ Semgrep advanced security scanning
- ✅ pip-audit dependency scanning

### Documentation
- ✅ Software Bill of Materials (SBOM)
- ✅ Security policy documentation
- ✅ Incident response procedures
- ✅ Compliance status reporting

## Usage

### Running SLSA Verification

```bash
# Verify SLSA compliance
slsa-verifier verify .slsa/slsa-config.yaml

# Generate SBOM
cyclonedx-py --format json --output sbom.json

# Run security scans
bandit -r . -f json -o bandit-report.json
safety check --json --output safety-report.json
```

### Configuration Updates

When updating SLSA configuration:

1. **Update `slsa-config.yaml`** for build process changes
2. **Update `security-policy.yaml`** for security requirement changes
3. **Update `verification.yaml`** for verification process changes
4. **Test changes** in development environment
5. **Update documentation** in `SECURITY.md`

## Integration with CI/CD

The SLSA configuration integrates with the GitHub Actions workflow:

- **Security scans** run on every commit
- **SBOM generation** occurs during build
- **Provenance generation** happens automatically
- **Verification** occurs before release

## Compliance Status

- **SLSA Level**: 2
- **OWASP Compliance**: Partial (2021 Top 10)
- **NIST Framework**: Partial (800-218)
- **Last Audit**: January 2024
- **Next Review**: April 2024

## Security Contacts

For SLSA-related questions:
- **Security Team**: security@example.com
- **SLSA Lead**: slsa-lead@example.com
- **Compliance**: compliance@example.com

## References

- [SLSA Framework](https://slsa.dev/)
- [In-toto Framework](https://in-toto.io/)
- [CycloneDX SBOM](https://cyclonedx.org/)
- [OWASP Top 10](https://owasp.org/Top10/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)