# tests/fixtures/

## Overview

This group of test fixtures across Java, Python, Ruby, and Rust provides a polyglot reference implementation of a user management system. The Java `App` class manages a collection of users via `addUser` and `getUserCount`, backed by an internal list. The Ruby `Router` class handles HTTP request dispatch by matching paths to handlers. The Python `TokenValidator` (with `require_auth` decorator) enforces OAuth2 authentication and token rotation. The Rust `User` struct and `ToJson` trait define the data model and serialization. Together they illustrate a microservices architecture where each language handles a distinct concern: data management, routing, authentication, and serialization.

## Modules
| File | Purpose |
|------|---------|
| tests/fixtures/sample_java/App.java | Sample Java fixture for parser testing |
| tests/fixtures/sample_ruby/app.rb | Sample Ruby fixture for parser testing |
| tests/fixtures/sample_rust/lib.rs | Sample Rust fixture for parser testing |
| tests/fixtures/sample_py/auth.py | Sample Python fixture for parser testing |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `tests/fixtures/sample_java/App.java::App` | class | Main application class managing user collection. |
| `tests/fixtures/sample_java/App.java::App.addUser` | method | Adds a user to the internal user list. |
| `tests/fixtures/sample_java/App.java::App.getUserCount` | method | Returns size of user list. |
| `tests/fixtures/sample_java/App.java::UserProfile` | interface | Interface defining user profile methods. |
| `tests/fixtures/sample_java/App.java::getDisplayName` | function | Returns the display name string. |
| `tests/fixtures/sample_java/App.java::getRole` | function | Returns the user role string. |
| `tests/fixtures/sample_java/App.java::Role` | enum | Enumeration of possible user roles. |
| `tests/fixtures/sample_py/auth.py::TokenValidator` | class | OAuth2 token validator and rotation handler. |
| `tests/fixtures/sample_py/auth.py::TokenValidator.refresh` | method | Rotates OAuth2 tokens by signing new payload. |
| `tests/fixtures/sample_py/auth.py::require_auth` | function | Decorator wrapping route with authentication check. |
| `tests/fixtures/sample_py/auth.py::wrapper` | function | Inner wrapper that calls original function. |
| `tests/fixtures/sample_ruby/app.rb::Router` | class | HTTP request router with route table. |
| `tests/fixtures/sample_ruby/app.rb::Router.initialize` | method | Initializes empty route table. |
| `tests/fixtures/sample_ruby/app.rb::Router.add_route` | method | Adds route path and handler to table. |
| `tests/fixtures/sample_ruby/app.rb::Router.dispatch` | method | Calls handler for matched path. |
| `tests/fixtures/sample_ruby/app.rb::Parser` | module | Module for parsing HTTP request strings. |
| `tests/fixtures/sample_ruby/app.rb::parse` | function | Strips and parses request string. |
| `tests/fixtures/sample_rust/lib.rs::User` | struct | Struct representing a user with name and age. |
| `tests/fixtures/sample_rust/lib.rs::age_difference` | function | Returns absolute age difference between two users. |
| `tests/fixtures/sample_rust/lib.rs::User.new` | method | Constructs User instance with name and age. |
| `tests/fixtures/sample_rust/lib.rs::User.is_adult` | method | Returns true if age >= 18. |
| `tests/fixtures/sample_rust/lib.rs::ToJson` | trait | Trait defining to_json serialization method. |
| `tests/fixtures/sample_rust/lib.rs::ToJson.to_json` | method_spec | Method specification for JSON serialization. |
| `tests/fixtures/sample_rust/lib.rs::User.to_json` | method | Serializes User to JSON string. |
| `tests/fixtures/sample_rust/lib.rs::Status` | enum | Enum with status codes Active and Inactive. |
| `tests/fixtures/sample_rust/lib.rs::UserResult` | type | Type alias for Result<User, String>. |
## Data Flows
- HTTP request arrives → Router.dispatch → matches path → calls handler (e.g., a lambda) → handler calls TokenValidator.require_auth → wraps original function
- TokenValidator.refresh → signs new payload via sign_payload → returns rotated token
- Client calls App.addUser → adds UserProfile to internal list → getUserCount calls size() on that list
- Rust user creation → User.new(name, age) → age_difference calculates absolute difference between two User instances → User.is_adult checks age >= 18
## Design Constraints
- Java `App.addUser` delegates to `List.add`; no duplicate or null checks — caller must ensure uniqueness and non-null.
- Python `require_auth` decorator returns `wrapper` that calls `func` only after authentication, but `func` is expected to be a callable (e.g., Flask route) — wrapping a non-callable will raise at decoration time.
- Ruby `Router.dispatch` calls `.call` on the handler; handlers must respond to `call` (e.g., procs or objects with `call` method).
- Rust `User` struct is used by value in `age_difference`, which computes absolute difference via `(a.age - b.age).abs()` — no lifetime or borrowing issues.
- Rust `UserResult` is a type alias (`Result<User, String>`), not a newtype — pattern matching on Result is required; there is no custom error type.
- Rust `ToJson` trait has no default implementation for `to_json`; each implementor (e.g., User) must define it manually.
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
