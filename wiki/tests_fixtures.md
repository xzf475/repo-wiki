# tests/fixtures/

## Modules
| File | Purpose |
|------|---------|
| tests/fixtures/sample_py/auth.py |  |
| tests/fixtures/sample_java/App.java |  |
| tests/fixtures/sample_rust/lib.rs |  |
| tests/fixtures/sample_ruby/app.rb |  |
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
