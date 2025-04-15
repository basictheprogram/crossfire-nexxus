from pathlib import Path

import tiktoken

# Load your tokenizer - use "cl100k_base" for GPT-4 models or check the specific model tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")

# Define the max token limit for chunking
MAX_TOKENS = 4000


def split_text_to_token_chunks(filename: str):
    """Read a file, tokenize its contents, and split it into chunks."""
    # Step 1: Read the entire text from the file
    with open(filename) as file:
        text = file.read()

    # Step 2: Tokenize the entire text
    tokens = tokenizer.encode(text)

    # Step 3: Split the text into diff blocks
    diff_blocks = []  # List to store blocks of diff data
    current_block = []  # Stores lines of the current diff block
    current_tokens = []  # Stores tokens for the current diff block

    # Split the text based on "diff --git" entries to preserve diff integrity
    for line in text.splitlines(True):
        # Tokenize the line
        line_tokens = tokenizer.encode(line)

        # Check if the line starts with a diff entry indicating a new block
        if line.startswith("diff --git"):
            # If there's an existing block, add it to the diff_blocks list
            if current_tokens:
                diff_blocks.append((current_block, current_tokens))

            # Reset for the new diff block
            current_block = [line]
            current_tokens = line_tokens
        else:
            # Add this line to the current diff block
            current_block.append(line)
            current_tokens += line_tokens

    # Don't forget to add the last block
    if current_tokens:
        diff_blocks.append((current_block, current_tokens))

    # Step 4: Chunk the diff blocks based on the MAX_TOKENS limit
    chunk_text = []  # Holds the text for the current chunk
    chunk_tokens = []  # Holds the tokenized text for the current chunk

    # Process each diff block
    for block, block_tokens in diff_blocks:
        # Check if adding this block exceeds the MAX_TOKENS limit
        if len(chunk_tokens) + len(block_tokens) > MAX_TOKENS:
            # If it does, save the current chunk and start a new one
            output_filename = f"chunk_{len(chunk_text) + 1}.txt"
            with open(output_filename, "w") as chunk_file:
                chunk_file.writelines(chunk_text)
            print(f"Saved {output_filename}")

            # Start a new chunk
            chunk_text = block
            chunk_tokens = block_tokens
        else:
            # If the block fits, add it to the current chunk
            chunk_text.extend(block)
            chunk_tokens.extend(block_tokens)

    # Save the final chunk
    if chunk_tokens:
        output_filename = f"chunk_{len(chunk_text) + 1}.txt"
        with Path.open(output_filename, "w") as chunk_file:
            chunk_file.writelines(chunk_text)
        print(f"Saved {output_filename}")


# Run the function if the script is executed directly
if __name__ == "__main__":
    # Path to the file to be split
    split_text_to_token_chunks("../zzz.diff")
