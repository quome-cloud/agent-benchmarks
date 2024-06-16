prompt_to_api_task_prompt = """Write REST APIs from a given the product requirements given in the user prompt

Use the command line and code execution tools to create the Python source code and the Dockerfile
to create the API.

APIs images will be built and run with the following commands
`docker build -t app`
`docker run -p 8000:8000 app`

They will then be evaluated on the port 8000, and the Swagger API docs / documentation will be expected at the following URL
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
