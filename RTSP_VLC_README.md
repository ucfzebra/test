# RTSP to VLC Remote Stream

Command-line utilities for pushing an RTSP stream to a VLC instance via its HTTP remote interface.

## Quick Start

### One-Liner Command

The simplest way to push the stream using curl:

```bash
# Without password
curl -k "https://192.168.1.43:41827/requests/status.xml?command=in_play&input=rtsp%3A%2F%2F192.168.1.178%3A7447%2FazFOoNFmvnePjaWb"

# With password (replace 'yourpassword')
curl -k -u :yourpassword "https://192.168.1.43:41827/requests/status.xml?command=in_play&input=rtsp%3A%2F%2F192.168.1.178%3A7447%2FazFOoNFmvnePjaWb"
```

### Using the Bash Script

For a more robust solution with error handling and options:

```bash
# Make the script executable
chmod +x rtsp-to-vlc.sh

# Run with default settings
./rtsp-to-vlc.sh

# Run with password
./rtsp-to-vlc.sh -P yourpassword

# Run with custom RTSP URL
./rtsp-to-vlc.sh -r rtsp://camera.local:554/stream

# Check VLC connection
./rtsp-to-vlc.sh --check
```

## Prerequisites

### 1. VLC Setup

Enable the HTTP interface in VLC:

**Option A: Command Line**
```bash
# Start VLC with HTTP interface enabled
vlc --extraintf http --http-host 0.0.0.0 --http-port 41827 --http-password yourpassword
```

**Option B: VLC GUI**
1. Open VLC
2. Go to Tools → Preferences
3. Show settings: All
4. Navigate to Interface → Main interfaces
5. Check "Web" or "HTTP"
6. Navigate to Interface → Main interfaces → Lua
7. Set HTTP password
8. Set host to 0.0.0.0 (to allow remote connections)
9. Set port to 41827
10. Restart VLC

### 2. System Requirements

- `curl` - for HTTP requests
- `jq` (optional) - for URL encoding in the script

Install on Debian/Ubuntu:
```bash
sudo apt-get install curl jq
```

Install on macOS:
```bash
brew install curl jq
```

## Script Options

```
Usage: ./rtsp-to-vlc.sh [OPTIONS]

OPTIONS:
    -h, --help              Show help message
    -r, --rtsp URL          RTSP stream URL
    -H, --host HOST         VLC host address (default: 192.168.1.43)
    -p, --port PORT         VLC port (default: 41827)
    -P, --password PASS     VLC HTTP password
    -s, --scheme SCHEME     URL scheme: http or https (default: https)
    -c, --check             Only check VLC connection status
```

## Environment Variables

You can also configure using environment variables:

```bash
export RTSP_URL="rtsp://192.168.1.178:7447/azFOoNFmvnePjaWb"
export VLC_HOST="192.168.1.43"
export VLC_PORT="41827"
export VLC_PASSWORD="yourpassword"
export VLC_SCHEME="https"

./rtsp-to-vlc.sh
```

## Advanced Usage

### Using ffmpeg to Re-stream

If you need more control over the streaming process, you can use ffmpeg to re-stream:

```bash
# Re-stream RTSP to VLC via HTTP
ffmpeg -i rtsp://192.168.1.178:7447/azFOoNFmvnePjaWb \
       -c copy \
       -f mpegts \
       http://192.168.1.43:41827/stream.ts
```

### Using VLC Command Line Directly

You can also use VLC's command-line interface to stream:

```bash
# On the VLC machine (192.168.1.43)
cvlc rtsp://192.168.1.178:7447/azFOoNFmvnePjaWb \
     --sout '#standard{access=http,mux=ts,dst=:8080}' \
     --no-sout-display
```

### Python Alternative

For a Python-based solution:

```python
import requests
from urllib.parse import quote

rtsp_url = "rtsp://192.168.1.178:7447/azFOoNFmvnePjaWb"
vlc_url = "https://192.168.1.43:41827"
password = "yourpassword"  # or None if no password

encoded_rtsp = quote(rtsp_url, safe='')
command_url = f"{vlc_url}/requests/status.xml?command=in_play&input={encoded_rtsp}"

# Send request
response = requests.get(
    command_url,
    auth=('', password) if password else None,
    verify=False  # Skip SSL verification for local network
)

if response.status_code == 200:
    print("Stream sent successfully")
else:
    print(f"Error: {response.status_code}")
```

## Troubleshooting

### Connection Refused

- Ensure VLC is running on the target machine
- Check that the HTTP interface is enabled
- Verify firewall settings allow connections on port 41827

### 401 Unauthorized

- Check that the password is correct
- Ensure VLC's HTTP interface has a password set

### SSL Certificate Errors

The `-k` flag in curl ignores SSL certificate verification. For production use, consider:
- Using `http://` instead of `https://`
- Setting up proper SSL certificates
- Using a VPN for secure connections

### Stream Not Playing

- Verify the RTSP URL is accessible: `vlc rtsp://192.168.1.178:7447/azFOoNFmvnePjaWb`
- Check VLC logs for errors
- Try using a different stream format or codec

## VLC HTTP API Commands

Other useful commands you can send to VLC:

```bash
# Get status
curl -k "https://192.168.1.43:41827/requests/status.xml"

# Play/Pause
curl -k "https://192.168.1.43:41827/requests/status.xml?command=pl_pause"

# Stop
curl -k "https://192.168.1.43:41827/requests/status.xml?command=pl_stop"

# Volume up
curl -k "https://192.168.1.43:41827/requests/status.xml?command=volume&val=+20"

# Volume down
curl -k "https://192.168.1.43:41827/requests/status.xml?command=volume&val=-20"

# Fullscreen
curl -k "https://192.168.1.43:41827/requests/status.xml?command=fullscreen"

# Clear playlist
curl -k "https://192.168.1.43:41827/requests/status.xml?command=pl_empty"
```

## Security Notes

- The examples use `-k` flag to skip SSL certificate verification
- For production use, implement proper SSL/TLS
- Consider using VPN for remote access
- Use strong passwords for VLC HTTP interface
- Limit access to trusted networks only

## License

MIT License - see main repository LICENSE file
