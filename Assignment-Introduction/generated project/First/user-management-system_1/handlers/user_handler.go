package handlers

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"net/http"
	"strconv"
	"strings"
	"sync"

	"usermgmt/models"
	"usermgmt/storage"
	"usermgmt/utils"
)

// UserHandler holds dependencies for all user-related HTTP handlers.
type UserHandler struct {
	store    *storage.Store
	sessions map[string]int
	mu       sync.RWMutex
}

func NewUserHandler(store *storage.Store) *UserHandler {
	return &UserHandler{
		store:    store,
		sessions: make(map[string]int),
	}
}

func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
	var req models.CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		utils.WriteError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	if req.Name == "" || req.Email == "" || req.Password == "" {
		utils.WriteError(w, http.StatusBadRequest, "name, email and password are required")
		return
	}

	hash, err := utils.HashPassword(req.Password)
	if err != nil {
		utils.WriteError(w, http.StatusInternalServerError, "could not process password")
		return
	}

	user := models.User{Name: req.Name, Email: req.Email, PasswordHash: hash}
	created, err := h.store.Create(user)
	if err != nil {
		if err == storage.ErrEmailExists {
			utils.WriteError(w, http.StatusConflict, "email already registered")
			return
		}
		utils.WriteError(w, http.StatusInternalServerError, "could not create user")
		return
	}
	utils.WriteJSON(w, http.StatusCreated, created)
}

func (h *UserHandler) ListUsers(w http.ResponseWriter, r *http.Request) {
	utils.WriteJSON(w, http.StatusOK, h.store.GetAll())
}

func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil {
		utils.WriteError(w, http.StatusBadRequest, "invalid user id")
		return
	}
	user, err := h.store.GetByID(id)
	if err != nil {
		utils.WriteError(w, http.StatusNotFound, "user not found")
		return
	}
	utils.WriteJSON(w, http.StatusOK, user)
}

func (h *UserHandler) UpdateUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil {
		utils.WriteError(w, http.StatusBadRequest, "invalid user id")
		return
	}
	var req models.UpdateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		utils.WriteError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	updated, err := h.store.Update(id, req.Name, req.Email)
	if err != nil {
		utils.WriteError(w, http.StatusNotFound, "user not found")
		return
	}
	utils.WriteJSON(w, http.StatusOK, updated)
}

func (h *UserHandler) DeleteUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil {
		utils.WriteError(w, http.StatusBadRequest, "invalid user id")
		return
	}
	if err := h.store.Delete(id); err != nil {
		utils.WriteError(w, http.StatusNotFound, "user not found")
		return
	}
	utils.WriteJSON(w, http.StatusOK, map[string]string{"message": "user deleted"})
}

func (h *UserHandler) Login(w http.ResponseWriter, r *http.Request) {
	var req models.LoginRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		utils.WriteError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	user, err := h.store.GetByEmail(req.Email)
	if err != nil {
		utils.WriteError(w, http.StatusUnauthorized, "invalid email or password")
		return
	}
	if err := utils.VerifyPassword(req.Password, user.PasswordHash); err != nil {
		utils.WriteError(w, http.StatusUnauthorized, "invalid email or password")
		return
	}

	token, err := generateToken()
	if err != nil {
		utils.WriteError(w, http.StatusInternalServerError, "could not create session")
		return
	}
	h.mu.Lock()
	h.sessions[token] = user.ID
	h.mu.Unlock()

	utils.WriteJSON(w, http.StatusOK, models.LoginResponse{Token: token, User: user})
}

// AuthMiddleware protects routes that require a valid session token
// passed via the "Authorization: Bearer <token>" header.
func (h *UserHandler) AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		authHeader := r.Header.Get("Authorization")
		if !strings.HasPrefix(authHeader, "Bearer ") {
			utils.WriteError(w, http.StatusUnauthorized, "missing or invalid authorization header")
			return
		}
		token := strings.TrimPrefix(authHeader, "Bearer ")
		if token == "" {
			utils.WriteError(w, http.StatusUnauthorized, "missing or invalid authorization header")
			return
		}

		h.mu.RLock()
		_, ok := h.sessions[token]
		h.mu.RUnlock()
		if !ok {
			utils.WriteError(w, http.StatusUnauthorized, "invalid or expired token")
			return
		}
		next.ServeHTTP(w, r)
	})
}

func generateToken() (string, error) {
	b := make([]byte, 24)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	return hex.EncodeToString(b), nil
}
