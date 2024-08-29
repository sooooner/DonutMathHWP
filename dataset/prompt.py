text_extract_system = """Task Description:
Extract all text content from the provided HTML snippet, including any mathematical expressions. Replace images with the placeholder [image], and ignore HTML tags and attributes. Ensure the extracted text is structured in a readable format, preserving the order of problem number, text, source, and options. Surround all mathematical expressions with dollar signs ($).

Instructions:
1. Extract the text content from the provided HTML snippet, ignoring any HTML tags and attributes.
2. Replace images with the placeholder [image].
3. Preserve the readability and structure of the text, ensuring each problem is clearly separated.
4. Surround all mathematical expressions with dollar signs ($).
5. Ensure the problem number, text, source, and options are included in the correct order.
6. Separate the problem number, text, source, options, and any other parts using newline characters ("\n").

JSON schema:
{
    "problems": {
        "type": "array",
        "description": "The list of problems included in a math problem.",
        "items": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Combined content of all parts of the problem, separated by newlines"
                }
            },
            "required": [
                "content"
            ]
        }
    }
}"""