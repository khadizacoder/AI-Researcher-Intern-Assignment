package main

import (
	"errors"
	"sync"
	"time"
)

var (
	ErrNotFound    = errors.New("user not found")
	ErrEmailExists = errors.New("email already registered")
)

// Store is a thread-safe in-memory user store.
type Store struct {
	mu     sync.RWMutex
	users  map[int]User
	nextID int
}

func NewStore() *Store {
	return &Store{
		users:  make(map[int]User),
		nextID: 1,
	}
}

func (s *Store) Create(u User) (User, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	for _, existing := range s.users {
		if existing.Email == u.Email {
			return User{}, ErrEmailExists
		}
	}

	u.ID = s.nextID
	u.CreatedAt = time.Now()
	u.UpdatedAt = time.Now()
	s.users[u.ID] = u
	s.nextID++
	return u, nil
}

func (s *Store) GetByID(id int) (User, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	u, ok := s.users[id]
	if !ok {
		return User{}, ErrNotFound
	}
	return u, nil
}

func (s *Store) GetByEmail(email string) (User, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	for _, u := range s.users {
		if u.Email == email {
			return u, nil
		}
	}
	return User{}, ErrNotFound
}

func (s *Store) GetAll() []User {
	s.mu.RLock()
	defer s.mu.RUnlock()
	all := make([]User, 0, len(s.users))
	for _, u := range s.users {
		all = append(all, u)
	}
	return all
}

func (s *Store) Update(id int, name, email string) (User, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	u, ok := s.users[id]
	if !ok {
		return User{}, ErrNotFound
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
