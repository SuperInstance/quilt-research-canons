#!/bin/bash
# Reproduces the quicunnel finding in §2 of the report.
#
# As shipped, SuperInstance/quicunnel does NOT compile:
#   Cargo.toml:36  rustls-pemfile = "2.2"
#   src/tls.rs    written against the rustls-pemfile 1.x API
#                (certs() -> Result<Vec<CertificateDer>>,
#                 rsa_private_keys() -> Result<Vec<Vec<u8>>>)
# In 2.x those return ITERATORS, so src/tls.rs produces
#   error[E0599]  no method named `map_err` ... at src/tls.rs:41
#   error[E0308]  mismatched types  at src/tls.rs:87, :90, :93
# and `cargo test` exits 101 with ZERO tests run.
#
# Because Cargo.lock is gitignored ("library crate convention"), CI always
# resolves the newest rustls-pemfile, so every `main` run has failed.
#
# This script proves the diagnosis by applying the one-line pin.
set -euo pipefail
REPO=${1:-/tmp/deep/quicunnel}
export HOME=/tmp/rust RUSTUP_HOME=/tmp/rust/.rustup CARGO_HOME=/tmp/rust/.cargo
export PATH=/tmp/rust/.cargo/bin:$PATH

cd "$REPO"
echo "=== AS SHIPPED ==="
grep -n 'rustls-pemfile' Cargo.toml
cargo test --all 2>&1 | grep -E "^(error|error\[)|could not compile|test result" | head -8 || true
echo "exit was: ${PIPESTATUS[0]}"

echo
echo "=== WITH THE ONE-LINE PIN ==="
cp Cargo.toml /tmp/Cargo.toml.quicunnel.bak
sed -i 's/^rustls-pemfile = "2.2"/rustls-pemfile = "1"/' Cargo.toml
grep -n 'rustls-pemfile' Cargo.toml
cargo test --all 2>&1 | grep -E "^(running|test result)|^error" | head -10 || true
cp /tmp/Cargo.toml.quicunnel.bak Cargo.toml
echo "(Cargo.toml restored)"
