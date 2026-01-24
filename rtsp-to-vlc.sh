#!/bin/bash

# RTSP to VLC Remote Stream Script
# Pushes an RTSP stream to a VLC instance via HTTP remote interface

# Configuration
RTSP_URL="${RTSP_URL:-rtsp://192.168.1.178:7447/azFOoNFmvnePjaWb}"
VLC_HOST="${VLC_HOST:-192.168.1.43}"
VLC_PORT="${VLC_PORT:-41827}"
VLC_PASSWORD="${VLC_PASSWORD:-}"  # Set VLC password if required
VLC_SCHEME="${VLC_SCHEME:-https}"

# Build VLC base URL
VLC_BASE_URL="${VLC_SCHEME}://${VLC_HOST}:${VLC_PORT}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to send command to VLC
vlc_command() {
    local command="$1"
    local auth_flag=""

    # Add authentication if password is set
    if [ -n "$VLC_PASSWORD" ]; then
        auth_flag="-u :${VLC_PASSWORD}"
    fi

    # Send command to VLC (ignore SSL certificate verification for local network)
    curl -k -s $auth_flag "${VLC_BASE_URL}/requests/${command}" 2>&1
}

# Function to play stream
play_stream() {
    local stream_url="$1"
    print_info "Sending stream to VLC: $stream_url"

    # URL encode the stream URL
    local encoded_url=$(printf %s "$stream_url" | jq -sRr @uri)

    # Add to playlist and play
    local result=$(vlc_command "status.xml?command=in_play&input=${encoded_url}")

    if [ $? -eq 0 ]; then
        print_info "Stream command sent successfully"
        return 0
    else
        print_error "Failed to send stream command"
        print_error "$result"
        return 1
    fi
}

# Function to check VLC status
check_vlc_status() {
    print_info "Checking VLC connection..."

    local result=$(vlc_command "status.xml" 2>&1)
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        print_info "Successfully connected to VLC at ${VLC_BASE_URL}"
        return 0
    else
        print_error "Cannot connect to VLC at ${VLC_BASE_URL}"
        print_error "Error: $result"
        return 1
    fi
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Push an RTSP stream to VLC remote interface

OPTIONS:
    -h, --help              Show this help message
    -r, --rtsp URL          RTSP stream URL (default: $RTSP_URL)
    -H, --host HOST         VLC host address (default: $VLC_HOST)
    -p, --port PORT         VLC port (default: $VLC_PORT)
    -P, --password PASS     VLC HTTP password
    -s, --scheme SCHEME     URL scheme: http or https (default: $VLC_SCHEME)
    -c, --check             Only check VLC connection status

ENVIRONMENT VARIABLES:
    RTSP_URL                RTSP stream URL
    VLC_HOST                VLC host address
    VLC_PORT                VLC port number
    VLC_PASSWORD            VLC HTTP interface password
    VLC_SCHEME              URL scheme (http/https)

EXAMPLES:
    # Use default values
    $0

    # Specify custom RTSP stream
    $0 -r rtsp://camera.local:554/stream

    # Specify VLC host and password
    $0 -H 192.168.1.100 -P mypassword

    # Use environment variables
    export VLC_PASSWORD="mypassword"
    $0

    # Check connection only
    $0 --check

EOF
}

# Parse command line arguments
CHECK_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -r|--rtsp)
            RTSP_URL="$2"
            shift 2
            ;;
        -H|--host)
            VLC_HOST="$2"
            VLC_BASE_URL="${VLC_SCHEME}://${VLC_HOST}:${VLC_PORT}"
            shift 2
            ;;
        -p|--port)
            VLC_PORT="$2"
            VLC_BASE_URL="${VLC_SCHEME}://${VLC_HOST}:${VLC_PORT}"
            shift 2
            ;;
        -P|--password)
            VLC_PASSWORD="$2"
            shift 2
            ;;
        -s|--scheme)
            VLC_SCHEME="$2"
            VLC_BASE_URL="${VLC_SCHEME}://${VLC_HOST}:${VLC_PORT}"
            shift 2
            ;;
        -c|--check)
            CHECK_ONLY=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
echo "======================================"
echo "  RTSP to VLC Remote Stream"
echo "======================================"
echo ""

# Check VLC connection
if ! check_vlc_status; then
    print_error "Please ensure:"
    print_error "  1. VLC is running on ${VLC_HOST}:${VLC_PORT}"
    print_error "  2. HTTP interface is enabled in VLC"
    print_error "  3. Firewall allows connections"
    print_error "  4. Password is correct (if required)"
    exit 1
fi

# If check only, exit here
if [ "$CHECK_ONLY" = true ]; then
    print_info "Connection check complete"
    exit 0
fi

echo ""

# Play the stream
if play_stream "$RTSP_URL"; then
    print_info "Stream is now playing on VLC"
    print_info "VLC URL: ${VLC_BASE_URL}"
    print_info "RTSP URL: ${RTSP_URL}"
else
    exit 1
fi

echo ""
echo "======================================"
