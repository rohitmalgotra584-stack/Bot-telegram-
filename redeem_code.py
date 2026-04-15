
import random
import string

class RedeemCodeSystem:
    def __init__(self, db_execute, get_setting, set_setting, safe_send):
        self.db_execute = db_execute
        self.get_setting = get_setting
        self.set_setting = set_setting
        self.safe_send = safe_send

    def generate_code(self, length=10):
        """Generate a random redeem code of given length."""
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(length))

    def add_code(self, code: str, value: int):
        """Add a redeem code to the database."""
        query = "INSERT INTO redeem_codes (code, value, status) VALUES (?, ?, ?)"
        self.db_execute(query, (code, value, 'active'))

    def remove_code(self, code: str):
        """Remove a redeem code from the database after use."""
        query = "UPDATE redeem_codes SET status = 'used' WHERE code = ?"
        self.db_execute(query, (code,))

    def list_codes(self):
        """Retrieve all active redeem codes."""
        query = "SELECT code, value FROM redeem_codes WHERE status = 'active'"
        return self.db_execute(query)

    def redeem_code(self, user_id, code: str, user_balance: int):
        """Handle redeem code by the user."""
        # Ensure the user has a balance above the minimum withdrawal limit
        min_withdrawal = 15
        gst_cut = 5

        if user_balance < min_withdrawal:
            return "Your balance is below the minimum withdrawal limit of ₹15."

        # Get the redeem code value
        query = "SELECT value FROM redeem_codes WHERE code = ? AND status = 'active'"
        code_value = self.db_execute(query, (code,))

        if not code_value:
            return "This code is invalid or already used."

        code_value = code_value[0][0]

        # Calculate GST cut and amount to be credited to the user's balance
        amount_to_credit = code_value - gst_cut

        # Update user balance and mark the code as used
        query = "UPDATE users SET balance = balance + ? WHERE user_id = ?"
        self.db_execute(query, (amount_to_credit, user_id))

        # Remove the redeem code after use
        self.remove_code(code)

        return f"Code redeemed successfully! ₹{amount_to_credit} has been added to your balance."
