# tests/fixtures/

## Overview

This module implements the core components of a polyglot microservices platform for user management and authentication. The Java `App` class provides an in-memory user registry via `addUser` and `getUserCount`; the Python `TokenValidator` handles OAuth2 token refresh with cryptographic signing; the Ruby `Router` manages HTTP request dispatching to registered handlers; and the Rust `User` struct offers a fast, serializable data model with age validation and JSON output via the `ToJson` trait. Together, they form a lightweight backend system where the router receives client requests, the validator guards endpoints, the app manages users, and the Rust library supplies efficient data structures.

## Modules
| File | Purpose |
|------|---------|
| tests/fixtures/sample_ruby/app.rb | Ruby HTTP request routing and parsing |
| tests/fixtures/sample_py/auth.py | OAuth2 token validation with route decorator |
| tests/fixtures/sample_java/App.java | Java main class managing users with display name and role |
| tests/fixtures/sample_rust/lib.rs | Rust function for user age difference calculation |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `tests/fixtures/sample_java/App.java::App` | class | Main application class managing users with add/getUserCount |
| `tests/fixtures/sample_java/App.java::App.addUser` | method | Adds a user name to the internal users list |
| `tests/fixtures/sample_java/App.java::App.getUserCount` | method | Returns the size of the users list |
| `tests/fixtures/sample_java/App.java::UserProfile` | interface | Interface for user profile with display name and role |
| `tests/fixtures/sample_java/App.java::getDisplayName` | function | Returns the display name string |
| `tests/fixtures/sample_java/App.java::getRole` | function | Returns the user role string |
| `tests/fixtures/sample_java/App.java::Role` | enum | Enum defining user roles (ADMIN, USER, GUEST) |
| `tests/fixtures/sample_py/auth.py::TokenValidator` | class | Validates and rotates OAuth2 tokens using signing |
| `tests/fixtures/sample_py/auth.py::TokenValidator.refresh` | method | Rotates OAuth2 refresh token by signing payload |
| `tests/fixtures/sample_py/auth.py::require_auth` | function | Decorator that guards routes by calling wrapped function |
| `tests/fixtures/sample_py/auth.py::wrapper` | function | Wrapper function that calls the guarded route function |
| `tests/fixtures/sample_ruby/app.rb::Router` | class | HTTP request router with route registration and dispatch |
| `tests/fixtures/sample_ruby/app.rb::Router.initialize` | method | Initializes empty routes hash and handler keys array |
| `tests/fixtures/sample_ruby/app.rb::Router.add_route` | method | Registers a route with path and handler block |
| `tests/fixtures/sample_ruby/app.rb::Router.dispatch` | method | Dispatches request to matching handler, calls handler |
| `tests/fixtures/sample_ruby/app.rb::Parser` | module | Module that parses incoming HTTP requests |
| `tests/fixtures/sample_ruby/app.rb::parse` | function | Strips leading/trailing whitespace from request string |
| `tests/fixtures/sample_rust/lib.rs::User` | struct | Struct representing a user with name and age fields |
| `tests/fixtures/sample_rust/lib.rs::age_difference` | function | Calculates absolute age difference between two Users |
| `tests/fixtures/sample_rust/lib.rs::User.new` | method | Creates a new User instance with given name and age |
| `tests/fixtures/sample_rust/lib.rs::User.is_adult` | method | Returns true if user age is 18 or older |
| `tests/fixtures/sample_rust/lib.rs::ToJson` | trait | Trait for objects that can be serialized to JSON |
| `tests/fixtures/sample_rust/lib.rs::ToJson.to_json` | method_spec | Method signature for converting to JSON string |
| `tests/fixtures/sample_rust/lib.rs::User.to_json` | method | Converts User struct to JSON string representation |
| `tests/fixtures/sample_rust/lib.rs::Status` | enum | Enum representing status codes (Active, Inactive, Pending) |
| `tests/fixtures/sample_rust/lib.rs::UserResult` | type | Type alias for Result type with User and Error |
## Data Flows
- Client POST /users → Ruby Router.dispatch → Java App.addUser (validated by Python require_auth decorator) → returns user count
- Client request with expired token → Python TokenValidator.refresh → signs payload with sign_payload → returns new token (Rust User.to_json serializes audit log)
- Ruby Router receives GET /users/count → Router.dispatch calls handler → handler calls Java App.getUserCount → returns integer
- Rust User.new creates user → is_adult check → age_difference computed → User.to_json serializes for response via Python or Java
## Design Constraints
- Java App's internal `users` list (ArrayList) is not thread-safe; concurrent addUser calls may corrupt state without external synchronization.
- Python TokenValidator.refresh relies on `sign_payload` which assumes a pre‑loaded private key; no key rotation logic is present in the module.
- Ruby Router.dispatch matches routes by key equality (hash lookup); no wildcard or parameterised path support is exposed.
- Rust User.age_difference uses `abs` internally; caller must ensure no overflow on i32 age values (though unrealistic, may panic on extreme inputs).
- Python `require_auth` decorator calls `func` directly without any retry or fallback; any exception from the guarded function propagates unhandled.
- Rust User.to_json returns a simple string without error handling; serialization failure (e.g., non‑UTF‑8) is not indicated to caller.
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
