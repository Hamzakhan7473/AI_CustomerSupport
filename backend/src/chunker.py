import re

def chunk_data(input_file: str, output_file: str, sentences_per_chunk: int = 4):
    """
    Reads text from a file, splits it into sentences, and groups
    them into smaller, more meaningful chunks.

    Args:
        input_file: The path to the text file to chunk.
        output_file: The path to save the chunked data to.
        sentences_per_chunk: The number of sentences to include in each chunk.
    """
    print(f"Reading data from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split text into sentences using a regular expression
    # This handles periods, question marks, and exclamation marks
    sentences = re.split(r'(?<=[.?!])\s+', text)
    
    # Filter out any very short or empty sentences
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    chunks = []
    # Group sentences into chunks
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = " ".join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk)

    # Save the processed chunks to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(chunk + "\n\n") # Separate chunks with double newlines

    print(f"✅ Successfully created {len(chunks)} chunks.")
    print(f"Cleaned and chunked data saved to {output_file}")


if __name__ == '__main__':
    input_filename = "aven_data.txt"
    output_filename = "chunked_aven_data.txt"
    chunk_data(input_filename, output_filename)