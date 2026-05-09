# tests/fixtures/

## Overview

This module provides synthetic, multi-language code samples designed for testing a code analysis tool that extracts symbols, call graphs, and type relationships. Each file exercises language-specific constructs: Java demonstrates generic List operations and interfaces (App, UserProfile), Python showcases decorators (require_auth) and token authentication (TokenValidator), Ruby implements a basic routing dispatch (Router), and Rust models a User struct with trait serialization (ToJson) and an enum (Status). Together, they validate the parser's ability to handle OOP, functional, and type system patterns across different languages.

## Modules
| File | Purpose |
|------|---------|
| tests/fixtures/sample_rust/lib.rs |  |
| tests/fixtures/sample_ruby/app.rb |  |
| tests/fixtures/sample_py/auth.py |  |
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
- Python: require_auth decorator wraps a function -> wrapper calls the original function after token validation, with TokenValidator.refresh calling sign_payload
- Java: App.addUser adds a UserProfile to internal list -> App.getUserCount calls size() on the list to return count
- Ruby: Router.dispatch receives a request path -> matches against stored routes -> calls the associated handler with call
- Rust: User::new creates a User instance -> User.to_json serializes the User to a JSON string using the ToJson trait method
## Design Constraints
- Java App does not enforce uniqueness; duplicate UserProfile objects can be added to the same list.
- Python require_auth decorator does not handle exceptions from func; wrapper will propagate any error from the original function.
- Ruby Router.dispatch assumes stored handler responds to `call`; no type checking on route registration.
- Rust age_difference returns an i32 difference; if ages are equal returns 0, but overflow for large i32 values is not handled.
- Rust User.to_json serializes fields in declaration order (name, age, status); order is not guaranteed by the ToJson trait signature.
- Python TokenValidator.refresh calls sign_payload which is not defined in this module; must be provided externally.
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
