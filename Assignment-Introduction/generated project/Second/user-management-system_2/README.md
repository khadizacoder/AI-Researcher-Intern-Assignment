# User Management System (Go)

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
curl -X POST localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com","password":"secret123"}'
```

Log in:
```
curl -X POST localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123"}'
```

List users (use the token from login):
```
curl localhost:8080/users -H "Authorization: Bearer <TOKEN>"
```

Get / update / delete a single user:
```
curl localhost:8080/users/1 -H "Authorization: Bearer <TOKEN>"

curl -X PUT localhost:8080/users/1 \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice Smith"}'

curl -X DELETE localhost:8080/users/1 -H "Authorization: Bearer <TOKEN>"
```

## Notes

- Data is stored in memory and resets when the server restarts.
- Passwords are hashed with a salted SHA-256 (stdlib only). For production
  use, swap in `golang.org/x/crypto/bcrypt` for stronger hashing.
- Requires Go 1.22+ (uses the method/path pattern matching added to
  `net/http.ServeMux`).
