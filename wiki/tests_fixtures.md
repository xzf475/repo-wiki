# tests/fixtures/

## Modules
| File | Purpose |
|------|---------|
| tests/fixtures/sample_java/App.java |  |
| tests/fixtures/sample_py/auth.py |  |
| tests/fixtures/sample_ruby/app.rb |  |
| tests/fixtures/sample_rust/lib.rs |  |
## Key Symbols
| ID | Type | Description |
|----|------|-------------|
| `tests/fixtures/sample_java/App.java::App` | class | Main application class that manages users. |
| `tests/fixtures/sample_java/App.java::App.addUser` | method | Adds a user to the application. |
| `tests/fixtures/sample_java/App.java::App.getUserCount` | method | Returns the number of registered users. |
| `tests/fixtures/sample_java/App.java::UserProfile` | interface | Represents a user profile. |
| `tests/fixtures/sample_java/App.java::UserProfile.getDisplayName` | method | Gets the display name. |
| `tests/fixtures/sample_java/App.java::UserProfile.getRole` | method | Gets the user role. |
| `tests/fixtures/sample_java/App.java::Role` | enum | Defines user roles. |
| `tests/fixtures/sample_py/auth.py::TokenValidator` | class | Validates and rotates OAuth2 tokens. |
| `tests/fixtures/sample_py/auth.py::TokenValidator.refresh` | method | Rotates OAuth2 refresh tokens. |
| `tests/fixtures/sample_py/auth.py::require_auth` | function | Decorator that guards routes. |
| `tests/fixtures/sample_py/auth.py::wrapper` | function |  |
| `tests/fixtures/sample_ruby/app.rb::Router` | class | Handles HTTP request routing. |
| `tests/fixtures/sample_ruby/app.rb::Router.initialize` | method |  |
| `tests/fixtures/sample_ruby/app.rb::Router.add_route` | method | Registers a route with the given path and handler. |
| `tests/fixtures/sample_ruby/app.rb::Router.dispatch` | method | Dispatches the request to the matching handler. |
| `tests/fixtures/sample_ruby/app.rb::Parser` | module | Parses incoming HTTP requests. |
| `tests/fixtures/sample_ruby/app.rb::Parser.parse` | method |  |
| `tests/fixtures/sample_rust/lib.rs::User` | struct | Represents a user in the system. |
| `tests/fixtures/sample_rust/lib.rs::age_difference` | function | Calculates the age difference between two users. |
| `tests/fixtures/sample_rust/lib.rs::User.new` | method | Create a new user with the given name and age. |
| `tests/fixtures/sample_rust/lib.rs::User.is_adult` | method | Check if the user is an adult. |
| `tests/fixtures/sample_rust/lib.rs::ToJson` | trait | A trait for objects that can be serialized to JSON. |
| `tests/fixtures/sample_rust/lib.rs::ToJson.to_json` | method_spec |  |
| `tests/fixtures/sample_rust/lib.rs::User.to_json` | method |  |
| `tests/fixtures/sample_rust/lib.rs::Status` | enum | Represents a status code. |
| `tests/fixtures/sample_rust/lib.rs::UserResult` | type | A type alias for a result type. |
## Relationships
- **Called by:** indexer/ast_parser.py::parse_file, indexer/go_parser.py::parse_go_file, indexer/java_parser.py::parse_java_file, indexer/js_parser.py::parse_js_file, indexer/rest_api.py::_webhook_sign, indexer/ruby_parser.py::parse_ruby_file, indexer/rust_parser.py::parse_rust_file
- **Imports from:** hashlib, import java.util.ArrayList;, import java.util.List;, use serde::{Deserialize, Serialize};, use std::collections::HashMap;, utils.crypto.sign_payload
## Entry Points
- `App`
- `TokenValidator`
- `require_auth`
- `wrapper`
- `Router`
- `age_difference`
