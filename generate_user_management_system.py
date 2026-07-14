#!/usr/bin/env python3
"""
generate_user_management_system.py

Run this script and it will automatically:
  1. Create a project folder called "user-management-system"
  2. Create every required Go source file inside it
  3. Write all the source code into the correct files

No manual copy-pasting of Go code is required.

Usage:
    python3 generate_user_management_system.py

Then:
    cd user-management-system
    go run .

The server listens on :8080. See the generated README.md for
example curl commands.
"""

import os

PROJECT_DIR = "user-management-system"

FILES = {}

# ---------------------------------------------------------------------------
# go.mod
# ---------------------------------------------------------------------------
FILES["go.mod"] = """module usermgmt

go 1.22
"""

# ---------------------------------------------------------------------------
# main.go
# ---------------------------------------------------------------------------
FILES["main.go"] = """package main

import (
\t"log"
\t"net/http"

\t"usermgmt/handlers"
\t"usermgmt/storage"
)

func main() {
\tstore := storage.NewStore()
\th := handlers.NewUserHandler(store)

\tmux := http.NewServeMux()

\t// Public routes
\tmux.HandleFunc("POST /users", h.CreateUser)
\tmux.HandleFunc("POST /login", h.Login)

\t// Protected routes (require "Authorization: Bearer <token>")
\tmux.Handle("GET /users", h.AuthMiddleware(http.HandlerFunc(h.ListUsers)))
\tmux.Handle("GET /users/{id}", h.AuthMiddleware(http.HandlerFunc(h.GetUser)))
\tmux.Handle("PUT /users/{id}", h.AuthMiddleware(http.HandlerFunc(h.UpdateUser)))
\tmux.Handle("DELETE /users/{id}", h.AuthMiddleware(http.HandlerFunc(h.DeleteUser)))

\taddr := ":8080"
\tlog.Printf("User Management System running on %s", addr)
\tif err := http.ListenAndServe(addr, mux); err != nil {
\t\tlog.Fatal(err)
\t}
}
"""

# ---------------------------------------------------------------------------
# models/user.go
# ---------------------------------------------------------------------------
FILES[os.path.join("models", "user.go")] = """package models

import "time"

// User represents a registered user in the system.
type User struct {
\tID           int       `json:"id"`
\tName         string    `json:"name"`
\tEmail        string    `json:"email"`
\tPasswordHash string    `json:"-"`
\tCreatedAt    time.Time `json:"created_at"`
\tUpdatedAt    time.Time `json:"updated_at"`
}

type CreateUserRequest struct {
\tName     string `json:"name"`
\tEmail    string `json:"email"`
\tPassword string `json:"password"`
}

type UpdateUserRequest struct {
\tName  string `json:"name"`
\tEmail string `json:"email"`
}

type LoginRequest struct {
\tEmail    string `json:"email"`
\tPassword string `json:"password"`
}

type LoginResponse struct {
\tToken string `json:"token"`
\tUser  User   `json:"user"`
}
"""

# ---------------------------------------------------------------------------
# storage/store.go
# ---------------------------------------------------------------------------
FILES[os.path.join("storage", "store.go")] = """package storage

import (
\t"errors"
\t"sync"
\t"time"

\t"usermgmt/models"
)

var (
\tErrNotFound    = errors.New("user not found")
\tErrEmailExists = errors.New("email already registered")
)

// Store is a thread-safe in-memory user store.
type Store struct {
\tmu     sync.RWMutex
\tusers  map[int]models.User
\tnextID int
}

func NewStore() *Store {
\treturn &Store{
\t\tusers:  make(map[int]models.User),
\t\tnextID: 1,
\t}
}

func (s *Store) Create(u models.User) (models.User, error) {
\ts.mu.Lock()
\tdefer s.mu.Unlock()

\tfor _, existing := range s.users {
\t\tif existing.Email == u.Email {
\t\t\treturn models.User{}, ErrEmailExists
\t\t}
\t}

\tu.ID = s.nextID
\tu.CreatedAt = time.Now()
\tu.UpdatedAt = time.Now()
\ts.users[u.ID] = u
\ts.nextID++
\treturn u, nil
}

func (s *Store) GetByID(id int) (models.User, error) {
\ts.mu.RLock()
\tdefer s.mu.RUnlock()
\tu, ok := s.users[id]
\tif !ok {
\t\treturn models.User{}, ErrNotFound
\t}
\treturn u, nil
}

func (s *Store) GetByEmail(email string) (models.User, error) {
\ts.mu.RLock()
\tdefer s.mu.RUnlock()
\tfor _, u := range s.users {
\t\tif u.Email == email {
\t\t\treturn u, nil
\t\t}
\t}
\treturn models.User{}, ErrNotFound
}

func (s *Store) GetAll() []models.User {
\ts.mu.RLock()
\tdefer s.mu.RUnlock()
\tall := make([]models.User, 0, len(s.users))
\tfor _, u := range s.users {
\t\tall = append(all, u)
\t}
\treturn all
}

func (s *Store) Update(id int, name, email string) (models.User, error) {
\ts.mu.Lock()
\tdefer s.mu.Unlock()
\tu, ok := s.users[id]
\tif !ok {
\t\treturn models.User{}, ErrNotFound
\t}
\tif name != "" {
\t\tu.Name = name
\t}
\tif email != "" {
\t\tu.Email = email
\t}
\tu.UpdatedAt = time.Now()
\ts.users[id] = u
\treturn u, nil
}

func (s *Store) Delete(id int) error {
\ts.mu.Lock()
\tdefer s.mu.Unlock()
\tif _, ok := s.users[id]; !ok {
\t\treturn ErrNotFound
\t}
\tdelete(s.users, id)
\treturn nil
}
"""

# ---------------------------------------------------------------------------
# utils/response.go
# ---------------------------------------------------------------------------
FILES[os.path.join("utils", "response.go")] = """package utils

import (
\t"encoding/json"
\t"net/http"
)

func WriteJSON(w http.ResponseWriter, status int, data interface{}) {
\tw.Header().Set("Content-Type", "application/json")
\tw.WriteHeader(status)
\tjson.NewEncoder(w).Encode(data)
}

func WriteError(w http.ResponseWriter, status int, message string) {
\tWriteJSON(w, status, map[string]string{"error": message})
}
"""

# ---------------------------------------------------------------------------
# utils/password.go
# ---------------------------------------------------------------------------
FILES[os.path.join("utils", "password.go")] = """package utils

import (
\t"crypto/rand"
\t"crypto/sha256"
\t"encoding/hex"
\t"errors"
)

// HashPassword generates a salted SHA-256 hash of the password.
// Stored format: "<salt_hex>:<hash_hex>"
func HashPassword(password string) (string, error) {
\tsalt := make([]byte, 16)
\tif _, err := rand.Read(salt); err != nil {
\t\treturn "", err
\t}
\thash := sha256.Sum256(append(salt, []byte(password)...))
\treturn hex.EncodeToString(salt) + ":" + hex.EncodeToString(hash[:]), nil
}

// VerifyPassword checks a plaintext password against a stored hash.
func VerifyPassword(password, encoded string) error {
\tparts := splitOnce(encoded, ':')
\tif len(parts) != 2 {
\t\treturn errors.New("invalid hash format")
\t}
\tsalt, err := hex.DecodeString(parts[0])
\tif err != nil {
\t\treturn err
\t}
\texpected, err := hex.DecodeString(parts[1])
\tif err != nil {
\t\treturn err
\t}
\tactual := sha256.Sum256(append(salt, []byte(password)...))
\tif hex.EncodeToString(actual[:]) != hex.EncodeToString(expected) {
\t\treturn errors.New("invalid password")
\t}
\treturn nil
}

func splitOnce(s string, sep byte) []string {
\tfor i := 0; i < len(s); i++ {
\t\tif s[i] == sep {
\t\t\treturn []string{s[:i], s[i+1:]}
\t\t}
\t}
\treturn []string{s}
}
"""

# ---------------------------------------------------------------------------
# handlers/user_handler.go
# ---------------------------------------------------------------------------
FILES[os.path.join("handlers", "user_handler.go")] = """package handlers

import (
\t"crypto/rand"
\t"encoding/hex"
\t"encoding/json"
\t"net/http"
\t"strconv"
\t"strings"
\t"sync"

\t"usermgmt/models"
\t"usermgmt/storage"
\t"usermgmt/utils"
)

// UserHandler holds dependencies for all user-related HTTP handlers.
type UserHandler struct {
\tstore    *storage.Store
\tsessions map[string]int
\tmu       sync.RWMutex
}

func NewUserHandler(store *storage.Store) *UserHandler {
\treturn &UserHandler{
\t\tstore:    store,
\t\tsessions: make(map[string]int),
\t}
}

func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
\tvar req models.CreateUserRequest
\tif err := json.NewDecoder(r.Body).Decode(&req); err != nil {
\t\tutils.WriteError(w, http.StatusBadRequest, "invalid request body")
\t\treturn
\t}
\tif req.Name == "" || req.Email == "" || req.Password == "" {
\t\tutils.WriteError(w, http.StatusBadRequest, "name, email and password are required")
\t\treturn
\t}

\thash, err := utils.HashPassword(req.Password)
\tif err != nil {
\t\tutils.WriteError(w, http.StatusInternalServerError, "could not process password")
\t\treturn
\t}

\tuser := models.User{Name: req.Name, Email: req.Email, PasswordHash: hash}
\tcreated, err := h.store.Create(user)
\tif err != nil {
\t\tif err == storage.ErrEmailExists {
\t\t\tutils.WriteError(w, http.StatusConflict, "email already registered")
\t\t\treturn
\t\t}
\t\tutils.WriteError(w, http.StatusInternalServerError, "could not create user")
\t\treturn
\t}
\tutils.WriteJSON(w, http.StatusCreated, created)
}

func (h *UserHandler) ListUsers(w http.ResponseWriter, r *http.Request) {
\tutils.WriteJSON(w, http.StatusOK, h.store.GetAll())
}

func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
\tid, err := strconv.Atoi(r.PathValue("id"))
\tif err != nil {
\t\tutils.WriteError(w, http.StatusBadRequest, "invalid user id")
\t\treturn
\t}
\tuser, err := h.store.GetByID(id)
\tif err != nil {
\t\tutils.WriteError(w, http.StatusNotFound, "user not found")
\t\treturn
\t}
\tutils.WriteJSON(w, http.StatusOK, user)
}

func (h *UserHandler) UpdateUser(w http.ResponseWriter, r *http.Request) {
\tid, err := strconv.Atoi(r.PathValue("id"))
\tif err != nil {
\t\tutils.WriteError(w, http.StatusBadRequest, "invalid user id")
\t\treturn
\t}
\tvar req models.UpdateUserRequest
\tif err := json.NewDecoder(r.Body).Decode(&req); err != nil {
\t\tutils.WriteError(w, http.StatusBadRequest, "invalid request body")
\t\treturn
\t}
\tupdated, err := h.store.Update(id, req.Name, req.Email)
\tif err != nil {
\t\tutils.WriteError(w, http.StatusNotFound, "user not found")
\t\treturn
\t}
\tutils.WriteJSON(w, http.StatusOK, updated)
}

func (h *UserHandler) DeleteUser(w http.ResponseWriter, r *http.Request) {
\tid, err := strconv.Atoi(r.PathValue("id"))
\tif err != nil {
\t\tutils.WriteError(w, http.StatusBadRequest, "invalid user id")
\t\treturn
\t}
\tif err := h.store.Delete(id); err != nil {
\t\tutils.WriteError(w, http.StatusNotFound, "user not found")
\t\treturn
\t}
\tutils.WriteJSON(w, http.StatusOK, map[string]string{"message": "user deleted"})
}

func (h *UserHandler) Login(w http.ResponseWriter, r *http.Request) {
\tvar req models.LoginRequest
\tif err := json.NewDecoder(r.Body).Decode(&req); err != nil {
\t\tutils.WriteError(w, http.StatusBadRequest, "invalid request body")
\t\treturn
\t}
\tuser, err := h.store.GetByEmail(req.Email)
\tif err != nil {
\t\tutils.WriteError(w, http.StatusUnauthorized, "invalid email or password")
\t\treturn
\t}
\tif err := utils.VerifyPassword(req.Password, user.PasswordHash); err != nil {
\t\tutils.WriteError(w, http.StatusUnauthorized, "invalid email or password")
\t\treturn
\t}

\ttoken, err := generateToken()
\tif err != nil {
\t\tutils.WriteError(w, http.StatusInternalServerError, "could not create session")
\t\treturn
\t}
\th.mu.Lock()
\th.sessions[token] = user.ID
\th.mu.Unlock()

\tutils.WriteJSON(w, http.StatusOK, models.LoginResponse{Token: token, User: user})
}

// AuthMiddleware protects routes that require a valid session token
// passed via the "Authorization: Bearer <token>" header.
func (h *UserHandler) AuthMiddleware(next http.Handler) http.Handler {
\treturn http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
\t\tauthHeader := r.Header.Get("Authorization")
\t\tif !strings.HasPrefix(authHeader, "Bearer ") {
\t\t\tutils.WriteError(w, http.StatusUnauthorized, "missing or invalid authorization header")
\t\t\treturn
\t\t}
\t\ttoken := strings.TrimPrefix(authHeader, "Bearer ")
\t\tif token == "" {
\t\t\tutils.WriteError(w, http.StatusUnauthorized, "missing or invalid authorization header")
\t\t\treturn
\t\t}

\t\th.mu.RLock()
\t\t_, ok := h.sessions[token]
\t\th.mu.RUnlock()
\t\tif !ok {
\t\t\tutils.WriteError(w, http.StatusUnauthorized, "invalid or expired token")
\t\t\treturn
\t\t}
\t\tnext.ServeHTTP(w, r)
\t})
}

func generateToken() (string, error) {
\tb := make([]byte, 24)
\tif _, err := rand.Read(b); err != nil {
\t\treturn "", err
\t}
\treturn hex.EncodeToString(b), nil
}
"""

# ---------------------------------------------------------------------------
# README.md
# ---------------------------------------------------------------------------
FILES["README.md"] = """# User Management System (Go)

A minimal, dependency-free REST API for managing users, written using only
the Go standard library (no external packages, no database required).

## Run it

```
go run .
```

The server starts on `http://localhost:8080`.

## Endpoints

| Method | Path         | Auth required | Description            |
|--------|--------------|----------------|-------------------------|
| POST   | /users       | no             | Register a new user     |
| POST   | /login       | no             | Log in, get a token     |
| GET    | /users       | yes            | List all users          |
| GET    | /users/{id}  | yes            | Get a single user       |
| PUT    | /users/{id}  | yes            | Update a user           |
| DELETE | /users/{id}  | yes            | Delete a user           |

Protected routes require an `Authorization: Bearer <token>` header, using the
token returned by `/login`.

## Example usage

Register:
```
curl -X POST localhost:8080/users \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Alice","email":"alice@example.com","password":"secret123"}'
```

Log in:
```
curl -X POST localhost:8080/login \\
  -H "Content-Type: application/json" \\
  -d '{"email":"alice@example.com","password":"secret123"}'
```

List users (use the token from login):
```
curl localhost:8080/users -H "Authorization: Bearer <TOKEN>"
```

Get a single user:
```
curl localhost:8080/users/1 -H "Authorization: Bearer <TOKEN>"
```

Update a user:
```
curl -X PUT localhost:8080/users/1 \\
  -H "Authorization: Bearer <TOKEN>" \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Alice Smith"}'
```

Delete a user:
```
curl -X DELETE localhost:8080/users/1 -H "Authorization: Bearer <TOKEN>"
```

## Notes

- Data is stored in memory and resets when the server restarts.
- Passwords are hashed with a salted SHA-256 (stdlib only). For production
  use, swap in `golang.org/x/crypto/bcrypt` for stronger hashing.
- Requires Go 1.22+ (uses the method/path pattern matching added to
  `net/http.ServeMux`).
"""


def main():
    root = os.path.abspath(PROJECT_DIR)
    os.makedirs(root, exist_ok=True)

    for rel_path, content in FILES.items():
        full_path = os.path.join(root, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"created: {os.path.join(PROJECT_DIR, rel_path)}")

    print()
    print(f"Project '{PROJECT_DIR}' generated successfully.")
    print()
    print("Next steps:")
    print(f"  cd {PROJECT_DIR}")
    print("  go run .")
    print()
    print("The API will be available at http://localhost:8080")
    print("See README.md inside the project for example curl commands.")


if __name__ == "__main__":
    main()
