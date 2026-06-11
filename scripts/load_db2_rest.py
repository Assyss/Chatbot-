#!/usr/bin/env python3
"""Load the AV-01 ICL sample data into IBM Db2 through the Db2 REST API."""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


TERMINAL_STATES = {
    "completed",
    "complete",
    "completed_with_errors",
    "done",
    "failed",
    "error",
    "success",
    "succeeded",
    "canceled",
    "cancelled",
}
FAILED_STATES = {"completed_with_errors", "failed", "error", "canceled", "cancelled"}


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def normalize_hostname(hostname: str) -> str:
    value = hostname.strip()
    if "://" in value:
        parsed = urlparse(value)
        value = parsed.netloc or parsed.path
    return value.strip("/")


def request_json(
    method: str,
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any] | None = None,
    *,
    insecure: bool = False,
    timeout: int = 60,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    context = ssl._create_unverified_context() if insecure else None

    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body) if response_body else {}
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed with HTTP {exc.code}: {error_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{method} {url} failed: {exc.reason}") from exc


def get_token(args: argparse.Namespace, base_url: str) -> str:
    if args.token:
        return args.token

    payload = {
        "userid": args.username,
        "password": args.password,
    }
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "x-deployment-id": args.deployment_id,
    }
    response = request_json(
        "POST",
        f"{base_url}/dbapi/v4/auth/tokens",
        headers,
        payload,
        insecure=args.insecure,
        timeout=args.timeout,
    )
    token = response.get("token")
    if not token:
        raise RuntimeError(f"Token was not present in Db2 response: {json.dumps(response, indent=2)}")
    return str(token)


def submit_sql_job(
    args: argparse.Namespace,
    base_url: str,
    token: str,
    sql: str,
    *,
    stop_on_error: str | None = None,
) -> str:
    payload = {
        "commands": sql,
        "separator": args.separator,
        "limit": args.limit,
        "stop_on_error": stop_on_error or args.stop_on_error,
    }
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "authorization": f"Bearer {token}",
        "x-deployment-id": args.deployment_id,
    }
    response = request_json(
        "POST",
        f"{base_url}/dbapi/v4/sql_jobs",
        headers,
        payload,
        insecure=args.insecure,
        timeout=args.timeout,
    )
    job_id = response.get("id") or response.get("job_id")
    if not job_id:
        raise RuntimeError(f"SQL job id was not present in Db2 response: {json.dumps(response, indent=2)}")
    return str(job_id)


def fetch_sql_job(args: argparse.Namespace, base_url: str, token: str, job_id: str) -> dict[str, Any]:
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
        "x-deployment-id": args.deployment_id,
    }
    return request_json(
        "GET",
        f"{base_url}/dbapi/v4/sql_jobs/{job_id}",
        headers,
        insecure=args.insecure,
        timeout=args.timeout,
    )


def job_state(job: dict[str, Any]) -> str:
    for key in ("status", "state", "job_status"):
        value = job.get(key)
        if value:
            return str(value).lower().replace(" ", "_").replace("-", "_")
    return ""


def wait_for_job(args: argparse.Namespace, base_url: str, token: str, job_id: str) -> dict[str, Any]:
    deadline = time.monotonic() + args.wait_timeout
    last_job: dict[str, Any] = {}

    while time.monotonic() < deadline:
        last_job = fetch_sql_job(args, base_url, token, job_id)
        state = job_state(last_job)
        if state in TERMINAL_STATES:
            return last_job
        time.sleep(args.poll_interval)

    raise TimeoutError(
        f"Timed out waiting for SQL job {job_id}. Last response: {json.dumps(last_job, indent=2)}"
    )


def required(value: str | None, name: str) -> str:
    if value:
        return value
    raise SystemExit(f"Missing {name}. Set it in .env or pass the matching command-line option.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=".env", help="Optional env file to load before reading settings.")
    parser.add_argument("--hostname", default=os.getenv("DB2_HOSTNAME"), help="Db2 REST API hostname.")
    parser.add_argument("--deployment-id", default=os.getenv("DB2_DEPLOYMENT_ID"), help="Db2 deployment id.")
    parser.add_argument("--username", default=os.getenv("DB2_USERNAME"), help="Db2 service credential username.")
    parser.add_argument("--password", default=os.getenv("DB2_PASSWORD"), help="Db2 service credential password.")
    parser.add_argument("--token", default=os.getenv("DB2_TOKEN"), help="Optional existing Db2 auth token.")
    parser.add_argument("--sql-file", default="sql/schema_and_seed.sql", help="SQL file to submit.")
    parser.add_argument("--reset-sql-file", default="sql/reset.sql", help="SQL file used to drop existing tables.")
    parser.add_argument("--skip-reset", action="store_true", help="Do not run the reset SQL before loading data.")
    parser.add_argument("--separator", default=";", help="SQL statement separator.")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum rows returned by Db2 REST API.")
    parser.add_argument(
        "--stop-on-error",
        choices=("yes", "no"),
        default="yes",
        help="Stop the data load if Db2 reports an error.",
    )
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Seconds between job polling attempts.")
    parser.add_argument("--wait-timeout", type=float, default=120.0, help="Maximum seconds to wait for job completion.")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP request timeout in seconds.")
    parser.add_argument("--insecure", action="store_true", help="Disable TLS certificate verification.")
    return parser


def parse_args() -> argparse.Namespace:
    env_parser = argparse.ArgumentParser(add_help=False)
    env_parser.add_argument("--env-file", default=".env")
    env_args, _ = env_parser.parse_known_args()
    load_env_file(Path(env_args.env_file))
    return build_parser().parse_args()


def main() -> int:
    args = parse_args()
    args.hostname = required(args.hostname, "DB2_HOSTNAME")
    args.deployment_id = required(args.deployment_id, "DB2_DEPLOYMENT_ID")
    args.token = args.token or None
    if not args.token:
        args.username = required(args.username, "DB2_USERNAME")
        args.password = required(args.password, "DB2_PASSWORD")

    hostname = normalize_hostname(args.hostname)
    base_url = f"https://{hostname}"

    token = get_token(args, base_url)
    if not args.skip_reset:
        reset_sql = Path(args.reset_sql_file).read_text(encoding="utf-8")
        print(f"Submitting reset SQL from {args.reset_sql_file} to {hostname}...")
        reset_job_id = submit_sql_job(args, base_url, token, reset_sql, stop_on_error="no")
        reset_job = wait_for_job(args, base_url, token, reset_job_id)
        print(f"Reset job finished with state: {job_state(reset_job) or 'unknown'}")

    sql = Path(args.sql_file).read_text(encoding="utf-8")
    print(f"Submitting SQL from {args.sql_file} to {hostname}...")
    job_id = submit_sql_job(args, base_url, token, sql)
    print(f"SQL job submitted: {job_id}")

    job = wait_for_job(args, base_url, token, job_id)
    print(json.dumps(job, indent=2, ensure_ascii=False))

    state = job_state(job)
    if state in FAILED_STATES:
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - keep CLI errors readable.
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
