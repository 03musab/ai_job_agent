from pathlib import Path

from scripts import hosting_readiness_agent, proc_runner


def test_build_service_commands_windows_and_posix(monkeypatch):
    monkeypatch.delenv("RUN_CELERY_IN_WEB", raising=False)

    web_win_cmd, web_win_env = proc_runner._build_service_command(
        "web", python_exe="python.exe", linux_script="start.sh", is_windows=True
    )
    assert web_win_cmd[0] == "python.exe"
    assert web_win_cmd[-1] == "_serve_web"
    assert web_win_env == {}

    web_posix_cmd, web_posix_env = proc_runner._build_service_command(
        "web", python_exe="/venv/bin/python", linux_script="start.sh", is_windows=False
    )
    assert web_posix_cmd == ["bash", "start.sh"]
    assert web_posix_env == {"RUN_CELERY_IN_WEB": "false"}

    worker_cmd, worker_env = proc_runner._build_service_command(
        "worker", python_exe="python.exe", is_windows=True
    )
    assert worker_cmd == [
        "python.exe",
        "-u",
        "-m",
        "celery",
        "-A",
        "app.celery",
        "worker",
        "--loglevel=info",
        "--pool=solo",
        "--concurrency=1",
    ]
    assert worker_env == {}

    beat_cmd, beat_env = proc_runner._build_service_command(
        "beat", python_exe="python.exe", is_windows=True
    )
    assert beat_cmd == [
        "python.exe",
        "-u",
        "-m",
        "celery",
        "-A",
        "app.celery",
        "beat",
        "--loglevel=info",
    ]
    assert beat_env == {}


def test_build_service_web_respects_explicit_run_celery_in_web(monkeypatch):
    monkeypatch.setenv("RUN_CELERY_IN_WEB", "true")
    _, extra_env = proc_runner._build_service_command(
        "web", python_exe="/venv/bin/python", linux_script="start.sh", is_windows=False
    )
    assert extra_env == {}


def test_resolve_python_executable_prefers_repo_venv(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(proc_runner.sys, "prefix", "/global/python")
    monkeypatch.setattr(proc_runner.sys, "base_prefix", "/global/python")
    monkeypatch.setattr(proc_runner.sys, "executable", "/global/python/python")

    if proc_runner.os.name == "nt":
        venv_python = tmp_path / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = tmp_path / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("", encoding="utf-8")

    assert proc_runner._resolve_python_executable(tmp_path) == str(venv_python)


def test_find_honcho_watch_pids_finds_cmd_and_detects_dead_ancestor():
    if not hasattr(proc_runner, "_find_honcho_watch_pids"):
        return

    # honcho (100) -> cmd.exe (200) -> venv python shim (300) -> runner python (400)
    procs = {
        100: (50, "python.exe"),
        200: (100, "cmd.exe"),
        300: (200, "python.exe"),
        400: (300, "python.exe"),
    }
    watch_pids, already_dead = proc_runner._find_honcho_watch_pids(procs, 400)
    assert watch_pids == [200]
    assert already_dead is False

    # cmd.exe (200) already terminated by Honcho before runner finished booting
    procs_dead = {
        100: (50, "python.exe"),
        300: (200, "python.exe"),
        400: (300, "python.exe"),
    }
    _, already_dead_2 = proc_runner._find_honcho_watch_pids(procs_dead, 400)
    assert already_dead_2 is True


def test_serve_web_blocks_unmigrated_postgres(monkeypatch):
    monkeypatch.setenv("REQUIRE_POSTGRES", "true")
    monkeypatch.setenv("DATABASE_MIGRATION_COMPLETE", "false")
    assert proc_runner._serve_web_in_process() == 1


def test_hosting_readiness_audit_passes_with_updated_procfile():
    checks = hosting_readiness_agent.audit_workspace()
    assert all(check["passed"] for check in checks), [c for c in checks if not c["passed"]]
