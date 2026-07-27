# tests/fixtures/

## Overview

This test fixtures module provides a curated set of small, multi-language code samples (Java, Python, Ruby, Rust) designed to validate the symbol extraction, type inference, and call-graph reconstruction capabilities of the static analysis tool. Key classes include `App` (Java) demonstrating class/interface/enum relationships, `TokenValidator` (Python) testing decorator and method call chains, `Router` (Ruby) verifying dispatch and route registration, and `User` (Rust) exercising structs, traits, enums, and type aliases. The module exists to ensure the analyzer correctly handles cross-language constructs, method overrides, and implicit dependencies (e.g., `UserProfile` interface without concrete implementation) that appear in real-world codebases but are often omitted from simpler unit tests. It fits as a regression fixture suite that the tool's testing harness loads and analyzes, covering edge cases like empty argument lists (`UserResult`), trait method specifications (`ToJson.to_json`), and standalone functions (`getDisplayName`) outside classes.

## Modules
| File | Purpose |
|------|---------|
| tests/fixtures/sample_rust/lib.rs |  |
| tests/fixtures/sample_java/App.java |  |
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
- Java: `App.addUser` → calls `add` on internal collection → `App.getUserCount` → calls `size` on same collection → returns count
- Python: `require_auth` decorator → wraps function `func` via `wrapper` → `TokenValidator.refresh` → calls `sign_payload` (external) → validates token
- Ruby: `Router.dispatch` → iterates registered routes → calls `call` on matched route handler → routes are added via `Router.add_route`
- Rust: `User.to_json` → implements trait `ToJson` → returns JSON string → `age_difference` (standalone) computes age gap between two `User` instances
## Design Constraints
- Java `UserProfile` is an interface with no implementing class; any code that attempts to instantiate it will fail at runtime, but the analyzer must still extract its method signatures (`getDisplayName`, `getRole`).
- The `require_auth` decorator (Python) returns the wrapper function without actually performing authentication; it is a structural test for decorator detection, not a functional security mechanism.
- Ruby `Router#initialize` has an empty argument list, but the `add_route` method is never called inside the fixture; the analyzer must infer routes from static registration only, not from runtime execution.
- Rust `UserResult` is a type alias for `Result<User, String>`, but nowhere in the code is it used; it exists solely to test type alias symbol extraction.
- The `parse` function (Ruby) calls `strip` on its input but does not check for nil; an edge case that the analyzer must handle gracefully (no crash on missing string method detection).
- `age_difference` (Rust) is a public function that takes two `User` references but is never called internally; the analyzer must still record it as a callable symbol with no outgoing calls.
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
