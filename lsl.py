from pylsl import StreamInlet, resolve_stream

# Find LSL streams
print("Looking for LSL streams...")
streams = resolve_stream()

if not streams:
    print("No LSL streams found!")
else:
    print(f"Found {len(streams)} LSL stream(s). Connecting to the first one...")

    # Connect to the first available stream
    inlet = StreamInlet(streams[0])

    print(f"Connected to stream: {streams[0].name()} ({streams[0].type()})")

    # Read data from the stream
    print("Receiving data... (Press Ctrl+C to stop)")
    try:
        while True:
            sample, timestamp = inlet.pull_sample()
            print(f"Time: {timestamp}, Data: {sample}")
            break
    except KeyboardInterrupt:
        print("\nStream monitoring stopped.")
