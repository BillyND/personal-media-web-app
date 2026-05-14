import subprocess


def run_command(args: list[str], input_text: str | None = None) -> str:
    result = subprocess.run(args, input=input_text, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Command failed"
        raise RuntimeError(message[:1000])
    return result.stdout
