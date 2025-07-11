import os
import json
import logging
from openai import OpenAI
import tiktoken

# Setup logging
logging.basicConfig(
    filename='comment_like_voter_llm.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Tokenizer for token counting
encoding = tiktoken.encoding_for_model("gpt-4o")
def count_tokens(text):
    return len(encoding.encode(text))

# Connect to LM Studio
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

# Tool function to record votes
def record_vote(complaint: str, votes: int):
    logger.info(f"Recording {votes} votes for complaint: {complaint}")
    global complaints
    complaints[complaint] = complaints.get(complaint, 0) + votes
    with open("like_weighted_complaints.json", "w") as f:
        json.dump(complaints, f, indent=2)

# Register tool for LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "record_vote",
            "description": "Records a number of votes for a complaint",
            "parameters": {
                "type": "object",
                "properties": {
                    "complaint": {
                        "type": "string",
                        "description": "The normalized complaint"
                    },
                    "votes": {
                        "type": "integer",
                        "description": "Number of votes (likes) to record"
                    }
                },
                "required": ["complaint", "votes"]
            }
        }
    }
]

# Load complaints
with open("complaints.json", "r") as f:
    complaints = json.load(f)

# Comment folders
tiktok_folder = "comments/tiktok"
instagram_folder = "comments/instagram"

platforms = [
    ("tiktok", tiktok_folder),
    ("instagram", instagram_folder)
]

with open("comments_to_complaints.json", "r") as f:
    comments_to_complaints = json.load(f)


for platform, folder in platforms:
    logger.info(f"Processing {platform} comments from {folder}")
    comments = []
    for file in os.listdir(folder):
        with open(os.path.join(folder, file), "r") as f:
            comment = f.read()
            ## is the comment longer than 4096 tokens?
            if count_tokens(comment) > 4096:
                ## chunk it into 4096 token chunks
                chunks = [comment[i:i+4096] for i in range(0, len(comment), 4096)]
                for chunk in chunks:
                    comments.append(chunk)
            else:
                comments.append(comment)
        
                
    logger.info(f"Loaded {len(comments)} comments from {platform}")

    for comment in comments:
        if comment in comments_to_complaints:
            logger.info(f"Comment {comment} already processed")
            continue
        try:
            
            logger.info(f"Processing comment ({count_tokens(comment)} tokens)")
            prompt = f"""
            Here is a comment: "{comment}"

            1. Normalize the complaint(s) in this comment. Use the existing complaints list below if possible. If not, add a new complaint.
            2. If you can tell how many likes this comment has, use the record_vote tool to record that many votes for each normalized complaint you extract from the comment. If you can't tell, just record 1 vote per complaint.
            2.5. If you can't tell how many likes this comment has, just record 1 vote per complaint.
            3. Only use the record_vote tool for each complaint.
            
            The end goal is to have a vote tally of all the complaints in the list, where slight variations, different ways of saying the same thing, and other variations are all counted as the same complaint. If it's meaningfully different, add another complaint to the list.
            The user will be using this vote tally to make a video about the complaints, so please make sure the complaints are as normalized as possible.

            Complaints list (so far, you can add to this list):
            {'\n- '.join(complaints.keys())}
            """
            response = client.chat.completions.create(
                model="qwq-32b-mlx",
                messages=[{"role": "user", "content": prompt}],
                tools=tools
            )
            complaints_returned = []
            # Handle tool calls
            for choice in response.choices:
                tool_calls = getattr(choice.message, "tool_calls", [])
                if tool_calls is None:
                    logger.error(f"No tool calls found for comment: {comment}")
                    comments_to_complaints[comment] = []
                    with open("comments_to_complaints.json", "w") as f:
                        json.dump(comments_to_complaints, f, indent=2)
                    continue
                for tool_call in tool_calls:
                    if tool_call.function.name == "record_vote":
                        args = json.loads(tool_call.function.arguments)
                        complaints_returned.append(args["complaint"])
                        record_vote(args["complaint"], args["votes"])
            comments_to_complaints[comment] = complaints_returned
            with open("comments_to_complaints.json", "w") as f:
                json.dump(comments_to_complaints, f, indent=2)
            
        except Exception as e:
            import traceback
            logger.error(f"Error processing comment: {e}")
            ## print the stack trace
            logger.error(traceback.format_exc())
            logger.error(f"Comment: {comment}")
            continue

logger.info("Processing complete. Complaints tally saved to like_weighted_complaints.json.") 