# EventWatch input files

Place the user-provided EventWatch files in this directory for local
BankruptcyHunter runs. Required files are validated by `src.file_loader` with
clear errors if they are missing:

- `eventwatch_rulebook(4).py`
- `eventwatch_industries(1).csv`
- `bankruptcy_events_100_full.csv`

Optional internal tracker workbooks may also be placed here. Missing optional
trackers are logged as warnings and do not crash the application:

- `EventWatch Notifications Tracker (2021 - onwards) - Copy (3)(1).xlsx`
- `2025 - EventWatch Complaints (3)(1).xlsx`
