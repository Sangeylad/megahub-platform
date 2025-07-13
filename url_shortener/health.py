#!/usr/bin/env python3
# url_shortener/health.py
import sys
import requests
import os

def health_check():
    """Health check pour Docker"""
    try:
        response = requests.get(
            'http://localhost:5000/health',
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print("Health check passed")
                sys.exit(0)
            else:
                print(f"Service unhealthy: {data}")
                sys.exit(1)
        else:
            print(f"Health check failed with status: {response.status_code}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    health_check()