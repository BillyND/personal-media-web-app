from app.db.connection import get_connection

SCHEMA = """
create table if not exists jobs (
  id text primary key,
  type text not null,
  status text not null,
  input_url text,
  input_text text,
  output_dir text not null,
  error_message text,
  created_at text not null,
  started_at text,
  completed_at text
);

create table if not exists job_files (
  id text primary key,
  job_id text not null references jobs(id) on delete cascade,
  kind text not null,
  path text not null,
  created_at text not null
);

create index if not exists idx_jobs_status_created_at on jobs(status, created_at);
create index if not exists idx_job_files_job_id on job_files(job_id);
"""


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(SCHEMA)
