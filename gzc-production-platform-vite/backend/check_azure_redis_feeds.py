#!/usr/bin/env python3
"""
Connect to Azure Redis and check FX price feeds
"""
import asyncio
import redis.asyncio as redis
import json
import ssl
import sys
sys.path.append('/Users/mikaeleage/Projects Container/gzc-production-platform/backend')

from app.core.azure_keyvault import keyvault_client


async def check_azure_redis_fx_feeds():
    """Connect to Azure Redis and check FX price feeds"""
    try:
        # Get Azure Redis connection from Key Vault
        print("🔑 Getting Azure Redis connection from Key Vault...")
        
        # Try different secret names
        redis_secret = None
        secret_names = [
            'redis-connection-string',
            'azure-cache-redis',
            'cache-connection-string',
            'redis-url'
        ]
        
        for secret_name in secret_names:
            try:
                redis_secret = keyvault_client.get_secret(secret_name)
                if redis_secret:
                    print(f"✅ Found Redis connection in secret: {secret_name}")
                    break
            except:
                continue
        
        if not redis_secret:
            print("❌ No Azure Redis connection string found in Key Vault")
            return
        
        # Parse connection string
        # Azure Redis connection strings typically look like:
        # hostname.redis.cache.windows.net:6380,password=xxx,ssl=True,abortConnect=False
        print("\n🔌 Connecting to Azure Redis...")
        
        # If it's a full redis:// URL
        if redis_secret.startswith('redis://') or redis_secret.startswith('rediss://'):
            redis_url = redis_secret
        else:
            # Parse Azure Cache for Redis connection string format
            parts = {}
            for part in redis_secret.split(','):
                if '=' in part:
                    key, value = part.split('=', 1)
                    parts[key.strip()] = value.strip()
                elif ':' in part and 'redis.cache.windows.net' in part:
                    # This is the host:port part
                    parts['host'] = part.strip()
            
            # Build Redis URL
            host = parts.get('host', redis_secret.split(',')[0])
            password = parts.get('password', parts.get('key', ''))
            ssl_enabled = parts.get('ssl', 'True').lower() == 'true'
            
            if ':' in host:
                hostname, port = host.split(':')
            else:
                hostname = host
                port = 6380 if ssl_enabled else 6379
            
            # Build URL
            protocol = 'rediss' if ssl_enabled else 'redis'
            redis_url = f"{protocol}://:{password}@{hostname}:{port}/0"
            
            print(f"  Host: {hostname}")
            print(f"  Port: {port}")
            print(f"  SSL: {ssl_enabled}")
        
        # Connect to Redis with SSL for Azure
        client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=10,
            socket_timeout=10
        )
        
        # Test connection
        await client.ping()
        print("✅ Connected to Azure Redis successfully!")
        
        # Get Redis info
        try:
            info = await client.info()
            print(f"\n📊 Azure Redis Info:")
            print(f"  - Server: {info.get('redis_version', 'Unknown')}")
            print(f"  - Mode: {info.get('redis_mode', 'standalone')}")
            print(f"  - Connected clients: {info.get('connected_clients', 0)}")
            print(f"  - Used memory: {info.get('used_memory_human', 'Unknown')}")
        except:
            print("  ℹ️  INFO command may be disabled on Azure Redis")
        
        # Search for FX price feed keys
        print("\n🔍 Searching for FX price feed keys...")
        
        # Common FX patterns
        patterns = [
            "fx:*",
            "fx-*", 
            "quote:*",
            "price:*",
            "feed:*",
            "rates:*",
            "market:*",
            "EUR*",
            "USD*",
            "GBP*",
            "JPY*",
            "*EURUSD*",
            "*GBPUSD*",
            "*USDJPY*",
            "currency:*",
            "spot:*",
            "forward:*"
        ]
        
        all_fx_keys = set()
        
        for pattern in patterns:
            try:
                cursor = 0
                while True:
                    cursor, keys = await client.scan(cursor, match=pattern, count=100)
                    all_fx_keys.update(keys)
                    if cursor == 0:
                        break
                    if len(all_fx_keys) > 1000:  # Limit for safety
                        break
            except Exception as e:
                print(f"  ⚠️  Error scanning pattern '{pattern}': {e}")
        
        if not all_fx_keys:
            print("\n  ❌ No FX-specific keys found")
            print("\n📋 Checking all keys (first 100)...")
            
            # Get sample of all keys
            cursor = 0
            cursor, all_keys = await client.scan(cursor, count=100)
            
            if all_keys:
                print(f"\n✅ Found {len(all_keys)} keys (showing first 20):")
                for key in sorted(all_keys)[:20]:
                    try:
                        key_type = await client.type(key)
                        ttl = await client.ttl(key)
                        ttl_str = f"TTL: {ttl}s" if ttl > 0 else "No expiry"
                        
                        if key_type == 'string':
                            value = await client.get(key)
                            # Check if it's JSON
                            try:
                                parsed = json.loads(value)
                                if any(curr in str(parsed) for curr in ['EUR', 'USD', 'GBP', 'JPY', 'CHF', 'AUD']):
                                    print(f"\n💹 {key} (string, {ttl_str}):")
                                    print(json.dumps(parsed, indent=2)[:300])
                                else:
                                    print(f"  - {key} (string, {ttl_str}): {str(value)[:100]}...")
                            except:
                                print(f"  - {key} (string, {ttl_str}): {str(value)[:100]}...")
                                
                        elif key_type == 'hash':
                            size = await client.hlen(key)
                            print(f"  - {key} (hash with {size} fields, {ttl_str})")
                            # Get sample fields
                            fields = await client.hkeys(key)
                            if fields and any(curr in str(fields) for curr in ['EUR', 'USD', 'GBP']):
                                sample = await client.hgetall(key)
                                print(f"    Fields: {json.dumps(sample, indent=2)[:200]}...")
                                
                        elif key_type == 'list':
                            length = await client.llen(key)
                            print(f"  - {key} (list with {length} items, {ttl_str})")
                            
                        elif key_type == 'set':
                            size = await client.scard(key)
                            print(f"  - {key} (set with {size} members, {ttl_str})")
                            
                        elif key_type == 'zset':
                            size = await client.zcard(key)
                            print(f"  - {key} (sorted set with {size} members, {ttl_str})")
                            
                    except Exception as e:
                        print(f"  ⚠️  Error reading {key}: {e}")
            else:
                print("  ❌ No keys found in Azure Redis")
                
        else:
            print(f"\n✅ Found {len(all_fx_keys)} FX-related keys!")
            
            # Group by pattern
            key_groups = {}
            for key in all_fx_keys:
                prefix = key.split(':')[0] if ':' in key else key.split('-')[0]
                if prefix not in key_groups:
                    key_groups[prefix] = []
                key_groups[prefix].append(key)
            
            print("\n📊 Key patterns found:")
            for prefix, keys in key_groups.items():
                print(f"  - {prefix}: {len(keys)} keys")
            
            # Show sample data
            print("\n💹 Sample FX data:")
            shown = 0
            for key in sorted(all_fx_keys):
                if shown >= 10:  # Show max 10 samples
                    break
                    
                try:
                    key_type = await client.type(key)
                    ttl = await client.ttl(key)
                    ttl_str = f"TTL: {ttl}s" if ttl > 0 else "No expiry"
                    
                    if key_type == 'string':
                        value = await client.get(key)
                        print(f"\n📈 {key} ({ttl_str}):")
                        try:
                            parsed = json.loads(value)
                            print(json.dumps(parsed, indent=2))
                        except:
                            print(f"  {value}")
                        shown += 1
                        
                    elif key_type == 'hash':
                        data = await client.hgetall(key)
                        print(f"\n📊 {key} (hash, {ttl_str}):")
                        print(json.dumps(data, indent=2))
                        shown += 1
                        
                except Exception as e:
                    print(f"  ⚠️  Error reading {key}: {e}")
        
        # Check specific quote cache pattern
        print("\n🔍 Checking quote cache pattern (quote:SYMBOL)...")
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "EURGBP", "AUDUSD", "USDCHF", "NZDUSD", "USDCAD"]
        found_quotes = False
        
        for symbol in symbols:
            try:
                quote_key = f"quote:{symbol}"
                if await client.exists(quote_key):
                    found_quotes = True
                    value = await client.get(quote_key)
                    ttl = await client.ttl(quote_key)
                    print(f"\n💹 {quote_key} (TTL: {ttl}s):")
                    try:
                        print(json.dumps(json.loads(value), indent=2))
                    except:
                        print(f"  {value}")
            except:
                pass
        
        if not found_quotes:
            print("  ❌ No quote:SYMBOL keys found")
        
        # Disconnect
        await client.close()
        print("\n✅ Azure Redis check complete!")
        
    except redis.ConnectionError as e:
        print(f"❌ Azure Redis connection error: {e}")
        print("\n💡 Check:")
        print("  1. Azure Redis instance is running")
        print("  2. Firewall rules allow your IP")
        print("  3. Connection string is correct in Key Vault")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_azure_redis_fx_feeds())