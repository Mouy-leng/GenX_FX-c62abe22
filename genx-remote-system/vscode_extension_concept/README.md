# GenX Agent Status Visualizer - VS Code Extension Concept

This document outlines the concept for a Visual Studio Code extension designed to visualize the status of your remote agents and authenticated sessions.

## 1. High-Level Architecture

The extension will act as a secure client to your existing Firebase/Firestore backend. It will provide a read-only view of the active sessions, offering a convenient way to monitor your system directly from your code editor.

The architecture would consist of three main parts:
1.  **VS Code Extension (Frontend)**: The user interface within VS Code, built using standard web technologies (HTML, CSS, JavaScript/TypeScript).
2.  **Firebase Authentication**: The extension will use Firebase's client-side SDK to securely authenticate the user. This ensures that only authorized individuals can view the status data.
3.  **Firestore Database (Backend)**: The extension will make real-time queries to your `sessions` collection in Firestore to fetch and display the data.

## 2. Core Features

-   **Secure Authentication**:
    -   On startup, the extension would prompt the user to log in using their GitHub account via Firebase Authentication.
    -   The authentication token would be securely stored in the VS Code `SecretStorage`.

-   **Real-Time Status View**:
    -   A new view in the VS Code activity bar would list all `active` sessions from the Firestore `sessions` collection.
    -   The view would update in real-time as session data changes in the database.

-   **Session Details**:
    -   Clicking on a session would open a detailed view showing:
        -   GitHub Username (`githubUsername`)
        -   Device Build Number (`deviceBuildNumber`)
        -   Session Creation Time (`createdAt`)
        -   Session Expiry Time (`expiresAt`)

-   **Simple Commands**:
    -   A command like `genx-agent-visualizer.showStatus` (as defined in `package.json`) would open the main status view.
    -   A `Refresh` button would allow for manually re-fetching the data.

## 3. Implementation Steps (Conceptual)

1.  **Initialize Project**:
    -   Use `yo code` to scaffold a new TypeScript-based VS Code extension.
    -   Install the `firebase` client SDK (`npm install firebase`).

2.  **Authentication Service**:
    -   Create a service class (`FirebaseService.ts`) to handle the Firebase initialization and authentication logic.
    -   Implement `signIn()` and `signOut()` methods that use `firebase/auth`.

3.  **Data Provider**:
    -   Implement a `TreeDataProvider` for the custom view in the activity bar.
    -   This provider will query the `sessions` collection in Firestore and return the data as tree items.
    -   It will use `onSnapshot` for real-time updates.

4.  **UI/View**:
    -   Define the custom view and the associated commands in `package.json`.
    -   The `extension.ts` file will register the `TreeDataProvider` and the commands.

## 4. Security Considerations

-   **Read-Only Access**: The Firebase security rules should be configured to ensure the extension can only read data and cannot modify or delete any session information.
-   **Secret Storage**: API keys and user tokens must be stored using VS Code's `SecretStorage` API, not in plain text configuration files.

This conceptual outline provides a clear path for developing a powerful and secure monitoring tool for your remote access system, directly integrated into your development workflow.