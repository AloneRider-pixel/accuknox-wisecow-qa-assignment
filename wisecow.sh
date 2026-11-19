#!/usr/bin/env bash
# Wisecow adaptation: the upstream fortune/cowsay app with per-connection transport.
# Original source is preserved in upstream/wisecow.sh; see docs/TRANSPORT_CHANGE.md.
set -u
export LC_ALL=C

reply() {
    local code=$1 reason=$2 body=$3 send_body=${4:-yes}
    printf 'HTTP/1.1 %s %s\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: %s\r\nConnection: close\r\nX-Content-Type-Options: nosniff\r\n\r\n' "$code" "$reason" "${#body}"
    [[ $send_body == no ]] || printf '%s' "$body"
    return 0
}

request() {
    local line='' header='' method='' target='' version='' extra=''
    local total=0 count=0 headers_done=no wisdom='' cow='' body=''
    # -n bounds allocation per line. The enclosing timeout also bounds the whole child.
    if ! IFS= read -r -n 8193 -t 2 line; then
        [[ -z $line ]] || reply 408 'Request Timeout' 'Request timed out.'
        return 0
    fi
    if (( ${#line} > 8192 )); then
        reply 414 'URI Too Long' 'Request line too long.'; return 0
    fi
    line=${line%$'\r'}
    read -r method target version extra <<< "$line"
    if [[ -n $extra || -z $target || $target != /* || ! $version =~ ^HTTP/1\.[01]$ ]]; then
        reply 400 'Bad Request' 'Malformed request.'; return 0
    fi
    total=${#line}
    for ((count=0; count<64; count++)); do
        if ! IFS= read -r -n 8193 -t 2 header; then
            reply 408 'Request Timeout' 'Headers timed out.'; return 0
        fi
        ((total+=${#header}+2))
        if (( ${#header} > 8192 || total > 16384 )); then
            reply 431 'Request Header Fields Too Large' 'Headers too large.'; return 0
        fi
        header=${header%$'\r'}
        if [[ -z $header ]]; then headers_done=yes; break; fi
        if [[ $header != *:* || $header == [$' \t']* ]]; then
            reply 400 'Bad Request' 'Malformed header.'; return 0
        fi
    done
    if [[ $headers_done != yes ]]; then
        reply 431 'Request Header Fields Too Large' 'Too many headers.'; return 0
    fi
    if [[ $method != GET && $method != HEAD ]]; then
        reply 405 'Method Not Allowed' 'Only GET and HEAD are supported.'; return 0
    fi
    if ! wisdom=$(timeout --kill-after=1s 2s fortune -s); then
        reply 503 'Service Unavailable' 'Fortune is unavailable.'; return 0
    fi
    if ! cow=$(printf '%s\n' "$wisdom" | timeout --kill-after=1s 2s cowsay); then
        reply 503 'Service Unavailable' 'Cow renderer is unavailable.'; return 0
    fi
    if (( ${#cow} > 65536 )); then
        reply 503 'Service Unavailable' 'Rendered response is too large.'; return 0
    fi
    # Display the original cow as text, not HTML supplied by the fortune database.
    cow=${cow//&/\&amp;}
    cow=${cow//</\&lt;}
    cow=${cow//>/\&gt;}
    body="<pre>${cow}</pre>"
    if [[ $method == HEAD ]]; then reply 200 OK "$body" no; else reply 200 OK "$body"; fi
}

if [[ ${1:-} == --request ]]; then
    request
else
    for tool in socat timeout fortune cowsay; do
        command -v "$tool" >/dev/null 2>&1 || { printf 'Missing dependency: %s\n' "$tool" >&2; exit 1; }
    done
    printf 'Wisecow concurrent transport listening on port 4499\n' >&2
    # One persistent listener, at most 8 independent handlers. No global FIFO.
    # Each child gets a total 8s budget; idle reads and rendering have tighter bounds.
    exec socat -T 9 TCP4-LISTEN:4499,reuseaddr,fork,max-children=8,backlog=32 \
        "EXEC:timeout --kill-after=1s 8s bash ${BASH_SOURCE[0]} --request"
fi
