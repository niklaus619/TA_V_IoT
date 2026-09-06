"""Wire-level Modbus and dashboard integration tests, without Pi hardware."""
import importlib.util
from pathlib import Path
import socket
import struct
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Src' / 'RaspServ'))
import database
import server as server_module
import app as web_module

spec = importlib.util.spec_from_file_location('modbus_client', ROOT / 'Src/RaspCtrl/server.py')
client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client_module)


def wait_for(predicate, timeout=4):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError('Timed out waiting for Modbus operation')


class ModbusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(database, 'DATABASE_PATH', Path(self.temp.name) / 'test.db')
        self.db_patch.start()
        database.initialize_database()
        self.server = server_module.RaspCtrlServer('127.0.0.1', 0).bind()
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = client_module.IoTServerClient('127.0.0.1', self.server.port, reconnect_seconds=0.05)
        self.web_patch = patch.object(web_module, 'raspctrl_server', self.server)
        self.web_patch.start()
        self.web = web_module.app.test_client()

    def tearDown(self):
        self.client.close()
        self.server.close()
        self.thread.join(2)
        self.web_patch.stop()
        self.db_patch.stop()
        self.temp.cleanup()

    def exchange(self, sock, pdu, fragmented=False, unit=1):
        packet = struct.pack('>HHHB', 123, 0, len(pdu) + 1, unit) + pdu
        if fragmented:
            for byte in packet:
                sock.sendall(bytes([byte]))
        else:
            sock.sendall(packet)
        header = server_module._read_exact(sock, 7)
        transaction, protocol, length, response_unit = struct.unpack('>HHHB', header)
        self.assertEqual((transaction, protocol, response_unit), (123, 0, unit))
        return server_module._read_exact(sock, length - 1)

    def status(self):
        return dict(type='status', temperature=-3.2, humidity=46.2, light=618,
                    blind='closed', heating=False, cooling=True,
                    target_temperature=22.0, temperature_deadband=0.5)

    def test_wire_format_fragmentation_and_exceptions(self):
        with socket.create_connection(('127.0.0.1', self.server.port), timeout=2) as sock:
            pdu = struct.pack('>BHHB6H', 16, 0, 6, 12, 65504, 462, 618, 5, 220, 5)
            self.assertEqual(self.exchange(sock, pdu, fragmented=True), b'\x10\x00\x00\x00\x06')
            self.assertEqual(self.exchange(sock, b'\x03\x00\x00\x00\x06'), b'\x03\x0c' + pdu[6:])
            self.assertEqual(self.exchange(sock, b'\x03\x00\x63\x00\x02'), b'\x83\x02')
            self.assertEqual(self.exchange(sock, b'\x03\x00\x00\x00\x00'), b'\x83\x03')
            self.assertEqual(self.exchange(sock, b'\x06\x00\x00\x00\x01'), b'\x86\x01')
            self.assertEqual(self.exchange(sock, pdu[:-1]), b'\x90\x03')
            self.assertEqual(self.exchange(sock, b'\x03\x00\x00\x00\x01', unit=2), b'\x83\x0b')
        self.assertEqual(database.get_measurements()[0]['temperature'], -3.2)

    def test_status_history_and_all_web_commands(self):
        self.assertEqual(self.web.post('/api/target-temperature', json={'target_temperature': 24}).status_code, 503)
        self.assertTrue(self.client.send(self.status()))
        wait_for(lambda: len(database.get_measurements()) == 1)
        self.assertTrue(self.web.get('/api/status').json['connected'])
        history = self.web.get('/api/history').json
        self.assertEqual((history[0]['humidity'], history[0]['light']), (46.2, 618))
        for endpoint, data in (
            ('target-temperature', {'target_temperature': 24.5}),
            ('temperature-deadband', {'temperature_deadband': 0.7}),
            ('cpb-neopixel', {'on': False}),
            ('sense-neopixel', {'on': True}),
        ):
            self.assertEqual(self.web.post('/api/' + endpoint, json=data).status_code, 200)
        commands = []
        def collected():
            commands.extend(self.client.receive())
            return len(commands) == 4
        wait_for(collected)
        self.assertIn({'type': 'set_parameters', 'target_temperature': 24.5}, commands)
        self.assertIn({'type': 'set_parameters', 'temperature_deadband': 0.7}, commands)
        self.assertIn({'type': 'set_cpb_neopixel', 'on': False}, commands)
        self.assertIn({'type': 'set_sense_neopixel', 'on': True}, commands)
        time.sleep(0.35)
        self.assertEqual(self.client.receive(), [])
        for value in (0, 0.01, 7000, float('nan'), float('inf')):
            self.assertEqual(self.web.post('/api/temperature-deadband', json={'temperature_deadband': value}).status_code, 400)

    def test_reconnect_replays_desired_values_and_reports_stale(self):
        self.client.receive()
        wait_for(self.server.is_connected)
        self.server.send_command({'type': 'set_cpb_neopixel', 'on': False})
        received = []
        def first_command():
            received.extend(self.client.receive())
            return bool(received)
        wait_for(first_command)
        # Ein echter Socket-Abbruch muss denselben Client neu verbinden lassen.
        received.clear()
        self.client._socket.shutdown(socket.SHUT_RDWR)
        wait_for(first_command)
        self.assertEqual(received, [{'type': 'set_cpb_neopixel', 'on': False}])
        self.client.close()
        with self.server._lock:
            self.server._last_seen = time.monotonic() - 6
        self.assertFalse(self.server.is_connected())
        self.client = client_module.IoTServerClient('127.0.0.1', self.server.port, reconnect_seconds=0.05)
        received.clear()
        wait_for(first_command)
        self.assertEqual(received, [{'type': 'set_cpb_neopixel', 'on': False}])

    def test_network_timeout_does_not_block_controller(self):
        entered = threading.Event()
        release = threading.Event()
        def slow_connect():
            entered.set()
            release.wait(2)
            return False
        with patch.object(self.client, 'connect', side_effect=slow_connect):
            self.client.receive()
            self.assertTrue(entered.wait(1))
            try:
                started = time.monotonic()
                for _ in range(100):
                    self.client.receive()
                    self.client.send(self.status())
                self.assertLess(time.monotonic() - started, 0.5)
            finally:
                release.set()

    def test_bad_header_closes_connection_and_database_failure_is_exception(self):
        with socket.create_connection(('127.0.0.1', self.server.port), timeout=2) as sock:
            sock.sendall(struct.pack('>HHHB', 1, 1, 2, 1) + b'\x03')
            try:
                self.assertEqual(sock.recv(1), b'')
            except ConnectionResetError:
                pass
        pdu = struct.pack('>BHHB6H', 16, 0, 6, 12, 220, 500, 50, 0, 220, 5)
        with patch.object(server_module, 'save_measurement', side_effect=OSError('test failure')):
            with self.assertLogs(server_module.LOG, level='ERROR'):
                self.assertEqual(self.server._process_pdu(pdu), b'\x90\x04')
        self.assertEqual(self.server.get_latest_status(), {})


if __name__ == '__main__':
    unittest.main()
