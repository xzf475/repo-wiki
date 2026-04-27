use std::collections::HashMap;
use serde::{Deserialize, Serialize};

/// Represents a user in the system.
struct User {
    name: String,
    age: u32,
}

/// Calculates the age difference between two users.
fn age_difference(a: &User, b: &User) -> u32 {
    if a.age > b.age {
        a.age - b.age
    } else {
        b.age - a.age
    }
}

impl User {
    /// Create a new user with the given name and age.
    fn new(name: String, age: u32) -> Self {
        User { name, age }
    }

    /// Check if the user is an adult.
    fn is_adult(&self) -> bool {
        self.age >= 18
    }
}

/// A trait for objects that can be serialized to JSON.
trait ToJson {
    /// Convert this object to a JSON string.
    fn to_json(&self) -> String;
}

impl ToJson for User {
    fn to_json(&self) -> String {
        format!("{{\"name\": \"{}\", \"age\": {}}}", self.name, self.age)
    }
}

/// Represents a status code.
enum Status {
    Active,
    Inactive,
    Archived,
}

/// A type alias for a result type.
type UserResult = Result<User, String>;
