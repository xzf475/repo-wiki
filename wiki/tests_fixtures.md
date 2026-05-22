# tests/fixtures/

## Overview

These fixtures provide minimal, self-contained cross-language code examples used to unit-test the symbol extraction pipeline. Each file exercises a distinct language feature set: Java (`App.java`) demonstrates classes, interfaces, enums, and methods that delegate to built-in calls (e.g., `add`, `size`); Python (`auth.py`) shows a decorator and a class with a private method calling an undefined helper; Ruby (`app.rb`) implements a simple router with lambda dispatch; Rust (`lib.rs`) features structs, impl blocks, trait definitions, type aliases, and an enum. The group exists to ensure the extractor correctly handles language-specific syntactic patterns while producing uniform symbol records with `calls` fields. By keeping fixtures small and intentionally incomplete (e.g., `sign_payload` not defined anywhere), the tests validate that the extractor captures external references without requiring resolution.

## Modules
| File | Purpose |
|------|---------|
| tests/fixtures/sample_java/App.java |  |
| tests/fixtures/sample_rust/lib.rs |  |
| tests/fixtures/sample_ruby/app.rb |  |
| tests/fixtures/sample_py/auth.py |  |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `tests/fixtures/sample_java/App.java::App` | class |  |
| `tests/fixtures/sample_java/App.java::App.addUser` | method |  |
| `tests/fixtures/sample_java/App.java::App.getUserCount` | method |  |
| `tests/fixtures/sample_java/App.java::UserProfile` | interface |  |
| `tests/fixtures/sample_java/App.java::getDisplayName` | function |  |
| `tests/fixtures/sample_java/App.java::getRole` | function |  |
| `tests/fixtures/sample_java/App.java::Role` | enum |  |
| `tests/fixtures/sample_py/auth.py::TokenValidator` | class |  |
| `tests/fixtures/sample_py/auth.py::TokenValidator.refresh` | method |  |
| `tests/fixtures/sample_py/auth.py::require_auth` | function |  |
| `tests/fixtures/sample_py/auth.py::wrapper` | function |  |
| `tests/fixtures/sample_ruby/app.rb::Router` | class |  |
| `tests/fixtures/sample_ruby/app.rb::Router.initialize` | method |  |
| `tests/fixtures/sample_ruby/app.rb::Router.add_route` | method |  |
| `tests/fixtures/sample_ruby/app.rb::Router.dispatch` | method |  |
| `tests/fixtures/sample_ruby/app.rb::Parser` | module |  |
| `tests/fixtures/sample_ruby/app.rb::parse` | function |  |
| `tests/fixtures/sample_rust/lib.rs::User` | struct |  |
| `tests/fixtures/sample_rust/lib.rs::age_difference` | function |  |
| `tests/fixtures/sample_rust/lib.rs::User.new` | method |  |
| `tests/fixtures/sample_rust/lib.rs::User.is_adult` | method |  |
| `tests/fixtures/sample_rust/lib.rs::ToJson` | trait |  |
| `tests/fixtures/sample_rust/lib.rs::ToJson.to_json` | method_spec |  |
| `tests/fixtures/sample_rust/lib.rs::User.to_json` | method |  |
| `tests/fixtures/sample_rust/lib.rs::Status` | enum |  |
| `tests/fixtures/sample_rust/lib.rs::UserResult` | type |  |
## Data Flows
- Test harness → App.addUser → calls 'add' on internal list (Java)
- HTTP request simulated → Router.dispatch → calls 'call' on matched route lambda (Ruby)
- Auth check → TokenValidator.refresh → calls undefined 'sign_payload' (Python)
- Age calculation → age_difference → accesses User.age fields (Rust)
## Design Constraints
- Fixtures must have zero external dependencies (no imports beyond language standard library) to guarantee portability across test environments.
- All `calls` entries are string literals extracted from source; they may reference methods that do not exist in the fixture set (e.g., `sign_payload`), as the goal is to record syntactic calls, not resolve them.
- Java interface `UserProfile` and Rust trait `ToJson` define no implementation and serve only to verify the extractor recognizes interface/trait symbol types.
- Ruby's `parse` function calls `strip` (a String method) but that call is recorded as a raw string — the extractor does not distinguish built-in from user-defined calls.
- Rust `UserResult` type alias is included to ensure `type` symbols are captured alongside struct/enum/trait symbols.
- Symbol IDs are globally unique by prepending the file path; duplicate simple names (e.g., `getDisplayName` in Java vs Ruby) are allowed only across different files.
## Relationships
- **Calls:** add, call, func, sign_payload, size, strip
- **Called by:** indexer/ast_parser.py::parse_file, indexer/go_parser.py::parse_go_file, indexer/java_parser.py::parse_java_file, indexer/js_parser.py::parse_js_file, indexer/ruby_parser.py::parse_ruby_file, indexer/rust_parser.py::parse_rust_file
- **Imports from:** hashlib, import java.util.ArrayList;, import java.util.List;, use serde::{Deserialize, Serialize};, use std::collections::HashMap;, utils.crypto.sign_payload
## Entry Points
- `App`
- `getDisplayName`
- `getRole`
- `TokenValidator`
- `require_auth`
- `wrapper`
- `Router`
- `age_difference`
