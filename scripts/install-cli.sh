#!/usr/bin/env sh
# Lightweight installer for create-django-bolt Rust CLI binary
set -e

REPO="bmartel/django-lightning"
BIN_NAME="create-django-bolt"

# Determine install directory (prefer ~/.local/bin or /usr/local/bin)
if [ -d "$HOME/.local/bin" ] || mkdir -p "$HOME/.local/bin" 2>/dev/null; then
    INSTALL_DIR="$HOME/.local/bin"
elif [ -w "/usr/local/bin" ]; then
    INSTALL_DIR="/usr/local/bin"
else
    INSTALL_DIR="$HOME/bin"
    mkdir -p "$INSTALL_DIR"
fi

OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux)
        case "$ARCH" in
            x86_64) ASSET="create-django-bolt-linux-x86_64.tar.gz" ;;
            aarch64|arm64) ASSET="create-django-bolt-linux-arm64.tar.gz" ;;
            *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
        esac
        ;;
    Darwin)
        case "$ARCH" in
            x86_64) ASSET="create-django-bolt-macos-x86_64.tar.gz" ;;
            arm64) ASSET="create-django-bolt-macos-arm64.tar.gz" ;;
            *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
        esac
        ;;
    *)
        echo "Unsupported OS: $OS"
        exit 1
        ;;
esac

URL="https://github.com/${REPO}/releases/latest/download/${ASSET}"
TMP_DIR="$(mktemp -d)"

echo "⚡ Downloading create-django-bolt CLI from ${URL}..."
curl -fsSL "$URL" -o "${TMP_DIR}/cli.tar.gz"

tar -xzf "${TMP_DIR}/cli.tar.gz" -C "${TMP_DIR}"

mv "${TMP_DIR}/${BIN_NAME}" "${INSTALL_DIR}/${BIN_NAME}"
chmod +x "${INSTALL_DIR}/${BIN_NAME}"
rm -rf "$TMP_DIR"

echo "✨ Successfully installed ${BIN_NAME} to ${INSTALL_DIR}/${BIN_NAME}!"
echo "Run 'create-django-bolt new my-app' to get started."
