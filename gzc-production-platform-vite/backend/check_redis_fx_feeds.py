#!/usr/bin/env python3
"""
Check Redis for FX price feeds
"""
import asyncio
import redis.asyncio as redis
import json
import sys
sys.path.append('/Users/mikaeleage/Projects Container/gzc-production-platform/backend')

from app.core.azure_keyvault import keyvault_client


async def check_redis_fx_feeds():
    """Connect to Redis and check FX price feeds"""
    try:
        # Get Redis connection from Key Vault
        print("🔑 Getting Redis connection from Azure Key Vault...")
        redis_secret = keyvault_client.get_secret('redis-connection-string')
        
        if not redis_secret:
            print("❌ No Redis connection string found in Key Vault")
            print("📝 Checking if Redis is running locally...")
            redis_url = "redis://localhost:6379"
        else:
            redis_url = redis_secret
            print("✅ Got Redis connection from Key Vault")
        
        # Connect to Redis
        print(f"\n🔌 Connecting to Redis...")
        client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Test connection
        await client.ping()
        print("✅ Connected to Redis successfully")
        
        # Get Redis info
        info = await client.info()
        print(f"\n📊 Redis Info:")
        print(f"  - Version: {info.get('redis_version', 'Unknown')}")
        print(f"  - Connected clients: {info.get('connected_clients', 0)}")
        print(f"  - Used memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"  - Total keys: {info.get('db0', {}).get('keys', 0) if isinstance(info.get('db0'), dict) else 'Unknown'}")
        
        # Search for FX-related keys
        print("\n🔍 Searching for FX price feed keys...")
        
        # Common FX key patterns
        patterns = [
            "fx:*",
            "quote:*",
            "price:*",
            "feed:*",
            "EUR*",
            "USD*",
            "GBP*",
            "JPY*",
            "CHF*",
            "AUD*",
            "currency:*",
            "fx_*",
            "rates:*",
            "market:*"
        ]
        
        all_fx_keys = set()
        
        for pattern in patterns:
            try:
                # Use SCAN instead of KEYS for production
                cursor = 0
                while True:
                    cursor, keys = await client.scan(cursor, match=pattern, count=100)
                    all_fx_keys.update(keys)
                    if cursor == 0:
                        break
            except Exception as e:
                print(f"  ⚠️  Error scanning pattern '{pattern}': {e}")
        
        if not all_fx_keys:
            print("  ❌ No FX-related keys found")
            
            # Check all keys (limited)
            print("\n📋 Listing all available keys (max 100):")
            cursor = 0
            cursor, all_keys = await client.scan(cursor, count=100)
            
            if all_keys:
                for key in sorted(all_keys)[:20]:  # Show first 20
                    key_type = await client.type(key)
                    if key_type == 'string':
                        value = await client.get(key)
                        print(f"  - {key} (string): {value[:100]}...")
                    elif key_type == 'hash':
                        value = await client.hgetall(key)
                        print(f"  - {key} (hash): {json.dumps(value, indent=2)[:100]}...")
                    elif key_type == 'list':
                        length = await client.llen(key)
                        print(f"  - {key} (list): {length} items")
                    elif key_type == 'set':
                        size = await client.scard(key)
                        print(f"  - {key} (set): {size} members")
                    elif key_type == 'zset':
                        size = await client.zcard(key)
                        print(f"  - {key} (zset): {size} members")
                
                if len(all_keys) > 20:
                    print(f"  ... and {len(all_keys) - 20} more keys")
            else:
                print("  ❌ No keys found in Redis")
        else:
            print(f"\n✅ Found {len(all_fx_keys)} FX-related keys:")
            
            # Display FX data
            for key in sorted(all_fx_keys)[:20]:  # Show first 20
                try:
                    key_type = await client.type(key)
                    
                    if key_type == 'string':
                        value = await client.get(key)
                        try:
                            # Try to parse as JSON
                            parsed = json.loads(value)
                            print(f"\n📈 {key}:")
                            print(json.dumps(parsed, indent=2))
                        except:
                            print(f"\n📈 {key}: {value}")
                    
                    elif key_type == 'hash':
                        value = await client.hgetall(key)
                        print(f"\n📊 {key} (hash):")
                        print(json.dumps(value, indent=2))
                    
                    elif key_type == 'list':
                        values = await client.lrange(key, 0, 5)  # Get first 5
                        print(f"\n📋 {key} (list, first 5 items):")
                        for v in values:
                            print(f"  - {v}")
                    
                    elif key_type == 'stream':
                        # Read last 5 entries from stream
                        entries = await client.xrevrange(key, count=5)
                        print(f"\n📡 {key} (stream, last 5 entries):")
                        for entry_id, data in entries:
                            print(f"  - {entry_id}: {data}")
                            
                except Exception as e:
                    print(f"  ⚠️  Error reading {key}: {e}")
            
            if len(all_fx_keys) > 20:
                print(f"\n... and {len(all_fx_keys) - 20} more FX keys")
        
        # Check for common FX price feed structures
        print("\n🔍 Checking common FX feed structures...")
        
        # Check quote cache pattern from redis_client.py
        quote_symbols = ["EURUSD", "GBPUSD", "USDJPY", "EURGBP", "AUDUSD"]
        for symbol in quote_symbols:
            quote_key = f"quote:{symbol}"
            if await client.exists(quote_key):
                value = await client.get(quote_key)
                print(f"\n💹 Quote cache for {symbol}:")
                try:
                    print(json.dumps(json.loads(value), indent=2))
                except:
                    print(value)
        
        # Disconnect
        await client.close()
        print("\n✅ Redis check complete")
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection error: {e}")
        print("\n💡 Make sure Redis is running:")
        print("   brew services start redis")
        print("   or")
        print("   redis-server")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_redis_fx_feeds())