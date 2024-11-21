#
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Read the configuration file to import tasks"""

import os
import sys
import yaml
import typing

from absl import logging
from docs_agent.utilities.helpers import get_project_path, resolve_path


class Flags:
    def __init__(
        self,
        model: typing.Optional[str] = None,
        file: typing.Optional[str] = None,
        perfile: typing.Optional[str] = None,
        allfiles: typing.Optional[str] = None,
        file_ext: typing.Optional[str] = None,
        rag: typing.Optional[bool] = False,
        yaml: typing.Optional[str] = None,
        out: typing.Optional[str] = None,
        new: typing.Optional[bool] = None,
        cont: typing.Optional[str] = None,
        terminal: typing.Optional[str] = None,
        default_input: typing.Optional[str] = None,
        response_type: typing.Optional[str] = None,
    ):
        self.model = model
        self.file = file
        self.perfile = perfile
        self.allfiles = allfiles
        self.file_ext = file_ext
        self.rag = rag
        self.yaml = yaml
        self.out = out
        self.new = new
        self.cont = cont
        self.terminal = terminal
        self.default_input = default_input
        self.response_type = response_type

    def __str__(self):
        help_str = ""
        if self.model is not None or self.model != "":
            help_str += f"Model: {self.model}\n"
        if self.file is not None and self.file != "":
            help_str += f"File: {self.file}\n"
        if self.perfile is not None and self.perfile != "":
            help_str += f"Per file: {self.perfile}\n"
        if self.allfiles is not None and self.allfiles != "":
            help_str += f"All files: {self.allfiles}\n"
        if self.default_input is not None and self.default_input != "":
            help_str += f"Default input: {self.default_input}\n"
        if self.file_ext is not None and self.file_ext != "":
            help_str += f"File ext: {self.file_ext}\n"
        if self.rag is not None and self.rag != False:
            help_str += f"RAG: {str(self.rag)}\n"
        if self.yaml is not None and self.yaml != "":
            help_str += f"YAML: {self.yaml}\n"
        if self.response_type is not None and self.response_type != "":
            help_str += f"Response type: {self.response_type}\n"
        if self.out is not None and self.out != "":
            help_str += f"Out: {self.out}\n"
        if self.new is not None and self.new != False:
            help_str += f"New: {str(self.new)}\n"
        if self.cont is not None and self.cont != "":
            help_str += f"Cont: {self.cont}\n"
        if self.terminal is not None and self.terminal != "":
            help_str += f"Terminal: {self.terminal}\n"
        return help_str


def dictionaryToFlags(flags: dict) -> Flags:
    if "model" in flags:
        model = str(flags["model"])
    else:
        model = ""
    if "file" in flags:
        file = str(flags["file"])
    else:
        file = ""
    if "perfile" in flags:
        perfile = str(flags["perfile"])
    else:
        perfile = ""
    if "allfiles" in flags:
        allfiles = str(flags["allfiles"])
    else:
        allfiles = ""
    if "file_ext" in flags:
        file_ext = str(flags["file_ext"])
    else:
        file_ext = ""
    if "rag" in flags:
        rag = bool(flags["rag"])
    else:
        rag = False
    if "yaml" in flags:
        yaml = str(flags["yaml"])
    else:
        yaml = ""
    if "out" in flags:
        out = str(flags["out"])
    else:
        out = ""
    if "new" in flags:
        new = bool(flags["new"])
    else:
        new = None
    if "cont" in flags:
        cont = str(flags["cont"])
    else:
        cont = ""
    if "terminal" in flags:
        terminal = str(flags["terminal"])
    else:
        terminal = ""
    if "default_input" in flags:
        default_input = str(flags["default_input"])
    else:
        default_input = ""
    if "response_type" in flags:
        response_type = str(flags["response_type"])
    else:
        response_type = ""
    flags = Flags(
        model=model,
        file=file,
        perfile=perfile,
        allfiles=allfiles,
        file_ext=file_ext,
        rag=rag,
        yaml=yaml,
        out=out,
        new=new,
        cont=cont,
        terminal=terminal,
        default_input=default_input,
        response_type=response_type,
    )
    return flags


class Step:
    def __init__(
        self,
        prompt: typing.Optional[str],
        name: typing.Optional[str] = None,
        function: typing.Optional[str] = None,
        flags: typing.Optional[Flags] = None,
        description: typing.Optional[str] = None,
    ):
        self.prompt = prompt
        self.name = name
        self.function = function
        self.flags = flags
        self.description = description

    def __str__(self):
        help_str = ""
        if self.name is not None or self.name != "":
            help_str += f"Task: {self.name}\n"
        if self.description is not None or self.description != "":
            help_str += f"Description: {self.description}\n"
        if self.function is not None or self.function != "":
            help_str += f"Function: {self.function}\n"
        if self.prompt is not None or self.prompt != "":
            help_str += f"Prompt: {self.prompt}\n"
        if self.flags is not None:
            help_str += f"Flags:\n{self.flags}\n"
        return help_str


class ReadSteps:
    # Tries to ingest a list of dictionaries with step_list values
    def __init__(self, step_list: list[dict]):
        self.step_list = step_list

    def returnSteps(self) -> list[Step]:
        inputs = []
        for item in self.step_list:
            try:
                # Creates a Flags object from the dictionary
                if "flags" in item:
                    flags = dictionaryToFlags(item["flags"])
                else:
                    flags = None
                # Using .get let's you specify optional keys
                step_item = Step(
                    prompt=item["prompt"],
                    name=item.get("name", None),
                    function=item.get("function", None),
                    flags=flags,
                    description=item.get("description", None),
                )
                inputs.append(step_item)
            except KeyError as error:
                logging.error(f"The task is missing a key {error}")
                # Exits the scripts if there is missing input keys
                return sys.exit(1)
        return inputs

    def __str__(self):
        return self.step_list


# Class to define an task that performs tasks
class TaskConfig:
    def __init__(
        self,
        name: str,
        steps: list[Step],
        # Required as a main model. Any task can overwrite this value with it's
        # own model.
        model: str,
        preamble: typing.Optional[str] = None,
        description: typing.Optional[str] = None,
    ):
        self.name = name
        self.model = model
        self.preamble = preamble
        self.description = description
        self.steps = steps

    def __str__(self):
        help_str = ""
        if self.name is not None:
            help_str += f"Name: {self.name}\n"
        if self.model is not None:
            help_str += f"Model: {self.model}\n"
        if self.description is not None:
            help_str += f"Description: {self.description}\n"
        if self.preamble is not None:
            help_str += f"Preamble: {self.preamble}\n"
        # Extracts the list of Steps
        steps = []
        if self.steps is not None:
            for step in self.steps:
                steps.append(str(step))
            task_str = "\n".join(steps)
            help_str += f"\nSteps:\n\n{task_str}\n"
        return help_str


# This class is used to store the content of a list of
# TaskConfig
class TaskConfigFile:
    def __init__(
        self,
        tasks: list[TaskConfig],
    ):
        self.tasks = tasks

    def __str__(self):
        output = []
        for item in self.tasks:
            output.append(str(item))
        return str(output)

    def return_first(self):
        return self.tasks[0]

    def return_task(self, task: str):
        for item in self.tasks:
            if item.name == task:
                return TaskConfigFile(tasks=[item])


# Class used to read a specific task configuration file or defaults
# to a yaml file in the tasks directory of the project
# printing the object returns the path as a string
# returnTasks() with an optional task flag will return
# all task configurations or the specified one
class ReadTaskConfig:
    # Tries to ingest a task configuration file and validate its keys.
    def __init__(
        self,
        yaml_path: str = os.path.join(
            get_project_path(), "tasks/release-notes-task.yaml"
        ),
    ):
        self.yaml_path = yaml_path
        try:
            with open(self.yaml_path, "r", encoding="utf-8") as inp_yaml:
                self.config_values = yaml.safe_load(inp_yaml)
        except FileNotFoundError:
            logging.error(f"The task file {self.yaml_path} does not exist.")
            return sys.exit(1)

    def __str__(self):
        return self.yaml_path

    def returnTasks(self, task: typing.Optional[str] = None) -> TaskConfigFile:
        tasks = []
        try:
            for item in self.config_values["tasks"]:
                name = ""
                try:
                    name = item["name"]
                except KeyError as error:
                    logging.error(f"Your task configuration is missing a {error}")
                    return sys.exit()
                try:
                    name = item["model"]
                except KeyError as error:
                    logging.error(f"Your task configuration is missing a {error}")
                    return sys.exit()
                try:
                    task_config = TaskConfig(
                        name=item["name"],
                        steps=item["steps"],
                        model=item["model"],
                        description=item.get("description", None),
                        preamble=item.get("preamble", None),
                    )
                    new_steps = ReadSteps(step_list=item["steps"]).returnSteps()
                    task_config.steps = new_steps
                    tasks.append(task_config)
                except KeyError as error:
                    if name != "":
                        logging.error(
                            f"A product configuration, {name} is missing a key {error}"
                        )
                        return sys.exit(1)
            if task is not None:
                match = False
                for item in tasks:
                    # If task is found, update tasks to a single entry in products
                    if item.name == task:
                        match = True
                        tasks = [item]
                        break
                # Exits if product is not found
                if not match:
                    logging.error(f"The task {task} does not exist in {self.yaml_path}")
                    return sys.exit(1)
            tasks_file = TaskConfigFile(tasks=tasks)
            return tasks_file
        except KeyError as error:
            logging.error(
                f"Your task configuration file is missing a configuration key {error} in {self.yaml_path}"
            )
            return sys.exit(1)


# Function to make using common_options simpler
def return_tasks_config(
    tasks_file: typing.Optional[str],
    task: typing.Optional[tuple[str]],
):
    loaded_tasks = ReadTaskConfig(yaml_path=tasks_file)
    final_tasks = []
    if task == () or task == [""]:
        task_config = loaded_tasks.returnTasks()
        final_tasks = task_config.tasks
    else:
        for item in task:
            task_config = loaded_tasks.returnTasks(task=item)
            final_tasks.append(task_config.tasks[0])
    task_config = TaskConfigFile(tasks=final_tasks)
    return task_config


# # Function to return a list of tasks from a given task configuration file
# def return_list_of_tasks(task_config: ReadTaskConfig) -> list[TaskConfig]:
#     tasks = task_config.returnTasks()
#     final_tasks = []
#     for item in tasks:
#         final_tasks.append(item)
#     return final_tasks


# Function to convert all yaml files inside a path into a single yaml
def combine_yaml_files(
    path: typing.Optional[str] = None,
):
    final_tasks = []
    for root, dirs, files in os.walk(resolve_path(path)):
        for file in files:
            if file.endswith(".yaml"):
                full_file_path = os.path.join(resolve_path(path), file)
                task_config = ReadTaskConfig(yaml_path=full_file_path).returnTasks()
                if len(task_config.tasks) == 1:
                    final_tasks.append(task_config.tasks[0])
                else:
                    for item in task_config.tasks:
                        final_tasks.append(item)
    merged_config = TaskConfigFile(tasks=final_tasks)
    # for item in merged_config.tasks:
    #     print(item)
    return merged_config
