package com.example.app;

import java.util.List;
import java.util.ArrayList;

/**
 * Main application class that manages users.
 */
class App {
    private List<String> users;

    /**
     * Constructs a new App instance.
     */
    App() {
        users = new ArrayList<>();
    }

    /**
     * Adds a user to the application.
     */
    void addUser(String name) {
        users.add(name);
    }

    /**
     * Returns the number of registered users.
     */
    int getUserCount() {
        return users.size();
    }
}

/**
 * Represents a user profile.
 */
interface UserProfile {
    /**
     * Gets the display name.
     */
    String getDisplayName();

    /**
     * Gets the user role.
     */
    String getRole();
}

/**
 * Defines user roles.
 */
enum Role {
    ADMIN,
    MEMBER,
    GUEST
}
