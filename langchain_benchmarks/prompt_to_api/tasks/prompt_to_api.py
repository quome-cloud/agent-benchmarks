"""Write REST APIs from a given the product requirements given in the user prompt

Use the command line and code execution tools to create the Python source code and the Dockerfile
to create the API.

APIs images will be built and run with the following commands
`docker build -t app`
`docker run -p 8000:8000 app`

They will then be evaluated on the port 8000, and the Swagger API docs / documentation will be expected at the following URL
http://localhost:8000/docs

APIs are expected to follow Restful API conventions

Example:
Create a social media platform for creating channels, and posting short text messages to the channels

GET     /channels                               list all channels
PUT     /channels                               create a new channel
GET     /channels/{channel_id}                  get a channel and all posts in it
POST    /channels/{channel_id}                  update a channel settings
PUT     /channels/{channel_id}/post             create a short text post in a channel
GET     /channels/{channel_id}/post/{post_id}   get a post in a channel

Prompt: {}
"""

DATASET_TINY = []


PROMPT_TO_API = ToolUsageTask(
    name="Prompt to API",
    create_environment=get_environment,
    instructions=(
        "You are requested to solve math questions in an alternate "
        "mathematical universe. The operations have been altered to yield "
        "different results than expected. Do not guess the answer or rely on your "
        " innate knowledge of math. Use the provided tools to answer the question. "
        "While associativity and commutativity apply, distributivity does not. Answer "
        "the question using the fewest possible tools. Only include the numeric "
        "response without any clarifications."
    ),
    description=(
        """\
An environment that contains a few basic math operations, but with altered results.

For example, multiplication of 5*3 will be re-interpreted as 5*3*1.1. \
The basic operations retain some basic properties, such as commutativity, \
associativity, and distributivity; however, the results are different than expected.

The objective of this task is to evaluate the ability to use the provided tools to \
solve simple math questions and ignore any innate knowledge about math.

This task is associated with 20 test examples.
"""
    ),
    eval_params={
        "output_evaluation": "qa_math_without_question",
    },
)
