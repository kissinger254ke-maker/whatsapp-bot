def ai_response_handler(user_message):
    """
    Handles the user's message and generates an appropriate AI response.
    """
    # Example of a simple response logic (can be more complex)
    if "hello" in user_message.lower():
        return "Hello! How can I assist you today?"
    elif "help" in user_message.lower():
        return "Sure! What do you need help with?"
    else:
        return "I'm sorry, I don't understand that."

# Example usage
if __name__ == '__main__':
    user_input = input("You: ")
    print("AI:", ai_response_handler(user_input))