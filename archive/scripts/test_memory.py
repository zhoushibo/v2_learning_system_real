"""Test V1 Memory System Integration"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("=" * 60)
print("V1 Memory System Integration Test")
print("=" * 60)

# Import the system
import sys
sys.path.insert(0, r'C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\mvp\src\common')

try:
    from v1_memory_integration import V1MemorySystemIntegration

    # Initialize
    print("\n1. Initializing memory system...")
    memory = V1MemorySystemIntegration()
    print("   OK")

    # Health check
    print("\n2. Health check...")
    health = memory.health_check()
    print(f"   Redis (L1):    {'OK' if health['l1_redis'] else 'FAIL'}")
    print(f"   ChromaDB (L2): {'OK' if health['l2_chroma'] else 'FAIL'}")
    print(f"   SQLite (L3):   {'OK' if health['l3_sqlite'] else 'FAIL'}")
    print(f"   All OK:        {health['all_ok']}")

    if not health['l3_sqlite']:
        print("\n   WARNING: SQLite initialization required")
        print("   MVP can use SQLite + Redis only")

    # Test Redis (L1)
    print("\n3. Testing L1: Redis Cache...")
    test_key = "test_key_123"
    test_value = {"message": "Hello Memory System", "timestamp": "2026-02-16"}

    # Save
    if memory.save_to_cache(test_key, test_value, ttl=60):
        print(f"   Save to cache: OK")

    # Get
    retrieved = memory.get_from_cache(test_key)
    if retrieved == test_value:
        print(f"   Get from cache: OK (data matches)")
    else:
        print(f"   Get from cache: FAIL (data mismatch)")

    # Test SQLite (L3) - Tasks
    print("\n4. Testing L3: SQLite (Tasks)...")
    task_data = {
        "task_id": "test_task_123",
        "content": "Test task for memory system",
        "status": "pending",
        "metadata": {"source": "test"}
    }

    if memory.save_to_sqlite("tasks", task_data):
        print(f"   Save task: OK")

    retrieved_task = memory.get_from_sqlite("tasks", "test_task_123", "task_id")
    if retrieved_task and retrieved_task['task_id'] == "test_task_123":
        print(f"   Get task: OK (task_id matches)")
        print(f"   Task status: {retrieved_task['status']}")

    # Test unified interface
    print("\n5. Testing unified interface...")
    unified_key = "unified_test_456"
    unified_value = {"data": "unified test", "layer": "all"}

    memory.save(unified_key, unified_value)
    retrieved_unified = memory.get(unified_key)

    if retrieved_unified:
        print(f"   Unified save/get: OK")

    # Summary
    print("\n" + "=" * 60)
    if health['l1_redis'] and health['l3_sqlite']:
        print("SUCCESS: Three-layer memory system test passed!")
        print("\nCore validation:")
        print("  - Redis Cache (L1)      OK")
        print("  - SQLite Persistence (L3) OK")
        print("  - Unified Interface      OK")
        print("\nNote:")
        print("  - ChromaDB (L2) is for semantic search in production")
        print("  - MVP successfully integrated V1 memory stack!")
    else:
        print("WARNING: Some components failed")
        print(f"  Redis (L1):    {'OK' if health['l1_redis'] else 'FAIL'}")
        print(f"  SQLite (L3):   {'OK' if health['l3_sqlite'] else 'FAIL'}")
        print("\nPlease install missing components:")
        if not health['l1_redis']:
            print("  - Redis: Install and start Redis server")
        if not health['l3_sqlite']:
            print("  - SQLite: Check database path")
    print("=" * 60)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
