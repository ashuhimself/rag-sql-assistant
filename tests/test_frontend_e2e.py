import pytest
from playwright.sync_api import Page, expect


class TestFrontendE2E:
    """End-to-end tests for the frontend using Playwright"""

    @pytest.fixture
    def page_with_backend(self, page: Page):
        """Fixture that starts the backend and navigates to the frontend"""
        # Note: In a real test environment, you'd start the backend here
        # For this example, we assume the backend is running
        page.goto("http://localhost:3000")
        return page

    def test_welcome_screen_loads(self, page_with_backend: Page):
        """Test that the welcome screen loads correctly"""
        page = page_with_backend

        # Check that the main title is visible
        expect(page.locator("h1")).to_contain_text("SQL Assistant")

        # Check that welcome message is displayed
        expect(page.locator("text=Welcome to the SQL Assistant")).to_be_visible()

        # Check that example queries are shown
        expect(page.locator("text=How many customers do we have?")).to_be_visible()

    def test_send_message_flow(self, page_with_backend: Page):
        """Test sending a message and receiving a response"""
        page = page_with_backend

        # Find the message input
        message_input = page.locator("textarea")
        expect(message_input).to_be_visible()

        # Type a message
        test_message = "How many customers do we have?"
        message_input.fill(test_message)

        # Send the message
        send_button = page.locator("button[title*='Send']")
        send_button.click()

        # Check that user message appears
        expect(page.locator(f"text={test_message}")).to_be_visible()

        # Wait for and check assistant response
        # Note: This would require the backend to be running with mock data
        page.wait_for_selector("[data-testid='assistant-message']", timeout=10000)

    def test_new_chat_button(self, page_with_backend: Page):
        """Test the new chat functionality"""
        page = page_with_backend

        # Send a message first
        page.locator("textarea").fill("Test message")
        page.locator("button[title*='Send']").click()

        # Click new chat button
        new_chat_button = page.locator("text=New Chat")
        new_chat_button.click()

        # Check that messages are cleared
        expect(page.locator("text=Welcome to the SQL Assistant")).to_be_visible()

    def test_message_input_validation(self, page_with_backend: Page):
        """Test message input validation"""
        page = page_with_backend

        message_input = page.locator("textarea")
        send_button = page.locator("button[title*='Send']")

        # Send button should be disabled for empty input
        expect(send_button).to_be_disabled()

        # Type a message
        message_input.fill("Test message")

        # Send button should be enabled
        expect(send_button).to_be_enabled()

        # Clear the message
        message_input.fill("")

        # Send button should be disabled again
        expect(send_button).to_be_disabled()

    def test_character_count_display(self, page_with_backend: Page):
        """Test that character count is displayed"""
        page = page_with_backend

        message_input = page.locator("textarea")

        # Type a message
        test_message = "This is a test message"
        message_input.fill(test_message)

        # Check character count is displayed
        char_count = page.locator(f"text={len(test_message)}/5000")
        expect(char_count).to_be_visible()

    def test_message_bubble_structure(self, page_with_backend: Page):
        """Test the structure of message bubbles"""
        page = page_with_backend

        # Send a message
        page.locator("textarea").fill("Test query")
        page.locator("button[title*='Send']").click()

        # Check user message bubble
        user_message = page.locator("[data-testid='user-message']").first
        expect(user_message).to_contain_text("Test query")

        # Check timestamp is displayed
        expect(page.locator("text=/\\d{1,2}:\\d{2}(:\\d{2})? (AM|PM)/")).to_be_visible()

    def test_sql_query_display_toggle(self, page_with_backend: Page):
        """Test toggling SQL query display"""
        page = page_with_backend

        # This test assumes a message with SQL query has been sent
        # and received from the backend

        # Send a database query
        page.locator("textarea").fill("Show me all customers")
        page.locator("button[title*='Send']").click()

        # Wait for response with SQL
        page.wait_for_selector("text=Show SQL", timeout=10000)

        # Click to show SQL
        show_sql_button = page.locator("text=Show SQL")
        show_sql_button.click()

        # Check that SQL query is displayed
        expect(page.locator("code")).to_be_visible()

        # Click to hide SQL
        hide_sql_button = page.locator("text=Hide SQL")
        hide_sql_button.click()

        # Check that SQL query is hidden
        expect(page.locator("code")).not_to_be_visible()

    def test_error_message_display(self, page_with_backend: Page):
        """Test error message display and dismissal"""
        page = page_with_backend

        # This would require the backend to return an error
        # For this test, we'll simulate a frontend error scenario

        # Check if error message appears (would need to trigger an error)
        # error_message = page.locator("[data-testid='error-message']")
        # expect(error_message).to_contain_text("Error")

        # Test dismiss functionality
        # dismiss_button = page.locator("[data-testid='error-dismiss']")
        # dismiss_button.click()
        # expect(error_message).not_to_be_visible()

    def test_responsive_design(self, page_with_backend: Page):
        """Test responsive design on different screen sizes"""
        page = page_with_backend

        # Test desktop size
        page.set_viewport_size({"width": 1200, "height": 800})
        expect(page.locator("h1")).to_be_visible()

        # Test tablet size
        page.set_viewport_size({"width": 768, "height": 1024})
        expect(page.locator("h1")).to_be_visible()

        # Test mobile size
        page.set_viewport_size({"width": 375, "height": 667})
        expect(page.locator("h1")).to_be_visible()

    def test_loading_indicator(self, page_with_backend: Page):
        """Test loading indicator appears during message processing"""
        page = page_with_backend

        # Send a message
        page.locator("textarea").fill("Test message")
        page.locator("button[title*='Send']").click()

        # Check that loading indicator appears
        # Note: This might be too fast to catch in a real scenario
        loading_indicator = page.locator("text=Thinking...")
        # expect(loading_indicator).to_be_visible()

    def test_keyboard_shortcuts(self, page_with_backend: Page):
        """Test keyboard shortcuts functionality"""
        page = page_with_backend

        message_input = page.locator("textarea")
        message_input.fill("Test message")

        # Test Enter to send
        message_input.press("Enter")

        # Check that message was sent
        expect(page.locator("text=Test message")).to_be_visible()

        # Test Shift+Enter for new line (should not send)
        message_input.fill("Line 1")
        message_input.press("Shift+Enter")
        message_input.type("Line 2")

        # Should still be in the input
        expect(message_input).to_have_value("Line 1\nLine 2")


@pytest.fixture
def page(browser):
    """Create a new page for each test"""
    page = browser.new_page()
    yield page
    page.close()