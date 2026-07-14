package utils

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"errors"
)

// HashPassword generates a salted SHA-256 hash of the password.
// Stored format: "<salt_hex>:<hash_hex>"
func HashPassword(password string) (string, error) {
	salt := make([]byte, 16)
	if _, err := rand.Read(salt); err != nil {
		return "", err
	}
	hash := sha256.Sum256(append(salt, []byte(password)...))
	return hex.EncodeToString(salt) + ":" + hex.EncodeToString(hash[:]), nil
}

// VerifyPassword checks a plaintext password against a stored hash.
func VerifyPassword(password, encoded string) error {
	parts := splitOnce(encoded, ':')
	if len(parts) != 2 {
		return errors.New("invalid hash format")
	}
	salt, err := hex.DecodeString(parts[0])
	if err != nil {
		return err
	}
	expected, err := hex.DecodeString(parts[1])
	if err != nil {
		return err
	}
	actual := sha256.Sum256(append(salt, []byte(password)...))
	if hex.EncodeToString(actual[:]) != hex.EncodeToString(expected) {
		return errors.New("invalid password")
	}
	return nil
}

func splitOnce(s string, sep byte) []string {
	for i := 0; i < len(s); i++ {
		if s[i] == sep {
			return []string{s[:i], s[i+1:]}
		}
	}
	return []string{s}
}
