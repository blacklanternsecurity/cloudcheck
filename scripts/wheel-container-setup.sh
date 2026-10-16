# Sourced by maturin-action inside the manylinux and musllinux containers; vendored OpenSSL needs perl and make.
if command -v apk >/dev/null 2>&1; then
  apk add --no-cache perl make musl-dev
elif command -v yum >/dev/null 2>&1; then
  yum install -y perl-core make gcc
elif command -v apt-get >/dev/null 2>&1; then
  apt-get update && apt-get install -y perl make gcc
fi
