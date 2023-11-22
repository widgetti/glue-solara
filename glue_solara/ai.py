import json
import os
import time

import solara
from glue_jupyter import JupyterApplication
from openai import NotFoundError, OpenAI

suggested_links = solara.reactive({})
suggested_renames = solara.reactive({})

# Declare tools for openai assistant to use
tools = [
    {
        "type": "function",
        "function": {
            "name": "suggest_link",
            "description": "Suggest a link between two columns from different datasets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_column_dataset": {
                        "type": "string",
                        "description": "a dataset name to be linked, e.g. 'w5'",
                    },
                    "first_column": {
                        "type": "string",
                        "description": "a column name to be linked, e.g. 'Right Ascension'",
                    },
                    "second_column_dataset": {
                        "type": "string",
                        "description": "a dataset name to be linked, e.g. 'w5_psc'",
                    },
                    "second_column": {
                        "type": "string",
                        "description": "a column name to be linked, e.g. 'RAJ2000'",
                    },
                },
                "required": [
                    "first_column_dataset",
                    "first_column",
                    "second_column_dataset",
                    "second_column",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_rename",
            "description": "Suggest a new, more descriptive name for a column.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column_dataset": {
                        "type": "string",
                        "description": "The dataset to which the column to be renamed belongs, e.g. 'w5'",
                    },
                    "original_name": {
                        "type": "string",
                        "description": "a column to be renamed, e.g. 'RAJ2000'",
                    },
                    "new_name": {
                        "type": "string",
                        "description": "a new column name, e.g. 'Right Ascension'",
                    },
                },
                "required": ["column_dataset", "original_name", "new_name"],
            },
        },
    },
]


def suggest_link(
    first_column_dataset: str, first_column: str, second_column_dataset: str, second_column: str
):
    suggested_link = {
        "link": [{first_column_dataset: first_column}, {second_column_dataset: second_column}],
        "is_chosen": True,
    }
    suggested_links.set([*suggested_links.value, suggested_link])
    return "Link Suggested"


def suggest_rename(column_dataset: str, original_name: str, new_name: str):
    suggested_name = {
        "rename": [{column_dataset: original_name}, {column_dataset: new_name}],
        "is_chosen": True,
    }
    suggested_renames.set([*suggested_renames.value, suggested_name])

    return "Rename Suggested"


functions = {"suggest_link": suggest_link, "suggest_rename": suggest_rename}


def ai_call(tool_call):
    function = tool_call.function
    name = function.name
    parameters = json.loads(function.arguments)
    function_output = functions[name](**parameters)
    return {
        "tool_call_id": tool_call.id,
        "output": function_output,
    }


def autolink(openai, thread_id: solara.Reactive[str], run_id: solara.Reactive[str], message: str):
    run = openai.beta.threads.create_and_run(
        assistant_id="asst_YCK18txotF9zJWNVB32hVzu2",
        thread={
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ]
        },
        tools=tools,
    )
    run_id.value = run.id
    thread_id.value = run.thread_id


def poll(openai, thread_id: solara.Reactive[str], run_id: solara.Reactive[str], cancel):
    if not run_id.value or thread_id.value is None:
        return
    completed = False
    while not completed:
        try:
            run = openai.beta.threads.runs.retrieve(run_id.value, thread_id=thread_id.value)
        except NotFoundError:
            print("Not found")
            time.sleep(0.2)
            continue
        if run.status == "requires_action":
            tool_outputs = []
            print("CALLING TOOLS:", run.required_action.submit_tool_outputs.tool_calls)
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                tool_output = ai_call(tool_call)
                tool_outputs.append(tool_output)
            openai.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id.value,
                run_id=run_id.value,
                tool_outputs=tool_outputs,
            )
        if run.status == "completed":
            run_id.set(None)
            thread_id.set(None)
            completed = True
            return
        time.sleep(0.1)
        if cancel.is_set():
            return


@solara.component
def LinkStep(
    step: solara.Reactive[int],
    popup_is_open: solara.Reactive[bool],
    app: JupyterApplication,
):
    openai = solara.use_memo(lambda: OpenAI(), dependencies=[], debug_name="openai_link")
    openai.api_key = os.getenv("OPENAI_API_KEY")

    run_id = solara.use_reactive(None)
    thread_id = solara.use_reactive(None)

    data_collection = app.data_collection
    list_of_columns = {}
    for data in data_collection:
        list_of_columns[data.label] = [attribute for attribute in data.components]

    def save_and_next():
        for item in suggested_links.value:
            if item["is_chosen"]:
                key1 = list(item["link"][0].keys())[0]
                key2 = list(item["link"][1].keys())[0]
                data1_index = list(list_of_columns.keys()).index(key1)
                data2_index = list(list_of_columns.keys()).index(key2)
                # Find index of the component we are looking at
                data1_component_index = list_of_columns[key1].index(
                    list(item["link"][0].values())[0]
                )
                data2_component_index = list_of_columns[key2].index(
                    list(item["link"][1].values())[0]
                )
                app.add_link(
                    data_collection[data1_index],
                    data_collection[data1_index].components[data1_component_index],
                    data_collection[data2_index],
                    data_collection[data2_index].components[data2_component_index],
                )

        step.value -= 1
        popup_is_open.value = False

    message = f"""Here are some datasets with the names of columns present in each dataset: {list_of_columns}.
        Could you suggest which columns represent the same thing."""

    solara.use_memo(
        lambda: autolink(openai, thread_id, run_id, message), dependencies=[popup_is_open.value]
    )
    result = solara.use_thread(
        lambda cancel: poll(openai, thread_id, run_id, cancel),
        dependencies=[run_id.value, thread_id.value],
        intrusive_cancel=False,
    )

    if result.state == solara.ResultState.RUNNING:
        solara.HTML(tag="h2", unsafe_innerHTML="Waiting for response from OpenAI...")
        solara.ProgressLinear(result.state == solara.ResultState.RUNNING)
    elif result.state == solara.ResultState.ERROR:
        solara.Error(f"Error while calling OpenAI API: {result.error}")
    else:
        with solara.v.List():
            if len(suggested_links.value) == 0:
                with solara.v.ListItem():
                    with solara.v.ListItemContent():
                        solara.HTML(tag="h2", unsafe_innerHTML="No links suggested")
            for index, item in enumerate(suggested_links.value):

                def set_link_chosen(new_value, index=index):
                    suggested_links.value[index]["is_chosen"] = new_value

                with solara.v.ListItem():
                    with solara.v.ListItemContent():
                        with solara.Row(style={"align-items": "center"}, justify="space-between"):
                            solara.HTML(
                                tag="h2",
                                unsafe_innerHTML=list(item["link"][0].values())[0],
                            )
                            with solara.ToggleButtonsSingle(
                                mandatory=False,
                                value=item["is_chosen"],
                                on_value=set_link_chosen,
                            ):
                                solara.Button(
                                    value=True,
                                    icon_name="mdi-link",
                                    color="primary",
                                    text=True,
                                )
                            solara.HTML(
                                tag="h2",
                                unsafe_innerHTML=list(item["link"][1].values())[0],
                            )
        with solara.Row(justify="end"):
            solara.Button("Save and Exit", on_click=save_and_next, color="primary")


@solara.component
def AutoLink(app: JupyterApplication):
    suggestion_popup_is_open = solara.use_reactive(False)
    current_step = solara.use_reactive(0)

    def start_autolink():
        current_step.value += 1
        suggestion_popup_is_open.value = True

    solara.Button(
        icon_name="mdi-auto-fix",
        on_click=start_autolink,
        text=True,
    )

    with solara.v.Dialog(
        v_model=suggestion_popup_is_open.value,
        width="unset",
        style_="min-height: 20vh; min-width: 400px;",
    ):
        with solara.v.Stepper(v_model=current_step.value):
            with solara.v.StepperHeader():
                with solara.v.StepperStep(step=1, complete=current_step.value > 1):
                    solara.HTML(tag="h2", unsafe_innerHTML="Link Columns")
            with solara.v.StepperItems():
                with solara.v.StepperContent(step=1):
                    if current_step.value == 1:  # To not call OpenAI before dialog opens
                        LinkStep(
                            step=current_step,
                            popup_is_open=suggestion_popup_is_open,
                            app=app,
                        )
