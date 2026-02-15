#!/usr/bin/env python3
import sys
print("Starting test...", file=sys.stdout, flush=True)
sys.stdout.flush()

try:
    from server import init_db, DB_FILE
    print(f"Imported successfully. DB file: {DB_FILE}", flush=True)
    sys.stdout.flush()
    
    print("Calling init_db()...", flush=True)
    sys.stdout.flush()
    
    init_db()
    
    print("init_db() completed successfully!", flush=True)
    sys.stdout.flush()
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    sys.stderr.flush()
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    sys.exit(1)

print("Test completed successfully!", flush=True)
sys.stdout.flush()
