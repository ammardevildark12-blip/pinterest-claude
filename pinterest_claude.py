#!/usr/bin/env python3
"""
Pinterest + Claude Integration
Fetches Pinterest board data and generates insights using Claude AI.
"""

import os
import json
import requests
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic()

# Pinterest API endpoints (requires API key)
PINTEREST_API_BASE = "https://api.pinterest.com/v1"
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN", "")

class PinterestClaudeIntegration:
    def __init__(self, pinterest_token: str = PINTEREST_ACCESS_TOKEN):
        """Initialize Pinterest + Claude integration."""
        self.pinterest_token = pinterest_token
        self.conversation_history = []

    def get_user_boards(self) -> list:
        """Fetch user's Pinterest boards."""
        if not self.pinterest_token:
            print("⚠️  PINTEREST_ACCESS_TOKEN not set. Using mock data.")
            return self._get_mock_boards()

        headers = {"Authorization": f"Bearer {self.pinterest_token}"}
        url = f"{PINTEREST_API_BASE}/me/boards"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching boards: {e}")
            return self._get_mock_boards()

    def get_board_pins(self, board_id: str, limit: int = 10) -> list:
        """Fetch pins from a specific board."""
        if not self.pinterest_token:
            return self._get_mock_pins()

        headers = {"Authorization": f"Bearer {self.pinterest_token}"}
        url = f"{PINTEREST_API_BASE}/boards/{board_id}/pins"
        params = {"fields": "id,url,note,image,created_at", "limit": limit}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching pins: {e}")
            return self._get_mock_pins()

    def _get_mock_boards(self) -> list:
        """Return mock Pinterest board data for testing."""
        return [
            {
                "id": "board_1",
                "name": "Home Decor Ideas",
                "description": "Modern and minimalist home decor inspiration",
                "url": "https://pinterest.com/user/home-decor-ideas"
            },
            {
                "id": "board_2",
                "name": "Recipe Collection",
                "description": "Healthy and delicious recipes",
                "url": "https://pinterest.com/user/recipe-collection"
            }
        ]

    def _get_mock_pins(self) -> list:
        """Return mock Pinterest pins for testing."""
        return [
            {
                "id": "pin_1",
                "note": "Minimalist living room with plants",
                "url": "https://pinterest.com/pin/12345"
            },
            {
                "id": "pin_2",
                "note": "Healthy smoothie bowl recipe",
                "url": "https://pinterest.com/pin/67890"
            }
        ]

    def analyze_board_with_claude(self, board_data: dict, pins: list) -> str:
        """Use Claude to analyze a Pinterest board."""
        prompt = f"""
Analyze this Pinterest board and provide insights:

Board Name: {board_data.get('name', 'Unknown')}
Description: {board_data.get('description', 'No description')}
URL: {board_data.get('url', 'N/A')}

Recent Pins:
{json.dumps(pins[:5], indent=2)}

Please provide:
1. Overall theme and aesthetic
2. Target audience
3. Content suggestions
4. SEO/discoverability tips
5. Engagement recommendations
"""

        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system="You are a Pinterest strategy expert. Analyze boards and provide actionable insights.",
            messages=self.conversation_history
        )

        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def generate_pin_caption(self, pin_note: str, board_theme: str) -> str:
        """Generate an optimized pin caption using Claude."""
        prompt = f"""
Generate an engaging Pinterest pin caption for this pin:

Pin Description: {pin_note}
Board Theme: {board_theme}

Requirements:
- Include relevant hashtags (#)
- Keep it concise (150 chars max)
- Make it searchable
- Add a call-to-action if appropriate
"""

        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            system="You are a Pinterest content expert. Create catchy, SEO-optimized pin captions.",
            messages=self.conversation_history
        )

        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def chat(self, user_message: str) -> str:
        """Have a multi-turn conversation with Claude about Pinterest."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system="You are a Pinterest strategy advisor. Help users optimize their Pinterest presence.",
            messages=self.conversation_history
        )

        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message


def main():
    """Interactive CLI for Pinterest + Claude."""
    print("🎨 Pinterest + Claude Integration")
    print("=" * 50)

    integration = PinterestClaudeIntegration()

    while True:
        print("\n📌 Options:")
        print("1. Analyze my boards")
        print("2. Generate pin captions")
        print("3. Chat with Pinterest expert")
        print("4. Exit")

        choice = input("\nSelect option (1-4): ").strip()

        if choice == "1":
            print("\n📂 Fetching your boards...")
            boards = integration.get_user_boards()

            if boards:
                for i, board in enumerate(boards[:3], 1):
                    print(f"\n{i}. {board.get('name', 'Unknown Board')}")
                    print(f"   {board.get('description', 'No description')}")

                    board_id = board.get("id")
                    if board_id:
                        pins = integration.get_board_pins(board_id, limit=5)
                        print(f"\n   Analyzing with Claude...")
                        analysis = integration.analyze_board_with_claude(board, pins)
                        print(f"\n   {analysis}")
            else:
                print("❌ No boards found or API unavailable.")

        elif choice == "2":
            note = input("Enter pin description: ").strip()
            theme = input("Enter board theme: ").strip()

            if note and theme:
                print("\n✨ Generating caption...")
                caption = integration.generate_pin_caption(note, theme)
                print(f"\n📍 Suggested Caption:\n{caption}")
            else:
                print("❌ Please provide both pin description and theme.")

        elif choice == "3":
            message = input("\n💬 Ask the Pinterest expert: ").strip()
            if message:
                response = integration.chat(message)
                print(f"\n🤖 Expert:\n{response}")

        elif choice == "4":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid option. Please select 1-4.")

if __name__ == "__main__":
    main()
