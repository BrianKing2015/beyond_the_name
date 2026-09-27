# Beyond the Name

This project is focused on turning baby name CSV data into a cleaner, faster, queryable source of truth. The overall goal is to make it easier to search and analyze name records without depending on raw CSV files directly.

Before running the import pipeline, you need to populate the local documents folder with the source yob files used by the project. The exact source and download steps are intentionally left vague here so the repo remains portable and easy to use with local data.

The plan is to build a small, test-driven pipeline:

1. Read the raw CSV files stored in the documents folder.
2. Load the cleaned rows into a SQLite database.
3. Add read-only query helpers that expose safe, typed access to the database.

This keeps the system simple, predictable, and easy to test as new naming rules or CSV formats are introduced.

## Proposed project structure

```text
beyond_the_name/
├── documents/
│   └── baby_names.csv
├── src/
│   ├── __init__.py
│   ├── csv_reader.py
│   ├── sqlite_loader.py
│   └── query_helpers.py
├── tests/
│   ├── test_csv_reader.py
│   ├── test_sqlite_loader.py
│   └── test_query_helpers.py
├── README.md
├── requirements.txt
└── .gitignore
```

This is intentionally split into separate files so each stage has a distinct job:

- csv_reader.py: load and validate CSV data from disk.
- sqlite_loader.py: create tables, insert rows, and keep database setup logic isolated.
- query_helpers.py: expose safe, read-only queries for reporting and search.

## Step 1: Read the yob files from the documents folder

The first responsibility is to read the source yob files and turn them into structured Python data that we can trust.

### Goal

- Find the yob files in the documents directory.
- Read the files safely.
- Normalize the data types of each row into a consistent shape.
- Reject or flag malformed rows without crashing the import.

### Expected behavior

- The yob file path is resolved from the documents folder.
- Missing values are handled consistently.
- Empty rows are ignored.
- Invalid rows can be counted or logged without breaking the rest of the import.

### TDD tests for this step

Write tests before implementation. At minimum:

- test_yob_reader_reads_rows_from_documents_folder
- test_yob_reader_raises_clear_error_when_yob_file_is_missing
- test_yob_reader_normalizes_data_types
- test_yob_reader_skips_blank_rows
- test_yob_reader_handles_invalid_row_shapes

These tests should confirm the import layer produces clean records before the database layer ever sees them.

## Step 2: Feed the data into SQLite

Once the CSV rows are reliable, the next step is to persist them in a SQLite database. SQLite is a good fit because it is portable, easy to inspect, and works well for local search and reporting.

### Goal

- Create the database file in a known project path.
- Create a schema that reflects the CSV data.
- Insert each row in a repeatable, idempotent way.
- Separate database setup from CSV parsing.

### Expected behavior

- The database file is created if it does not exist.
- Tables are created with the correct columns and types.
- Duplicate rows are handled intentionally rather than silently duplicated.
- Import is repeatable: running it again should not leave the system in a confusing state.

### TDD tests for this step

- test_sqlite_loader_creates_database_and_tables
- test_sqlite_loader_inserts_rows_from_csv_records
- test_sqlite_loader_add_year
- test_sqlite_loader_inserts_rows_from_yob_file
- test_sqlite_loader_replaces_existing_data_cleanly
- test_sqlite_loader_handles_empty_record_set
- test_sqlite_loader_rejects_invalid_schema_data

These tests should protect the shape of the database and the integrity of the import process.

## Step 3: Create read-only query functions

The final layer should be a safe query API. No writing should happen here; this should only read from the database and return typed, clear results.

### Goal

- Pull rows back out of SQLite in a controlled way.
- Keep the database read-only from the query layer's perspective.
- Return structured Python objects or dictionaries instead of raw SQLite rows.
- Keep the search logic centralized in a few small helper functions.

### Expected behavior

- Queries are read-only and do not mutate the database.
- Search helpers allow targeted lookups such as by name, year, or gender.
- Results are returned with predictable types.
- Query wrappers fail clearly when the caller asks for a missing field or invalid filter.

### TDD tests for this step

- test_query_helpers_returns_rows_for_name_lookup
- test_query_helpers_returns_rows_for_year_filter
- test_query_helpers_returns_empty_list_when_no_match_exists
- test_query_helpers_raises_for_unknown_column
- test_query_helpers_uses_read_only_database_access

These tests are especially important because they define the public contract for the rest of the application.

## TDD workflow

Use a simple red-green-refactor cycle:

1. Write the failing tests for one behavior.
2. Implement the smallest code needed to satisfy it.
3. Run the focused test file.
4. Refactor only after the test passes.
5. Repeat for the next layer.

Example command flow:

```bash
pytest tests/test_csv_reader.py
pytest tests/test_sqlite_loader.py
pytest tests/test_query_helpers.py
```

This keeps the work incremental and makes it easier to see which stage caused a regression.

## Recommended implementation order

1. Build the CSV reader and its tests.
2. Build the SQLite loader and its tests.
3. Build the read-only query helpers and their tests.
4. Link the three pieces together in a single application flow:
   - read CSV → validate rows → insert into SQLite → run safe queries

## Success criteria

The project is successful when:

- CSV files from the documents folder are reliably ingested.
- The SQLite database is created with a stable schema.
- Search queries are easy to write and safe to execute.
- Each stage is protected by TDD tests that catch regressions early.

This plan creates a clean foundation for growing the dataset without scattering logic across unrelated files.

## Future TODOs

These are the next ideas worth exploring after the core ETL and query layers are stable. The best next candidates are the ones that are easy to express in SQL and immediately useful for browsing the dataset.

### High priority

1. TODO: wildcard name searches
   - Support prefix and suffix matching such as "A%" or "%a".
   - This is a natural extension of a name lookup and works well with SQL LIKE queries.
   - Good next step because it adds search flexibility without changing the schema.

2. TODO: top X names in a given year
   - Return the most popular names for a selected year and optionally by gender.
   - This is a strong reporting feature and a nice way to validate the raw database output.
   - Good next step because it is simple to reason about and highly useful for real-world data exploration.

3. TODO: first appearance vs peak year for a name
   - Track when a name first appears in the data and when it reaches its highest count.
   - This is the most interesting analytical query after search and ranking.
   - Good next step because it builds on the existing year and count fields without requiring new assumptions.

### Medium priority

4. TODO: male/female name variants
   - Explore how to relate names across genders, such as "Alex" / "Alexa", "Jordan" / "Jordyn", or shared stems.
   - This is likely a more nuanced matching problem and may require a dedicated name-normalization step.
   - Worth addressing after the simpler queries are in place.

5. TODO: name lifespan window analysis
   - Estimate how many people with a given name were alive within a rolling 80-year window.
   - This is a rich historical question, but it requires careful assumptions about birth year, age, and how to model life spans.
   - Best tackled after the core database and query features are settled.

### Suggested order

1. wildcard name searches
2. top X names in a given year
3. first appearance vs peak year for a name
4. male/female variant analysis
5. lifespan window analysis

This sequence keeps the work grounded in the most useful and least ambiguous SQL features before moving on to more speculative historical analysis.
