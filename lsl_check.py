from pylsl import resolve_stream

# Resolve all streams
streams = resolve_stream()

# Print information about each stream
for stream in streams:
    print(f"Name: {stream.name()}, Type: {stream.type()}, Source ID: {stream.source_id()}")