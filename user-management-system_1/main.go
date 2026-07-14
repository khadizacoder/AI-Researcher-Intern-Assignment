package main

import (
	"log"
	"net/http"

	"usermgmt/handlers"
	"usermgmt/storage"
)

func main() {
	store := storage.NewStore()
	h := handlers.NewUserHandler(store)

	mux := http.NewServeMux()

	// Public routes
	mux.HandleFunc("POST /users", h.CreateUser)
	mux.HandleFunc("POST /login", h.Login)

	// Protected routes (require "Authorization: Bearer <token>")
	mux.Handle("GET /users", h.AuthMiddleware(http.HandlerFunc(h.ListUsers)))
	mux.Handle("GET /users/{id}", h.AuthMiddleware(http.HandlerFunc(h.GetUser)))
	mux.Handle("PUT /users/{id}", h.AuthMiddleware(http.HandlerFunc(h.UpdateUser)))
	mux.Handle("DELETE /users/{id}", h.AuthMiddleware(http.HandlerFunc(h.DeleteUser)))

	addr := ":8080"
	log.Printf("User Management System running on %s", addr)
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatal(err)
	}
}
