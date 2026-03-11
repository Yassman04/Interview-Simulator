from speech_to_text import listen_to_user


def run_interview():
    print("\nWelcome to your mock interview.")

    # This calls your function from the other file
    user_answer = listen_to_user()

    print(f"\n-------- FULL TRANSCRIPT --------\n\n {user_answer}")
    # Next step: Send user_answer to the LLM...


if __name__ == "__main__":
    run_interview()
