#!/usr/bin/env python3
"""
Connect to Azure Redis and check FX price feeds (synchronous version)
"""
import redis
import json
import sys
sys.path.append('/Users/mikaeleage/Projects Container/gzc-production-platform/backend')

from app.core.azure_keyvault import keyvault_client


def check_azure_redis_fx_feeds():
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
        
        print("\n🔌 Connecting to Azure Redis...")
        print(f"  Connection string format: {redis_secret[:30]}...")
        
        # Parse connection string - could be URL format or Azure format
        if redis_secret.startswith('redis://') or redis_secret.startswith('rediss://'):
            # Parse Redis URL format: redis://:password@hostname:port
            from urllib.parse import urlparse
            parsed = urlparse(redis_secret)
            hostname = parsed.hostname
            port = parsed.port or 6380  # Azure Redis typically uses 6380
            password = parsed.password
            # Azure Redis Cache always uses SSL on port 6380
            ssl_enabled = port == 6380 or parsed.scheme == 'rediss'
        elif ',' in redis_secret and '=' in redis_secret:
            # Azure format: hostname.redis.cache.windows.net:6380,password=xxx,ssl=True
            parts = {}
            for part in redis_secret.split(','):
                if '=' in part:
                    key, value = part.split('=', 1)
                    parts[key.strip()] = value.strip()
                elif ':' in part and 'redis.cache.windows.net' in part:
                    parts['host'] = part.strip()
            
            host = parts.get('host', redis_secret.split(',')[0])
            password = parts.get('password', parts.get('key', ''))
            ssl_enabled = parts.get('ssl', 'True').lower() == 'true'
            
            if ':' in host:
                hostname, port = host.split(':')
                port = int(port)
            else:
                hostname = host
                port = 6380 if ssl_enabled else 6379
        else:
            # Simple host:port format
            if ':' in redis_secret:
                parts = redis_secret.split(':')
                hostname = parts[0]
                port = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 6380
            else:
                hostname = redis_secret
                port = 6380
            password = None
            ssl_enabled = port == 6380
        
        print(f"  Host: {hostname}")
        print(f"  Port: {port}")
        print(f"  SSL: {ssl_enabled}")
        
        # Connect to Redis
        if ssl_enabled:
            client = redis.Redis(
                host=hostname,
                port=port,
                password=password,
                ssl=True,
                ssl_cert_reqs=None,
                decode_responses=True,
                socket_connect_timeout=10,
                socket_timeout=10
            )
        else:
            client = redis.Redis(
                host=hostname,
                port=port,
                password=password,
                decode_responses=True,
                socket_connect_timeout=10,
                socket_timeout=10
            )
        
        # Test connection
        client.ping()
        print("✅ Connected to Azure Redis successfully!")
        
        # Get basic info
        print("\n📊 Azure Redis Status:")
        try:
            db_size = client.dbsize()
            print(f"  - Total keys: {db_size}")
        except:
            print("  - DBSIZE command may be disabled")
        
        # Search for FX-related keys
        print("\n🔍 Searching for FX price feed keys...")
        
        all_fx_keys = set()
        patterns = [
            "fx:*", "fx-*", "quote:*", "price:*", "feed:*", 
            "rates:*", "market:*", "*EUR*", "*USD*", "*GBP*",
            "*JPY*", "*CHF*", "*AUD*", "spot:*", "forward:*"
        ]
        
        # Scan for keys
        for pattern in patterns:
            try:
                cursor = 0
                while True:
                    cursor, keys = client.scan(cursor, match=pattern, count=100)
                    all_fx_keys.update(keys)
                    if cursor == 0:
                        break
                    if len(all_fx_keys) > 500:  # Limit
                        break
            except Exception as e:
                if "unknown command" not in str(e).lower():
                    print(f"  ⚠️  Error scanning '{pattern}': {e}")
        
        if not all_fx_keys:
            print("\n  ❌ No FX-specific keys found")
            
            # Get a sample of all keys
            print("\n📋 Sampling all keys...")
            try:
                cursor, sample_keys = client.scan(0, count=50)
                if sample_keys:
                    print(f"\n✅ Found {len(sample_keys)} keys (showing up to 20):")
                    for key in sorted(sample_keys)[:20]:
                        try:
                            key_type = client.type(key)
                            ttl = client.ttl(key)
                            ttl_str = f"TTL:{ttl}s" if ttl > 0 else "Persistent"
                            
                            if key_type == 'string':
                                value = client.get(key)
                                # Check if it contains FX data
                                if any(curr in str(value).upper() for curr in ['EUR', 'USD', 'GBP', 'JPY']):
                                    print(f"\n💹 {key} ({ttl_str}):")
                                    try:
                                        parsed = json.loads(value)
                                        print(json.dumps(parsed, indent=2)[:300])
                                    except:
                                        print(f"  {value[:200]}...")
                                else:
                                    print(f"  - {key} (string, {ttl_str})")
                            else:
                                print(f"  - {key} ({key_type}, {ttl_str})")
                        except Exception as e:
                            print(f"  ⚠️  Error reading {key}: {e}")
                else:
                    print("  ❌ No keys found")
            except Exception as e:
                print(f"  ⚠️  SCAN may be disabled: {e}")
                
        else:
            print(f"\n✅ Found {len(all_fx_keys)} FX-related keys!")
            
            # Show samples
            print("\n💹 FX Price Feed Data:")
            for i, key in enumerate(sorted(all_fx_keys)):
                if i >= 15:  # Limit display
                    print(f"\n... and {len(all_fx_keys) - 15} more keys")
                    break
                
                try:
                    key_type = client.type(key)
                    ttl = client.ttl(key)
                    ttl_str = f"TTL:{ttl}s" if ttl > 0 else "Persistent"
                    
                    print(f"\n📈 {key} ({key_type}, {ttl_str}):")
                    
                    if key_type == 'string':
                        value = client.get(key)
                        try:
                            parsed = json.loads(value)
                            print(json.dumps(parsed, indent=2)[:400])
                        except:
                            print(f"  {value[:200]}...")
                    
                    elif key_type == 'hash':
                        data = client.hgetall(key)
                        print(json.dumps(data, indent=2)[:400])
                    
                    elif key_type == 'list':
                        length = client.llen(key)
                        samples = client.lrange(key, 0, 2)
                        print(f"  List with {length} items. First 3:")
                        for item in samples:
                            print(f"    - {item[:100]}...")
                    
                except Exception as e:
                    print(f"  ⚠️  Error: {e}")
        
        # Check specific patterns
        print("\n🔍 Checking standard FX quote patterns...")
        
        # Check quote:SYMBOL pattern
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "EURGBP", "AUDUSD", "EUR/USD", "GBP/USD", "USD/JPY"]
        for symbol in symbols:
            for prefix in ["quote:", "price:", "fx:", "market:", ""]:
                key = f"{prefix}{symbol}"
                try:
                    if client.exists(key):
                        value = client.get(key)
                        ttl = client.ttl(key)
                        print(f"\n✅ Found {key} (TTL:{ttl}s):")
                        try:
                            print(json.dumps(json.loads(value), indent=2))
                        except:
                            print(f"  {value}")
                        break
                except:
                    pass
        
        # Close connection
        client.close()
        print("\n✅ Azure Redis check complete!")
        
    except redis.ConnectionError as e:
        print(f"❌ Azure Redis connection error: {e}")
        print("\n💡 Possible issues:")
        print("  1. Check firewall rules in Azure Portal")
        print("  2. Verify connection string format")
        print("  3. Ensure Redis instance is running")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_azure_redis_fx_feeds()