# LangSmith libs
from langchain.smith import RunEvalConfig, run_on_dataset
from langsmith       import Client

# other libs
import pytest
import uuid

# custom libs
import chains




# =================== SETUP =================== #

@pytest.fixture
def chain_1():
    chain = chains.assistant_chain("Bob")

    return chain.getChain()


@pytest.fixture
def chain_2():
    chain = chains.documentation_chain("https://docs.smith.langchain.com")

    return chain.getChain()

# ============================================= #




# =================== TESTS =================== #

# This test uses the chain_1 fixture (which is just re-usable code that
# executes before the test is run)
def test_name(chain_1):
    # instantiate LangSmith client
    client = Client()

    # Define input/output
    input_text  = "What is your name?"
    output_text = chain_1.invoke({"question": input_text})
    print("Question: " + input_text)
    print("Answer:   " + output_text)
    
    assert "bob" in output_text.lower()


# This test uses the chain_1 fixture (which is just re-usable code that
# executes before the test is run)
def test_basic_arithmetic(chain_1):
    # instantiate LangSmith client
    client = Client()

    # Define input/output
    input_text  = "What is 5 + 7?"
    output_text = chain_1.invoke({"question": input_text})
    print("Question: " + input_text)
    print("Answer:   " + output_text)
    
    assert "12" in output_text.lower()


# This test uses the chain_2 fixture (which is just re-usable code that
# executes before the test is run)
def test_llm_evaluators(chain_2):
    # instantiate LangSmith client
    client = Client()


    # define question and expected output example test set for qa evaluators in langsmith.
    examples = [
        ("what is langchain?", "langchain is an open-source framework for building applications using large language models. it is also the name of the company building langsmith."),
        ("how might i query for all runs in a project?", "client.list_runs(project_name='my-project-name'), or in typescript, client.listruns({projectname: 'my-project-anme'})"),
        ("what's a langsmith dataset?", "a langsmith dataset is a collection of examples. each example contains inputs and optional expected outputs or references for that data point."),
        ("how do i use a traceable decorator?", """the traceable decorator is available in the langsmith python sdk. to use, configure your environment with your api key,\
    import the required function, decorate your function, and then call the function. below is an example:
    ```python
    from langsmith.run_helpers import traceable
    @traceable(run_type="chain") # or "llm", etc.
    def my_function(input_param):
        # function logic goes here
        return output
    result = my_function(input_param)
    ```"""),
        ("can i trace my llama v2 llm?", "so long as you are using one of langchain's llm implementations, all your calls can be traced"),
        ("why do i have to set environment variables?", "environment variables can tell your langchain application to perform tracing and contain the information necessary to authenticate to langsmith."
         " while there are other ways to connect, environment variables tend to be the simplest way to configure your application."),
        ("how do i move my project between organizations?", "langsmith doesn't directly support moving projects between organizations.")
    ]


    # create a dataset for langsmith evaluator using the example qa list from above
    dataset_name = f"retrieval qa questions {str(uuid.uuid4())}"
    dataset = client.create_dataset(dataset_name=dataset_name)
    for q, a in examples:
        client.create_example(inputs={"question": q}, outputs={"answer": a}, dataset_id=dataset.id)


    # run qa evaluators
    eval_config = RunEvalConfig(
        evaluators=["qa"],
        # if you want to configure the eval llm:
        # eval_llm=chatanthropic(model="claude-2", temperature=0)
    )


    # Run the evaluation. This makes predictions over the dataset and then uses
    # the "QA" evaluator to check the correctness on each data point.
    _ = client.run_on_dataset(
        dataset_name=dataset_name,
        llm_or_chain_factory=lambda: chain_2,
        evaluation=eval_config,
    )


