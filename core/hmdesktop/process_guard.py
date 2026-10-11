"""Hold a handle to this job's own worker, so timeout cannot kill a reused PID."""
import os


class WorkerProcess:
    def __init__(self, pid):
        self.handle = None
        if os.name == 'nt':
            import ctypes
            from ctypes import wintypes
            self.api = ctypes.WinDLL('kernel32', use_last_error=True)
            self.api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            self.api.OpenProcess.restype = wintypes.HANDLE
            self.api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
            self.api.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
            self.api.CloseHandle.argtypes = [wintypes.HANDLE]
            self.handle = self.api.OpenProcess(0x100001, False, pid)

    def exited(self):
        return bool(self.handle and self.api.WaitForSingleObject(self.handle, 0) == 0)

    def terminate(self):
        if self.handle and not self.exited():
            self.api.TerminateProcess(self.handle, 1)

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None
