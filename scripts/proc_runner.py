#!/usr/bin/env python3
"""Cross-platform process launcher for Procfile services (web, worker, beat).

Ensures local Windows runs via Honcho start Flask cleanly instead of invoking
Linux-only `bash start.sh`, and tracks the Windows Job Object / parent shell
so terminating Honcho never leaves orphaned Celery or Python child processes
holding stdout pipes open.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent


def _resolve_python_executable(repo_root: Path = REPO_ROOT) -> str:
    """Prefer the project's virtual environment interpreter when available."""
    if sys.prefix != sys.base_prefix:
        return sys.executable

    if os.name == "nt":
        candidates = (repo_root / ".venv" / "Scripts" / "python.exe",)
    else:
        candidates = (repo_root / ".venv" / "bin" / "python",)
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def _is_truthy(value: Optional[str]) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _build_child_env(base_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    env = dict(os.environ if base_env is None else base_env)
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    return env


def _build_service_command(
    service: str,
    python_exe: str,
    linux_script: str = "start.sh",
    is_windows: Optional[bool] = None,
) -> Tuple[List[str], Dict[str, str]]:
    """Return `(argv, extra_env)` for the requested Procfile service."""
    on_windows = (os.name == "nt") if is_windows is None else is_windows

    if service == "web":
        if on_windows:
            return [python_exe, "-u", str(Path(__file__).resolve()), "_serve_web"], {}
        extra_env: Dict[str, str] = {}
        if "RUN_CELERY_IN_WEB" not in os.environ:
            # Procfile already declares dedicated worker and beat services.
            extra_env["RUN_CELERY_IN_WEB"] = "false"
        return ["bash", linux_script], extra_env

    if service == "worker":
        return [
            python_exe,
            "-u",
            "-m",
            "celery",
            "-A",
            "app.celery",
            "worker",
            "--loglevel=info",
            "--pool=solo",
            "--concurrency=1",
        ], {}

    if service == "beat":
        return [
            python_exe,
            "-u",
            "-m",
            "celery",
            "-A",
            "app.celery",
            "beat",
            "--loglevel=info",
        ], {}

    raise ValueError(f"Unsupported service: {service}")


def _serve_web_in_process() -> int:
    """Initialize databases and run the Flask development server on Windows."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    if _is_truthy(os.environ.get("REQUIRE_POSTGRES")) and not _is_truthy(
        os.environ.get("DATABASE_MIGRATION_COMPLETE")
    ):
        print(
            "[proc_runner] PostgreSQL cutover is blocked until SQLite data migration is completed.",
            file=sys.stderr,
            flush=True,
        )
        return 1

    from app import JobDatabase, app, initialize_database

    initialize_database()
    JobDatabase().init_db()

    port = int(os.environ.get("PORT", "5000"))
    debug = _is_truthy(os.environ.get("FLASK_DEBUG") or os.environ.get("DEBUG"))
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
    return 0


# ---------------------------------------------------------------------------
# Windows process-tree lifecycle management
# ---------------------------------------------------------------------------

if os.name == "nt":
    import ctypes
    import ctypes.wintypes as wt

    _TH32CS_SNAPPROCESS = 0x00000002
    _SYNCHRONIZE = 0x00100000
    _INFINITE = 0xFFFFFFFF
    _WAIT_OBJECT_0 = 0x00000000
    _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    _JOB_OBJECT_EXTENDED_LIMIT_INFO = 9

    class _PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wt.DWORD),
            ("cntUsage", wt.DWORD),
            ("th32ProcessID", wt.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
            ("th32ModuleID", wt.DWORD),
            ("cntThreads", wt.DWORD),
            ("th32ParentProcessID", wt.DWORD),
            ("pcPriClassBase", wt.LONG),
            ("dwFlags", wt.DWORD),
            ("szExeFile", wt.WCHAR * 260),
        ]

    class _IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wt.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wt.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wt.DWORD),
            ("SchedulingClass", ctypes.c_uint32),
        ]

    class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", _IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _kernel32.CreateToolhelp32Snapshot.argtypes = [wt.DWORD, wt.DWORD]
    _kernel32.CreateToolhelp32Snapshot.restype = wt.HANDLE
    _kernel32.Process32FirstW.argtypes = [wt.HANDLE, ctypes.POINTER(_PROCESSENTRY32W)]
    _kernel32.Process32FirstW.restype = wt.BOOL
    _kernel32.Process32NextW.argtypes = [wt.HANDLE, ctypes.POINTER(_PROCESSENTRY32W)]
    _kernel32.Process32NextW.restype = wt.BOOL
    _kernel32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
    _kernel32.OpenProcess.restype = wt.HANDLE
    _kernel32.CloseHandle.argtypes = [wt.HANDLE]
    _kernel32.CloseHandle.restype = wt.BOOL
    _kernel32.WaitForMultipleObjects.argtypes = [
        wt.DWORD,
        ctypes.POINTER(wt.HANDLE),
        wt.BOOL,
        wt.DWORD,
    ]
    _kernel32.WaitForMultipleObjects.restype = wt.DWORD
    _kernel32.CreateJobObjectW.argtypes = [wt.LPVOID, wt.LPCWSTR]
    _kernel32.CreateJobObjectW.restype = wt.HANDLE
    _kernel32.SetInformationJobObject.argtypes = [wt.HANDLE, ctypes.c_int, wt.LPVOID, wt.DWORD]
    _kernel32.SetInformationJobObject.restype = wt.BOOL
    _kernel32.AssignProcessToJobObject.argtypes = [wt.HANDLE, wt.HANDLE]
    _kernel32.AssignProcessToJobObject.restype = wt.BOOL
    _kernel32.TerminateJobObject.argtypes = [wt.HANDLE, wt.UINT]
    _kernel32.TerminateJobObject.restype = wt.BOOL
    _kernel32.GetCurrentProcess.argtypes = []
    _kernel32.GetCurrentProcess.restype = wt.HANDLE

    def _snapshot_processes() -> Dict[int, Tuple[int, str]]:
        snap = _kernel32.CreateToolhelp32Snapshot(_TH32CS_SNAPPROCESS, 0)
        if not snap or snap == wt.HANDLE(-1).value:
            return {}
        procs: Dict[int, Tuple[int, str]] = {}
        try:
            entry = _PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(_PROCESSENTRY32W)
            if _kernel32.Process32FirstW(snap, ctypes.byref(entry)):
                while True:
                    procs[int(entry.th32ProcessID)] = (
                        int(entry.th32ParentProcessID),
                        entry.szExeFile.lower(),
                    )
                    if not _kernel32.Process32NextW(snap, ctypes.byref(entry)):
                        break
        finally:
            _kernel32.CloseHandle(snap)
        return procs

    def _find_honcho_watch_pids(
        procs: Dict[int, Tuple[int, str]],
        self_pid: int,
    ) -> Tuple[List[int], bool]:
        """Locate Honcho's shell PID (`cmd.exe`) above this runner.

        Returns `(watch_pids, ancestor_already_dead)`.
        """
        if not procs or self_pid not in procs:
            return [], False

        watch_pids: List[int] = []
        seen = {self_pid}
        cursor = procs[self_pid][0]

        for _ in range(4):
            if cursor <= 0 or cursor in seen:
                break
            if cursor not in procs:
                # A wrapper ancestor (such as cmd.exe killed by Honcho) already exited.
                return watch_pids, True
            seen.add(cursor)
            ppid, exe = procs[cursor]
            if exe == "cmd.exe":
                return [cursor], False
            watch_pids.append(cursor)
            cursor = ppid

        return watch_pids[:1], False

    def _create_kill_on_close_job(assign_self: bool = True) -> Optional[int]:
        job = _kernel32.CreateJobObjectW(None, None)
        if not job:
            return None
        info = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not _kernel32.SetInformationJobObject(
            job,
            _JOB_OBJECT_EXTENDED_LIMIT_INFO,
            ctypes.byref(info),
            ctypes.sizeof(info),
        ):
            _kernel32.CloseHandle(job)
            return None
        if assign_self and not _kernel32.AssignProcessToJobObject(
            job, _kernel32.GetCurrentProcess()
        ):
            _kernel32.CloseHandle(job)
            return None
        return int(job)

    def _terminate_tree_and_exit(
        job_handle: Optional[int],
        proc: Optional[subprocess.Popen],
    ) -> None:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except Exception:
            pass
        if job_handle:
            _kernel32.TerminateJobObject(job_handle, 0)
        if proc is not None and proc.poll() is None:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=3,
                    check=False,
                )
            except Exception:
                pass
            try:
                proc.kill()
            except Exception:
                pass
        os._exit(0)

    def _run_windows_managed(cmd: List[str], env: Dict[str, str]) -> int:
        under_honcho = bool(os.environ.get("HONCHO_PROCESS_NAME"))
        watch_pids: List[int] = []

        if under_honcho:
            procs = _snapshot_processes()
            watch_pids, already_dead = _find_honcho_watch_pids(procs, os.getpid())
            if already_dead:
                return 0

        # Put the runner itself into a kill-on-close Job Object before spawning
        # so every child/grandchild (venv shim, celery, selenium, etc.) is born
        # inside the job with zero race window.
        job_handle = _create_kill_on_close_job(assign_self=True)
        child_job: Optional[int] = None
        if job_handle is None:
            child_job = _create_kill_on_close_job(assign_self=False)

        proc = subprocess.Popen(cmd, env=env, cwd=str(REPO_ROOT))
        if child_job is not None:
            _kernel32.AssignProcessToJobObject(child_job, int(proc._handle))

        done_event = threading.Event()
        active_job = job_handle or child_job

        if under_honcho and watch_pids:
            handles = []
            for pid in watch_pids:
                handle = _kernel32.OpenProcess(_SYNCHRONIZE, False, pid)
                if not handle:
                    _terminate_tree_and_exit(active_job, proc)
                handles.append(handle)

            def _watch_ancestors() -> None:
                arr = (wt.HANDLE * len(handles))(*handles)
                wait_rc = _kernel32.WaitForMultipleObjects(len(handles), arr, False, _INFINITE)
                for h in handles:
                    _kernel32.CloseHandle(h)
                if not done_event.is_set() and wait_rc >= _WAIT_OBJECT_0:
                    _terminate_tree_and_exit(active_job, proc)

            watcher = threading.Thread(target=_watch_ancestors, daemon=True)
            watcher.start()

        try:
            rc = proc.wait()
        except KeyboardInterrupt:
            try:
                rc = proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _terminate_tree_and_exit(active_job, proc)
                rc = 130
        finally:
            done_event.set()

        # Keep job_handle open until process teardown if we assigned self, so
        # Windows closes it on exit and reaps any lingering grandchild without
        # prematurely killing this process before returning `rc`.
        if child_job is not None:
            _kernel32.TerminateJobObject(child_job, 0)
            _kernel32.CloseHandle(child_job)
        return rc


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run a Procfile service cleanly across OSes.")
    parser.add_argument("service", choices=["web", "worker", "beat", "_serve_web"])
    parser.add_argument("--linux-script", default="start.sh")
    args = parser.parse_args(argv)

    if args.service == "_serve_web":
        return _serve_web_in_process()

    python_exe = _resolve_python_executable()
    cmd, extra_env = _build_service_command(
        args.service,
        python_exe=python_exe,
        linux_script=args.linux_script,
    )
    env = _build_child_env()
    env.update(extra_env)

    if os.name != "nt":
        os.chdir(REPO_ROOT)
        os.execvpe(cmd[0], cmd, env)

    return _run_windows_managed(cmd, env)


if __name__ == "__main__":
    sys.exit(main())
