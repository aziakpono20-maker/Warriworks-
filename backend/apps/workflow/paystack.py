"""Paystack HTTP helpers. Secret keys are read only from backend environment."""
import json, os, urllib.request, urllib.error

BASE = 'https://api.paystack.co'

def paystack_request(path, payload=None, method=None):
    secret = os.getenv('PAYSTACK_SECRET_KEY')
    if not secret:
        raise RuntimeError('PAYSTACK_SECRET_KEY is not configured on the backend.')
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method or ('POST' if data else 'GET'), headers={'Authorization': f'Bearer {secret}', 'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors='replace')
        raise RuntimeError(f'Paystack API error ({exc.code}): {detail[:500]}') from exc
    if not result.get('status'):
        raise RuntimeError(result.get('message', 'Paystack request failed'))
    return result.get('data', {})
