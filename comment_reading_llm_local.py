from openai import OpenAI
import os
import json
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o") # model doesn't matter we're just counting tokens

def count_tokens(text):
    return len(encoding.encode(text))

client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

## read in the complaints.json file
with open("complaints.json", "r") as f:
    complaints = json.load(f)



## there are many files of comments in /Users/annhoward/src/comment_reader/comments/tiktok and /Users/annhoward/src/comment_reader/comments/instagram

tiktok_folder = "/Users/annhoward/src/comment_reader/comments/tiktok"
instagram_folder = "/Users/annhoward/src/comment_reader/comments/instagram"

tiktok_comments = []
instagram_comments = []

for file in os.listdir(tiktok_folder):
    with open(os.path.join(tiktok_folder, file), "r") as f:
        tiktok_comments.append(f.read())

for file in os.listdir(instagram_folder):
    with open(os.path.join(instagram_folder, file), "r") as f:
        instagram_comments.append(f.read())
        
platforms = ["tiktok", "instagram"]

for comments in [tiktok_comments, instagram_comments]:
    platform = platforms.pop(0)
    platform_comments_to_complaints = {}
    print(f"Processing {platform} {len(comments)} comments")
    


    comments_to_complaints = {}

    for comment in comments:
        if comment in comments_to_complaints:
            complaints_returned = comments_to_complaints[comment]
            for complaint in complaints_returned:
                complaints[complaint] = complaints.get(complaint, 0) + 1
            continue
        print(f"Processing comment {count_tokens(comment)} tokens")
        if count_tokens(comment) > 4096: # chunk it into 4096 token chunks
            chunks = [comment[i:i+4096] for i in range(0, len(comment), 4096)]
        else:
            chunks = [comment]
            
            
        for chunk in chunks:
                try:
                    
                    complaints_list = list(complaints.keys())

                    prompt = f"""
                    It's your role to normalize the complaints in my comments. You'll review each comment thread one at a time and come up with a normalized version of the complaint.

                    Here are the complaints you've seen so far:
                    {"\n- ".join(complaints_list)}.

                    Here is the comment you're reviewing:
                    {comment}

                    You need to normalize the complaint to one or more of the complaints in the list, OR, if the complaint is not in the list, you need to add a new complaint to the list.

                    The end goal is to have a vote tally of all the complaints in the list, where slight variations, different ways of saying the same thing, and other variations are all counted as the same complaint. If it's meaningfully different, add another complaint to the list.
                    
                    Each sentence you return will be considered a separate complaint, so each complaint should only be a single sentence. A script will parse the output and split on the . character.
                    
                    Eventually, a video will be made for each complaint by me, a content creator, to whom these comments are addressed, in order according to the vote tally (so please only return new complaints if they are not in the list, not if they're only slightly different).

                    Either return one or more of the normalized complaints EXACTLY as it appears in the list, or add a new complaint to the list by returning a new sentence that is a complaint. 
                    These will be added as keys to a dictionary data structure in python that will be used to tally the complaints.
                    Do not return any other text than the normalized complaints, such as "The AI art issue maps directly to an existing entry" or "The Memphis environmental justice example fits under "Data centers are harming ecosystems"" as this will cause the script to log these as separate complaints due to the extra text.
                    """
                    print(prompt)

                    response = client.chat.completions.create(
                        model="qwq-32b-mlx",
                        messages=[{"role": "user", "content": prompt}]   
                    )
                    complaint = response.choices[0].message.content
                    ## strip out the <think> and </think> tags and all content in between them
                    think_start = complaint.find("<think>")
                    think_end = complaint.find("</think>")
                    if think_start != -1 and think_end != -1:
                        complaint = complaint[think_end+len("</think>"):]
                    complaint = complaint.strip()
                    ## now split on the . character
                    complaints_returned = complaint.split(".")
                    ## some complaints aren't given with . at the end, so we'll see 2 spaces, we should split on 2 spaces as well, but not all elements will have 2 spaces
                    double_spaced_complaints = [complaint_returned.split("  ") for complaint_returned in complaints_returned if "  " in complaint_returned]
                    complaints_returned = [complaint_returned for complaint_returned in complaints_returned if "  " not in complaint_returned]
                    complaints_returned = complaints_returned + [item for sublist in double_spaced_complaints for item in sublist]
                    
                    for complaint_returned in complaints_returned:
                        complaint_returned = complaint_returned.strip()
                        complaint_returned = complaint_returned.replace("\n", "")
                        complaints[complaint_returned] = complaints.get(complaint_returned, 0) + 1
                    comments_to_complaints[comment] = comments_to_complaints.get(comment, []) + complaints_returned 
                    platform_comments_to_complaints[comment] = platform_comments_to_complaints.get(comment, []) + complaints_returned 
                    ## write the tallies to a file for each comment
                    with open(f"current_vote_tally.json", "w") as f:
                        json.dump(complaints, f)
                    
                    with open(f"current_comments_to_complaints_{platform}.json", "w") as f:
                        json.dump(comments_to_complaints, f)
                    
                    with open(f"current_comments_to_complaints.json", "w") as f:
                        json.dump(comments_to_complaints, f)
                        
                    with open(f"current_comments_to_complaints_{platform}.json", "w") as f:
                        json.dump(comments_to_complaints, f)
                        
                    with open(f"complaints.json", "w") as f:
                        json.dump(complaints, f)

                        print(response.choices[0].message.content)
                except Exception as e:
                    print(f"Error processing comment: {e}")
                    print(f"Comment: {comment}")
                    continue

## write them to a file at the end
with open("complaints.json", "w") as f:
    json.dump(complaints, f)

with open("comments_to_complaints.json", "w") as f:
    json.dump(comments_to_complaints, f)