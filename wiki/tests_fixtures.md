# tests/fixtures/

## Overview

This fixture module provides minimal, cross-language sample code (Python, Ruby, Java, Rust) designed to test a multi-language static analysis tool. It models common backend patterns—token-based authentication (Python `TokenValidator` with `refresh`), HTTP routing (Ruby `Router` with `add_route`/`dispatch`), user profile management (Java `App` storing `UserProfile` objects, with `Role` enum), and a Rust `User` struct implementing `ToJson` for serialization. Each language snippet is self-contained and independent, allowing the tool to verify symbol resolution, call-graph extraction, and type inference across different syntaxes without external dependencies.

## Modules
| File | Purpose |
|------|---------|
| tests/fixtures/sample_py/auth.py |  |
| tests/fixtures/sample_rust/lib.rs |  |
| tests/fixtures/sample_ruby/app.rb |  |
| tests/fixtures/sample_java/App.java |  |
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
- require_auth decorator → calls wrapper → calls func, illustrating decorator pattern call interception in Python
- Router.dispatch(path) → iterates routes → calls stored lambda (call), demonstrating dynamic dispatch in Ruby
- App.addUser(name, role) → creates UserProfile (anonymous class) → adds to ArrayList, modeling in-memory user store in Java
- User.to_json() → formats fields (name, age, status) into JSON string, using Rust's trait implementation for serialization
## Design Constraints
- TokenValidator.refresh() assumes `sign_payload` is a callable in scope; no fallback or error handling is provided (minimal test stub).
- Router.initialize accepts no arguments; routes are stored as a hash without thread safety—single-threaded test context only.
- Java App.getUserCount() returns the raw size of the ArrayList; no null or duplicate checks on addUser (duplicate names allowed).
- Rust age_difference(a, b) is a pure function that returns absolute difference; it does not handle negative ages or overflow (u8).
- The Rust Status enum has no default or unknown variant; any serialization of an uninitialized User would panic (no TryFrom/Default).
- Ruby parse(str) calls strip on the input but does not handle nil—calling parse(nil) would raise NoMethodError.
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
