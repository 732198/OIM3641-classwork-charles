from datetime import datetime
from dateutil import parser
import hashlib


class User:
    def __init__(self, username='', password='', email='', birthday=''):
        # Store as private attribute _username to support the property getter/setter
        self._username = username
        self.password = self._encrypt_password(password) if password else ''
        self.email = email
        self.birthday = birthday

    # -- from video 4 updates ---
    @property
    def username(self):
        """Getter for username."""
        return self._username

    @username.setter
    def username(self, new_username):
        """Setter for username with validation."""
        if not new_username or not new_username.strip():
            raise ValueError("Username cannot be empty or blank.")
        self._username = new_username

    # --- from video 3 updates ---
    def _encrypt_password(self, password):
        """Private helper to convert plain text password into a SHA-256 hash."""
        encoded_pw = password.encode('utf-8')
        return hashlib.sha256(encoded_pw).hexdigest()

    def check_password(self, password_to_check):
        """Verifies if a plain text password matches the stored hash."""
        return self.password == self._encrypt_password(password_to_check)

    def get_age(self):
        """Parses birthday string and calculates age in years."""
        if not self.birthday:
            return None
        dob = parser.parse(self.birthday)
        now = datetime.now()
        days_diff = (now - dob).days
        return days_diff // 365

    # --- from video 3 updates ---
    def __eq__(self, other):
        """Overrides '==' to check if two User objects share the same username."""
        if isinstance(other, User):
            return self.username == other.username
        return False

    # --- from video 2 updates ---
    def __str__(self):
        """Informal string representation for end-user display."""
        age = self.get_age()
        age_str = f"{age} years old" if age is not None else "Age unknown"
        return f"User: {self.username} ({age_str}, Email: {self.email})"

    def __repr__(self):
        """Formal string representation for debugging and introspection."""
        return f"{self.__class__.__name__}({self.__dict__})"


# --- Testing All Functionality ---
if __name__ == "__main__":
    # Create user instances
    user1 = User('johndoe', 'Secret123', 'john@example.com', '1990-05-15')
    user2 = User('johndoe', 'DifferentPass', 'john2@example.com', '1995-01-01')

    print("--- 1. String Representations ---")
    print("Informal (__str__):", user1)
    print("Formal (__repr__):  ", repr(user1))

    print("\n--- 2. Password Hashing & Verification ---")
    print("Hashed Password:", user1.password)
    print("Check 'WrongPass':", user1.check_password('WrongPass'))
    print("Check 'Secret123':", user1.check_password('Secret123'))

    print("\n--- 3. Equality Check (__eq__) ---")
    print("Is user1 == user2?", user1 == user2)

    print("\n--- 4. Property Getter & Setter ---")
    user1.username = 'jonathan'
    print("Updated Username:", user1.username)

    try:
        user1.username = ""  # Triggers validation exception
    except ValueError as e:
        print("Validation Caught Error:", e)
        