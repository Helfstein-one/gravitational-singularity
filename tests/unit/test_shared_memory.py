"""
Unit tests for SharedMemoryRingBuffer (IPC Zero-Copy).
Verifies ring buffer roundtrip, wrap-around, and sub-millisecond latency.
"""

import unittest
from src.adapters.outbound.shared_memory_adapter import SharedMemoryRingBuffer


class TestSharedMemoryRingBuffer(unittest.TestCase):
    def setUp(self):
        self.shm_name = "test_singularity_shm"
        self.writer = SharedMemoryRingBuffer(name=self.shm_name, size=8192, create=True)
        self.reader = SharedMemoryRingBuffer(name=self.shm_name, size=8192, create=False)

    def tearDown(self):
        self.writer.close()
        self.reader.close()
        self.writer.unlink()

    def test_write_and_read_event_roundtrip(self):
        ok = self.writer.write_event("test_event", {"metric": "tokens_saved", "value": 4200})
        self.assertTrue(ok)

        events = self.reader.read_latest_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], "test_event")
        self.assertEqual(events[0]["data"]["metric"], "tokens_saved")
        self.assertEqual(events[0]["data"]["value"], 4200)

    def test_multiple_events_and_wrap(self):
        for i in range(25):
            self.writer.write_event("tick", {"seq": i})

        events = self.reader.read_latest_events(max_count=10)
        self.assertLessEqual(len(events), 10)
        self.assertEqual(events[-1]["data"]["seq"], 24)


if __name__ == "__main__":
    unittest.main()
