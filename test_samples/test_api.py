import unittest
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from unittest.mock import Mock, patch


@dataclass
class User:
    """User model."""

    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool = True


class UserAPI:
    """Simulated REST API for user management."""

    def __init__(self):
        """Initialize API with empty user database."""
        self.users: Dict[int, User] = {}
        self.next_id = 1

    def create_user(self, username: str, email: str) -> User:
        """Create a new user."""
        if not username or not email:
            raise ValueError("Username and email are required")

        if "@" not in email:
            raise ValueError("Invalid email format")

        user = User(
            id=self.next_id, username=username, email=email, created_at=datetime.now()
        )
        self.users[user.id] = user
        self.next_id += 1
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)

    def list_users(self, active_only: bool = False) -> List[User]:
        """List all users, optionally filtering by active status."""
        if active_only:
            return [u for u in self.users.values() if u.is_active]
        return list(self.users.values())

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields."""
        user = self.users.get(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False


class TestUserAPI(unittest.TestCase):
    """Test cases for UserAPI."""

    def setUp(self):
        """Set up test cases."""
        self.api = UserAPI()
        # Create a test user
        self.test_user = self.api.create_user(
            username="testuser", email="test@example.com"
        )

    def test_create_user(self):
        """Test user creation."""
        user = self.api.create_user(username="newuser", email="new@example.com")
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(user.is_active)

    def test_create_user_validation(self):
        """Test user creation validation."""
        with self.assertRaises(ValueError):
            self.api.create_user("", "invalid")

        with self.assertRaises(ValueError):
            self.api.create_user("user", "invalid-email")

    def test_get_user(self):
        """Test getting user by ID."""
        user = self.api.get_user(self.test_user.id)
        self.assertEqual(user.username, "testuser")

        # Test non-existent user
        self.assertIsNone(self.api.get_user(999))

    def test_list_users(self):
        """Test listing users."""
        # Create additional users
        self.api.create_user("user2", "user2@example.com")
        self.api.create_user("user3", "user3@example.com")

        users = self.api.list_users()
        self.assertEqual(len(users), 3)

    def test_list_active_users(self):
        """Test listing active users."""
        # Create an inactive user
        user = self.api.create_user("inactive", "inactive@example.com")
        self.api.update_user(user.id, is_active=False)

        active_users = self.api.list_users(active_only=True)
        self.assertEqual(len(active_users), 1)
        self.assertTrue(all(u.is_active for u in active_users))

    def test_update_user(self):
        """Test updating user."""
        updated = self.api.update_user(
            self.test_user.id, username="updated", email="updated@example.com"
        )
        self.assertEqual(updated.username, "updated")
        self.assertEqual(updated.email, "updated@example.com")

        # Test updating non-existent user
        self.assertIsNone(self.api.update_user(999, username="nonexistent"))

    def test_delete_user(self):
        """Test deleting user."""
        self.assertTrue(self.api.delete_user(self.test_user.id))
        self.assertIsNone(self.api.get_user(self.test_user.id))

        # Test deleting non-existent user
        self.assertFalse(self.api.delete_user(999))


if __name__ == "__main__":
    unittest.main()
