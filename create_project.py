#!/usr/bin/env python3
"""
create_project.py

Run this script and it will automatically:
  1. Create a project folder called "user-management-system"
  2. Create go.mod, main.go, models.go, handlers.go, and storage.go
  3. Write all the Go source code into the correct files

No manual copy-pasting required.

Usage:
    python3 create_project.py

Then:
    cd user-management-system
    go run .

The server listens on :8080. See the printed instructions / README
for example curl commands.
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
# models.go
# ---------------------------------------------------------------------------
FILES["models.go"] = """package main

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
# storage.go
# ---------------------------------------------------------------------------
FILES["storage.go"] = """package main

import (
\t"errors"
\t"sync"
\t"time"
)

var (
\tErrNotFound    = errors.New("user not found")
\tErrEmailExists = errors.New("email already registered")
)

// Store is a thread-safe in-memory user store.
type Store struct {
\tmu     sync.RWMutex
\tusers  map[int]User
\tnextID int
}

func NewStore() *Store {
\treturn &Store{
\t\tusers:  make(map[int]User),
\t\tnextID: 1,
\t}
}

func (s *Store) Create(u User) (User, error) {
\ts.mu.Lock()
\tdefer s.mu.Unlock()

\tfor _, existing := range s.users {
\t\tif existing.Email == u.Email {
\t\t\treturn User{}, ErrEmailExists
\t\t}
\t}

\tu.ID = s.nextID
\tu.CreatedAt = time.Now()
\tu.UpdatedAt = time.Now()
\ts.users[u.ID] = u
\ts.nextID++
\treturn u, nil
}

func (s *Store) GetByID(id int) (User, error) {
\ts.mu.RLock()
\tdefer s.mu.RUnlock()
\tu, ok := s.users[id]
\tif !ok {
\t\treturn User{}, ErrNotFound
\t}
\treturn u, nil
}

func (s *Store) GetByEmail(email string) (User, error) {
\ts.mu.RLock()
\tdefer s.mu.RUnlock()
\tfor _, u := range s.users {
\t\tif u.Email == email {
\t\t\treturn u, nil
\t\t}
\t}
\treturn User{}, ErrNotFound
}

func (s *Store) GetAll() []User {
\ts.mu.RLock()
\tdefer s.mu.RUnlock()
\tall := make([]User, 0, len(s.users))
\tfor _, u := range s.users {
\t\tall = append(all, u)
\t}
\treturn all
}

func (s *Store) Update(id int, name, email string) (User, error) {
\ts.mu.Lock()
\tdefer s.mu.Unlock()
\tu, ok := s.users[id]
\tif !ok {
\t\treturn User{}, ErrNotFound
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
# handlers.go
# ---------------------------------------------------------------------------
FILES["handlers.go"] = """package main

import (
\t"crypto/rand"
\t"crypto/sha256"
\t"encoding/hex"
\t"encoding/json"
\t"errors"
\t"net/http"
\t"strconv"
\t"strings"
\t"sync"
)

// UserHandler holds dependencies for all user-related HTTP handlers.
type UserHandler struct {
\tstore    *Store
\tsessions map[string]int
\tmu       sync.RWMutex
}

func NewUserHandler(store *Store) *UserHandler {
\treturn &UserHandler{
\t\tstore:    store,
\t\tsessions: make(map[string]int),
\t}
}

// ---- JSON helpers ----

func writeJSON(w http.ResponseWriter, status int, data interface{}) {
\tw.Header().Set("Content-Type", "application/json")
\tw.WriteHeader(status)
\tjson.NewEncoder(w).Encode(data)
}

func writeError(w http.ResponseWriter, status int, message string) {
\twriteJSON(w, status, map[string]string{"error": message})
}

// ---- Password hashing (stdlib-only, salted SHA-256) ----

// hashPassword returns "<salt_hex>:<hash_hex>"
func hashPassword(password string) (string, error) {
\tsalt := make([]byte, 16)
\tif _, err := rand.Read(salt); err != nil {
\t\treturn "", err
\t}
\thash := sha256.Sum256(append(salt, []byte(password)...))
\treturn hex.EncodeToString(salt) + ":" + hex.EncodeToString(hash[:]), nil
}

func verifyPassword(password, encoded string) error {
\tidx := strings.IndexByte(encoded, ':')
\tif idx == -1 {
\t\treturn errors.New("invalid hash format")
\t}
\tsaltHex, hashHex := encoded[:idx], encoded[idx+1:]
\tsalt, err := hex.DecodeString(saltHex)
\tif err != nil {
\t\treturn err
\t}
\texpected, err := hex.DecodeString(hashHex)
\tif err != nil {
\t\treturn err
\t}
\tactual := sha256.Sum256(append(salt, []byte(password)...))
\tif hex.EncodeToString(actual[:]) != hex.EncodeToString(expected) {
\t\treturn errors.New("invalid password")
\t}
\treturn nil
}

func generateToken() (string, error) {
\tb := make([]byte, 24)
\tif _, err := rand.Read(b); err != nil {
\t\treturn "", err
\t}
\treturn hex.EncodeToString(b), nil
}

// ---- Handlers ----

func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
\tvar req CreateUserRequest
\tif err := json.NewDecoder(r.Body).Decode(&req); err != nil {
\t\twriteError(w, http.StatusBadRequest, "invalid request body")
\t\treturn
\t}
\tif req.Name == "" || req.Email == "" || req.Password == "" {
\t\twriteError(w, http.StatusBadRequest, "name, email and password are required")
\t\treturn
\t}

\thash, err := hashPassword(req.Password)
\tif err != nil {
\t\twriteError(w, http.StatusInternalServerError, "could not process password")
\t\treturn
\t}

\tuser := User{Name: req.Name, Email: req.Email, PasswordHash: hash}
\tcreated, err := h.store.Create(user)
\tif err != nil {
\t\tif err == ErrEmailExists {
\t\t\twriteError(w, http.StatusConflict, "email already registered")
\t\t\treturn
\t\t}
\t\twriteError(w, http.StatusInternalServerError, "could not create user")
\t\treturn
\t}
\twriteJSON(w, http.StatusCreated, created)
}

func (h *UserHandler) ListUsers(w http.ResponseWriter, r *http.Request) {
\twriteJSON(w, http.StatusOK, h.store.GetAll())
}

func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
\tid, err := strconv.Atoi(r.PathValue("id"))
\tif err != nil {
\t\twriteError(w, http.StatusBadRequest, "invalid user id")
\t\treturn
\t}
\tuser, err := h.store.GetByID(id)
\tif err != nil {
\t\twriteError(w, http.StatusNotFound, "user not found")
\t\treturn
\t}
\twriteJSON(w, http.StatusOK, user)
}

func (h *UserHandler) UpdateUser(w http.ResponseWriter, r *http.Request) {
\tid, err := strconv.Atoi(r.PathValue("id"))
\tif err != nil {
\t\twriteError(w, http.StatusBadRequest, "invalid user id")
\t\treturn
\t}
\tvar req UpdateUserRequest
\tif err := json.NewDecoder(r.Body).Decode(&req); err != nil {
\t\twriteError(w, http.StatusBadRequest, "invalid request body")
\t\treturn
\t}
\tupdated, err := h.store.Update(id, req.Name, req.Email)
\tif err != nil {
\t\twriteError(w, http.StatusNotFound, "user not found")
\t\treturn
\t}
\twriteJSON(w, http.StatusOK, updated)
}

func (h *UserHandler) DeleteUser(w http.ResponseWriter, r *http.Request) {
\tid, err := strconv.Atoi(r.PathValue("id"))
\tif err != nil {
\t\twriteError(w, http.StatusBadRequest, "invalid user id")
\t\treturn
\t}
\tif err := h.store.Delete(id); err != nil {
\t\twriteError(w, http.StatusNotFound, "user not found")
\t\treturn
\t}
\twriteJSON(w, http.StatusOK, map[string]string{"message": "user deleted"})
}

func (h *UserHandler) Login(w http.ResponseWriter, r *http.Request) {
\tvar req LoginRequest
\tif err := json.NewDecoder(r.Body).Decode(&req); err != nil {
\t\twriteError(w, http.StatusBadRequest, "invalid request body")
\t\treturn
\t}
\tuser, err := h.store.GetByEmail(req.Email)
\tif err != nil {
\t\twriteError(w, http.StatusUnauthorized, "invalid email or password")
\t\treturn
\t}
\tif err := verifyPassword(req.Password, user.PasswordHash); err != nil {
\t\twriteError(w, http.StatusUnauthorized, "invalid email or password")
\t\treturn
\t}

\ttoken, err := generateToken()
\tif err != nil {
\t\twriteError(w, http.StatusInternalServerError, "could not create session")
\t\treturn
\t}
\th.mu.Lock()
\th.sessions[token] = user.ID
\th.mu.Unlock()

\twriteJSON(w, http.StatusOK, LoginResponse{Token: token, User: user})
}

// AuthMiddleware protects routes that require a valid session token
// passed via the "Authorization: Bearer <token>" header.
func (h *UserHandler) AuthMiddleware(next http.Handler) http.Handler {
\treturn http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
\t\tauthHeader := r.Header.Get("Authorization")
\t\tif !strings.HasPrefix(authHeader, "Bearer ") {
\t\t\twriteError(w, http.StatusUnauthorized, "missing or invalid authorization header")
\t\t\treturn
\t\t}
\t\ttoken := strings.TrimPrefix(authHeader, "Bearer ")
\t\tif token == "" {
\t\t\twriteError(w, http.StatusUnauthorized, "missing or invalid authorization header")
\t\t\treturn
\t\t}

\t\th.mu.RLock()
\t\t_, ok := h.sessions[token]
\t\th.mu.RUnlock()
\t\tif !ok {
\t\t\twriteError(w, http.StatusUnauthorized, "invalid or expired token")
\t\t\treturn
\t\t}
\t\tnext.ServeHTTP(w, r)
\t})
}
"""

# ---------------------------------------------------------------------------
# main.go
# ---------------------------------------------------------------------------
FILES["main.go"] = """package main

import (
\t"log"
\t"net/http"
)

func main() {
\tstore := NewStore()
\th := NewUserHandler(store)

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
# README.md (extra, not required but helpful — safe to ignore/delete)
# ---------------------------------------------------------------------------
FILES["README.md"] = """# User Management System (Go)

A minimal, dependency-free REST API for managing users, written using only
the Go standard library (no external packages, no database required).
All code lives in a single `package main` across main.go, models.go,
handlers.go, and storage.go.

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

Get / update / delete a single user:
```
curl localhost:8080/users/1 -H "Authorization: Bearer <TOKEN>"

curl -X PUT localhost:8080/users/1 \\
  -H "Authorization: Bearer <TOKEN>" \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Alice Smith"}'

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

    for filename, content in FILES.items():
        full_path = os.path.join(root, filename)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"created: {os.path.join(PROJECT_DIR, filename)}")

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
