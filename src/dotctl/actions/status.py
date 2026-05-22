from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
import json

from dotctl.paths import app_profile_directory, app_config_file
from dotctl.handlers.config_handler import conf_reader, Config
from dotctl.handlers.git_handler import get_repo, is_git_repo
from dotctl.handlers.status_handler import (
    DriftReport,
    StatusCode,
    Severity,
    status_icon,
    build_drift_report,
)
from dotctl.utils import log


@dataclass
class HealthStatus:
    healthy: bool
    code: StatusCode
    severity: Severity
    message: str
    errors: list[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        return len(self.errors) > 0


@dataclass
class ProfileInfo:
    profile_dir: Path
    active_profile: str | None
    remote_url: str | None
    is_remote: bool
    health: HealthStatus

    def has_remote(self) -> bool:
        return self.is_remote and self.remote_url is not None


@dataclass
class ConfigInfo:
    config_path: Path
    health: HealthStatus


@dataclass
class StatusReport:
    profile: ProfileInfo
    config: ConfigInfo
    drift: DriftReport | None
    # symlink: CheckResult
    # permissions: CheckResult
    # hooks: CheckResult

    def is_healthy(self) -> bool:
        return self.profile.health.healthy and self.config.health.healthy

    def can_analyze_drift(self) -> bool:
        return self.drift is not None


@dataclass
class StatusProps:
    profile_dir: Path
    json: bool
    short: bool


status_default_props = StatusProps(
    profile_dir=Path(app_profile_directory),
    json=False,
    short=False,
)


def render_full(report: StatusReport):

    profile = report.profile
    config = report.config

    print(f"{status_icon(profile.health.healthy)} " f"profile: {profile.health.message}")

    print(f"{status_icon(config.health.healthy)} " f"config: {config.health.message}")

    if profile.active_profile:
        print(f"✔ active profile: {profile.active_profile}")

    if profile.has_remote():
        print(f"✔ remote: {profile.remote_url}")

    if not report.can_analyze_drift():
        print("\n⚠ drift analysis unavailable")
        return

    drift = report.drift

    print()

    if drift is None:
        return

    if drift.is_clean():
        print("✔ system: in sync")
    else:
        print("⚠ system: drift detected")

    print(f"✔ synced files: {len(drift.synced_files)}")

    if drift.modified_files:
        print(f"⚠ modified files: {len(drift.modified_files)}")
    else:
        print("✔ modified files: none")

    if drift.missing_files:
        print(f"⚠ missing files: {len(drift.missing_files)}")
    else:
        print("✔ missing files: none")

    changed = drift.modified_files + drift.missing_files

    if changed:

        grouped = Counter(f.state.value for f in changed)

        print("\nChanged files:")

        for f in changed:
            print(f"  - {f.path}")

        print()

        for state, count in grouped.items():
            print(f"  {state}: {count}")


def render_short(report: StatusReport):

    profile = report.profile
    config = report.config

    if not profile.health.healthy:
        print(f"profile: {profile.health.message}")
        return

    if not config.health.healthy:
        print(f"config: {config.health.message}")
        return

    if not report.can_analyze_drift():
        print("drift: unavailable")
        return

    drift = report.drift

    if drift is None:
        print("drift: unavailable")
        return

    if drift.is_clean():
        print("✔ clean")
        return

    print(
        f"modified={len(drift.modified_files)} "
        f"missing={len(drift.missing_files)} "
        f"synced={len(drift.synced_files)}"
    )


def render_json(report: StatusReport):

    def encode_health(health: HealthStatus):
        return {
            "healthy": health.healthy,
            "code": health.code.value,
            "severity": health.severity.value,
            "message": health.message,
            "errors": health.errors,
        }

    def encode_file(f):
        return {
            "group": f.group,
            "entry": f.entry,
            "path": str(f.path),
            "state": f.state.value,
        }

    output = {
        "profile": {
            "profile_dir": str(report.profile.profile_dir),
            "active_profile": report.profile.active_profile,
            "remote_url": report.profile.remote_url,
            "is_remote": report.profile.is_remote,
            "health": encode_health(report.profile.health),
        },
        "config": {
            "config_path": str(report.config.config_path),
            "health": encode_health(report.config.health),
        },
        "drift": None,
    }

    if report.drift:

        drift = report.drift

        output["drift"] = {
            "clean": drift.is_clean(),
            "total_files": drift.total_files(),
            "modified_files": [encode_file(f) for f in drift.modified_files],
            "missing_files": [encode_file(f) for f in drift.missing_files],
            "synced_files": [encode_file(f) for f in drift.synced_files],
        }

    print(json.dumps(output, indent=2))


def collect_profile_info(profile_dir: Path, errors: list[str]) -> ProfileInfo:
    health = HealthStatus(
        healthy=True,
        code=StatusCode.OK,
        severity=Severity.INFO,
        message="ok",
    )

    active_profile = None
    remote_url = None
    is_remote = False

    try:

        if not profile_dir.exists():
            health = HealthStatus(
                healthy=False,
                code=StatusCode.REPO_NOT_FOUND,
                severity=Severity.ERROR,
                message="profile directory not found",
            )

        elif not profile_dir.is_dir():
            health = HealthStatus(
                healthy=False,
                code=StatusCode.REPO_INVALID_DIRECTORY,
                severity=Severity.ERROR,
                message="invalid profile directory",
            )

        elif not is_git_repo(profile_dir):
            health = HealthStatus(
                healthy=False,
                code=StatusCode.REPO_NOT_GIT,
                severity=Severity.ERROR,
                message="not a git repository",
            )

        else:

            repo = get_repo(profile_dir)

            if repo.bare:
                health = HealthStatus(
                    healthy=False,
                    code=StatusCode.REPO_BARE,
                    severity=Severity.ERROR,
                    message="bare repository",
                )

            else:
                try:
                    active_profile = repo.active_branch.name
                except Exception:
                    active_profile = None

                try:
                    if repo.remotes:
                        origin = next(
                            (r for r in repo.remotes if r.name == "origin"),
                            None,
                        )
                        if origin:
                            remote_url = origin.url
                            is_remote = True
                except Exception as e:
                    errors.append(f"remote inspection failed: {e}")

    except Exception as e:

        health = HealthStatus(
            healthy=False,
            code=StatusCode.ERROR,
            severity=Severity.ERROR,
            message="profile check failed",
            errors=[str(e)],
        )

        errors.append(f"Profile check failed: {e}")

    return ProfileInfo(
        profile_dir=profile_dir,
        active_profile=active_profile,
        remote_url=remote_url,
        is_remote=is_remote,
        health=health,
    )


def collect_config_info(errors: list[str]) -> tuple[ConfigInfo, Config | None]:

    config_path = Path(app_config_file)

    health = HealthStatus(
        healthy=True,
        code=StatusCode.OK,
        severity=Severity.INFO,
        message="ok",
    )

    config = None

    try:

        if not config_path.exists():
            health = HealthStatus(
                healthy=False,
                code=StatusCode.CONFIG_NOT_FOUND,
                severity=Severity.ERROR,
                message="config file not found",
            )

        elif not config_path.is_file():
            health = HealthStatus(
                healthy=False,
                code=StatusCode.CONFIG_INVALID_FILE,
                severity=Severity.ERROR,
                message="invalid config file",
            )

        else:

            config = conf_reader(config_file=config_path)

            if not config:
                health = HealthStatus(
                    healthy=False,
                    code=StatusCode.CONFIG_UNSUPPORTED,
                    severity=Severity.ERROR,
                    message="invalid config format",
                )

    except Exception as e:

        health = HealthStatus(
            healthy=False,
            code=StatusCode.CONFIG_PARSE_FAILED,
            severity=Severity.ERROR,
            message="config parsing failed",
            errors=[str(e)],
        )

        errors.append(f"Config check failed: {e}")

    return (
        ConfigInfo(
            config_path=config_path,
            health=health,
        ),
        config,
    )


def status(props: StatusProps) -> None:

    errors: list[str] = []

    profile_info = collect_profile_info(props.profile_dir, errors)

    config_info, config = collect_config_info(errors)

    drift_report = None

    try:
        if profile_info.health.healthy and config_info.health.healthy and config:

            drift_report = build_drift_report(
                props.profile_dir,
                config,
            )

    except Exception as e:
        errors.append(f"Drift check failed: {e}")

    report = StatusReport(
        profile=profile_info,
        config=config_info,
        drift=drift_report,
    )

    if props.json:
        render_json(report)
    elif props.short:
        render_short(report)
    else:
        render_full(report)
