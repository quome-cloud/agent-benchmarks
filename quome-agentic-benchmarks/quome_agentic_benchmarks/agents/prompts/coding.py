prompt_to_api_task_prompt = """Your task is to write functional REST APIs from the given requirements provided by the product manager.

APIs images will be built and run with the following commands:
`docker build -t app`
`docker run -p 8000:8000 app`

APIs will be evaluated on port 8000, and the Swagger API docs / documentation will be expected at the following URL
http://localhost:8000/docs

APIs are expected to follow Restful API conventions

Prompt: $prompt
"""

example_prompt_to_api = """

Example:
Create a social media platform for creating channels, and posting short text messages to the channels

GET     /channels                               list all channels
PUT     /channels                               create a new channel
GET     /channels/{channel_id}                  get a channel and all posts in it
POST    /channels/{channel_id}                  update a channel settings
PUT     /channels/{channel_id}/post             create a short text post in a channel
GET     /channels/{channel_id}/post/{post_id}   get a post in a channel"""
