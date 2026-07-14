package storage

import (
	"errors"
	"sync"
	"time"

	"usermgmt/models"
)

var (
	ErrNotFound    = errors.New("user not found")
	ErrEmailExists = errors.New("email already registered")
)

// Store is a thread-safe in-memory user store.
type Store struct {
	mu     sync.RWMutex
	users  map[int]models.User
	nextID int
}

func NewStore() *Store {
	return &Store{
		users:  make(map[int]models.User),
		nextID: 1,
	}
}

func (s *Store) Create(u models.User) (models.User, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	for _, existing := range s.users {
		if existing.Email == u.Email {
			return models.User{}, ErrEmailExists
		}
	}

	u.ID = s.nextID
	u.CreatedAt = time.Now()
	u.UpdatedAt = time.Now()
	s.users[u.ID] = u
	s.nextID++
	return u, nil
}

func (s *Store) GetByID(id int) (models.User, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	u, ok := s.users[id]
	if !ok {
		return models.User{}, ErrNotFound
	}
	return u, nil
}

func (s *Store) GetByEmail(email string) (models.User, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	for _, u := range s.users {
		if u.Email == email {
			return u, nil
		}
	}
	return models.User{}, ErrNotFound
}

func (s *Store) GetAll() []models.User {
	s.mu.RLock()
	defer s.mu.RUnlock()
	all := make([]models.User, 0, len(s.users))
	for _, u := range s.users {
		all = append(all, u)
	}
	return all
}

func (s *Store) Update(id int, name, email string) (models.User, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	u, ok := s.users[id]
	if !ok {
		return models.User{}, ErrNotFound
	}
	if name != "" {
		u.Name = name
	}
	if email != "" {
		u.Email = email
	}
	u.UpdatedAt = time.Now()
	s.users[id] = u
	return u, nil
}

func (s *Store) Delete(id int) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.users[id]; !ok {
		return ErrNotFound
	}
	delete(s.users, id)
	return nil
}
