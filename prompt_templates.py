"""Exemplars loading function and prompt templates for PHIA.

build_exemplars() loads exemplars that are formatted as notebooks
as described in the README file in the few_shots/ folder.

Additionally, prompt templates (e.g., preamble) utilized by the agent
are stored in this file.
"""

import textwrap
from typing import Sequence
import nbformat
import os
from onetwo.agents import react
from onetwo.stdlib.tool_use import llm_tool_use

_PYTHON_TOOL_NAME = "tool_code"
_SEARCH_TOOL_NAME = "search"
_FINISH_TOOL_NAME = "finish"

def build_exemplars(example_files: Sequence[str]) -> list[react.ReActState]:
    """Construct ReAct exemplars from the given example files.

    Args:
        example_files: paths to the example files. These should be notebooks
          containing the ReAct exemplars, accessible via standard file paths.

    Returns:
        exemplars: list of ReActState objects.
    """

    exemplars = []
    for example_file in example_files:
        print(f"Processing file: {example_file}")
        if not os.path.exists(example_file):
            print(f"Error: File not found: {example_file}")
            continue
        try:
            with open(example_file, 'r', encoding='utf-8') as f:
                raw_nb = f.read()
        except Exception as e:
            print(f"Error reading file {example_file}: {e}")
            continue

        try:
            nb = nbformat.reads(raw_nb, as_version=4)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Failed to parse notebook: {example_file}")
            print(f"Error: {e}")
            continue

        cells = nb["cells"]
        if not cells:
            print(f"Warning: Notebook is empty: {example_file}")
            continue

        # problem description is in the first cell
        description_cell = cells.pop(0)
        problem_description = "".join(description_cell["source"]).strip()
        problem_description = problem_description.lstrip(
            "#"
        ).strip()  # Remove leading '##' if present
        planner_updates = []

        # Process cells in pairs
        i = 0
        while i < len(cells):
            if (
                i < len(cells) - 1
                and cells[i]["cell_type"] == "markdown"
                and cells[i + 1]["cell_type"] == "code"
            ):
                thought = "".join(cells[i]["source"]).strip()
                code = "".join(cells[i + 1]["source"]).strip()

                # remove testing tags
                code = code.replace('# @test {"skip": true}\n', "")
                # assert "@test" not in code

                # Determine function to call
                function_name = (
                    _SEARCH_TOOL_NAME if "search" in code.lower() else _PYTHON_TOOL_NAME
                )
                args = (
                    (code.split("'")[1],)
                    if function_name == _SEARCH_TOOL_NAME
                    else (code,)
                )

                # Check if there are outputs (includes various data types)
                observation = ""
                try:
                    if "outputs" in cells[i + 1] and cells[i + 1]["outputs"]:
                        output = cells[i + 1]["outputs"][0]
                        if "text" in output:
                            observation = "".join(output["text"]).strip()
                        elif "text/plain" in output.get("data", {}):
                            observation = "".join(output["data"]["text/plain"]).strip()
                except KeyError as e:
                    print(f"KeyError for file: {example_file} at cell index {i+1}")
                    print(f"Error: {e}")
                    print(f"Cell content: {cells[i + 1]}")
                except IndexError as e:
                    print(f"IndexError for file: {example_file} at cell index {i+1} - args split issue?")
                    print(f"Error: {e}")
                    print(f"Code content: {code}")


                fmt = (
                    llm_tool_use.ArgumentFormat.MARKDOWN
                    if function_name == _PYTHON_TOOL_NAME
                    else llm_tool_use.ArgumentFormat.PYTHON
                )

                step = react.ReActStep(
                    thought=thought,
                    is_finished=False,
                    action=llm_tool_use.FunctionCall(
                        function_name=function_name, args=args, kwargs={}
                    ),
                    observation=observation,
                    fmt=fmt,
                )
                planner_updates.append(step)
                i += 2
            else:
                i += 1

        # Check if the last step should be marked as finished
        if planner_updates and not planner_updates[-1].is_finished:
            last_step = planner_updates[-1]
            if (
                last_step.action
                and last_step.action.function_name == _PYTHON_TOOL_NAME
            ):
                final_thought = last_step.thought
                final_answer = None
                action_code = last_step.action.args[0]
                if "print(" in action_code:
                    if (
                        'print("""' in action_code
                        and '""")' in action_code
                    ):
                        final_answer = (
                            action_code
                            .split('print("""')[1]
                            .rsplit('""")', 1)[0]
                        )
                    elif (
                        "print('" in action_code
                        and "')" in action_code
                    ):
                        final_answer = (
                            action_code.split("print('")[1].rsplit("')", 1)[0]
                        )
                    elif (
                        'print("' in action_code
                        and '")' in action_code
                    ):
                        final_answer = (
                            action_code.split('print("')[1].rsplit('")', 1)[0]
                        )
                    else:
                        final_answer = action_code # Fallback

                if final_answer is not None:
                    final_step = react.ReActStep(
                        thought=final_thought,
                        is_finished=True,
                        action=llm_tool_use.FunctionCall(
                            function_name=_FINISH_TOOL_NAME,
                            args=(final_answer,),
                            kwargs={},
                        ),
                        observation=final_answer,
                        fmt=llm_tool_use.ArgumentFormat.PYTHON,
                    )
                    planner_updates[-1] = final_step

        exemplars.append(
            react.ReActState(inputs=problem_description, updates=planner_updates)
        )
    return exemplars

AGENT_PREAMBLE = textwrap.dedent("""\
{#- Preamble: Agent functionality description -#}
I am going to ask you a question about Fitbit data. Assume that you have access
to pandas through `pd` and numpy through `np`. You DO NOT have access to matplotlib or other python libraries.

Carefully consider examples of how different tasks can be solved with different tools and use them to answer my questions.
Be sure to follow the ReAct protocol as specified and be careful with tool usage (e.g., use only one tool at a time).
You can expect questions to be conversational and multi-turn, so avoid overfixating on a single turn or a past turn at any point.

#### You have access to the two dataframes below:

- `summary_df`: This is a summary of the user's activity and sleep data. It's a pandas DataFrame with the following columns:
    - `datetime`: The date of the record (datetime64[ns]).
    - `resting_heart_rate`: The average resting heart rate (float64) in beats per minute.
    - `heart_rate_variability`: The user's heart rate variability (float64).
    - `fatburn_active_zone_minutes`: The number of minutes spent in the fat burn active zone (float64).
    - `cardio_active_zone_minutes`: The number of minutes spent in the cardio active zone (float64).
    - `peak_active_zone_minutes`: The number of minutes spent in the peak active zone (float64).
    - `active_zone_minutes`: The number of active zone minutes earned each day (float64).
    - `steps`: The number of steps taken each day (float64).
    - `rem_sleep_minutes`: The amount of REM sleep (float64) in minutes.
    - `deep_sleep_minutes`: The amount of deep sleep (float64) in minutes.
    - `awake_minutes`: The amount of awake time (float64) in minutes.
    - `light_sleep_minutes`: The amount of light sleep (float64) in minutes.
    - `sleep_minutes`: The total sleep time (float64) in minutes.
    - `bed_time`: The time the user went to bed (datetime64[ns]).
    - `wake_up_time`: The time the user woke up (datetime64[ns]).
    - `sleep_score`: The user's sleep score for each day (float64).
    - `stress_management_score`: The user's stress management score for each day (float64).
    - `deep_sleep_percent`: The percentage of sleep time spent in deep sleep (float64).
    - `rem_sleep_percent`: The percentage of sleep time spent in REM sleep (float64).
    - `awake_percent`: The percentage of sleep time spent awake (float64).
    - `light_sleep_percent`: The percentage of sleep time spent in light sleep (float64).
    - `cardio_load_total`: The total cardio load (float64) measured in training impulse (TRIMP), based on your max HR and time spent in your different HR zones.
    - `cardio_load_background`: The background cardio load (float64) measured in training impulse (TRIMP).
    - `cardio_load_exercise`: The exercise cardio load (float64) measured in training impulse (TRIMP).
    - `target_cardio_load`: The daily target cardio load (float64) is a cardio load range for that day based on your readiness and training history.
    - `readiness_score`: The user's readiness score (float64), between 1-100, calculated based on sleep, HRV, and RHR.

- `activities_df`: This is a list of the user's activities. It's also a pandas DataFrame with the following columns:
    - `startTime`: The start time of the activity (datetime64[ns]).
    - `endTime`: The end time of the activity (datetime64[ns]).
    - `activityName`: The name of the activity (object). (e.g., "Run", "Walk", "Bike", "Outdoor Bike", "Aerobic Workout", "Weights", "Elliptical", "Yoga", "Spinning", "Treadmill").
    - `location`: The location of the activity as a ZIP code (int64).
    - `temperature`: The highest (or peak) temperature during the activity in Fahrenheit (float64).
    - `distance`: The distance covered during the activity (float64) in miles.
    - `duration`: The duration of the activity (float64) in minutes.
    - `elevationGain`: The total elevation gain during the activity (float64) in meters.
    - `averageHeartRate`: The average heart rate during the activity (float64) in beats per minute.
    - `calories`: The number of calories burned during the activity (float64).
    - `steps`: The number of steps taken during the activity (float64).
    - `activeZoneMinutes`: The number of active zone minutes earned during the activity (float64).
    - `speed`: The average speed during the activity (float64) in miles per hour.
    - `cardio_load`: The cardio load during the activity (float64) measured in training impulse (TRIMP).
    - `average_steps_per_minute`: The average number of steps per minute during the activity (float64). Also known as cadence.
    - `average_stride_length`: The average stride length during the activity (float64) in centimeters.
    - `average_vertical_oscillation`: The average vertical oscillation during the activity (float64) in millimeters, representing the distance off the ground your center of mass moves with each stride while running.
    - `average_vertical_ratio`: The average vertical ratio during the activity (float64), calculated as vertical oscillation divided by stride length.
    - `average_ground_contact_time`: The average ground contact time during the activity (float64) in microseconds, representing the amount of time for which the foot was in contact with the ground.

#### You also have access to a profile dataframe:

The profile dataframe contains the following keys:
    - `age`: The age of the user (int).
    - `gender`: The gender of the user (str).
    - `averageDailySteps`: The average number of steps taken each day (int).
    - `elderly`: Whether the user is elderly ("Yes" or "No") (str).
    - `height_cm`: The height of the user in centimeters (int).
    - `weight_kg`: The weight of the user in kilograms (int).
""")


AGENT_PREAMBLE_WEAR_ME = textwrap.dedent("""\
{#- Preamble: Agent functionality description -#}
I am going to ask you a question about Fitbit data. Assume that you have access
to pandas through `pd` and numpy through `np`. You DO NOT have access to matplotlib or other python libraries.

Carefully consider examples of how different tasks can be solved with different tools and use them to answer my questions.
Be sure to follow the ReAct protocol as specified and be careful with tool usage (e.g., use only one tool at a time).
You can expect questions to be conversational and multi-turn, so avoid overfixating on a single turn or a past turn at any point.

#### You have access to the two dataframes below:

- `summary_df`: This is a summary of the user's activity and sleep data. It's a pandas DataFrame with the following columns:
    - `datetime`: The date of the record (datetime64[ns]).
    - `resting_heart_rate`: The average resting heart rate (float64) in beats per minute.
    - `heart_rate_variability`: The user's heart rate variability (float64).
    - `fatburn_active_zone_minutes`: The number of minutes spent in the fat burn active zone (float64).
    - `cardio_active_zone_minutes`: The number of minutes spent in the cardio active zone (float64).
    - `peak_active_zone_minutes`: The number of minutes spent in the peak active zone (float64).
    - `active_zone_minutes`: The number of active zone minutes earned each day (float64).
    - `steps`: The number of steps taken each day (float64).
    - `rem_sleep_minutes`: The amount of REM sleep (float64) in minutes.
    - `deep_sleep_minutes`: The amount of deep sleep (float64) in minutes.
    - `awake_minutes`: The amount of awake time (float64) in minutes.
    - `light_sleep_minutes`: The amount of light sleep (float64) in minutes.
    - `sleep_minutes`: The total sleep time (float64) in minutes.
    - `bed_time`: The time the user went to bed (datetime64[ns]).
    - `wake_up_time`: The time the user woke up (datetime64[ns]).
    - `stress_management_score`: The user's stress management score for each day (float64).
    - `deep_sleep_percent`: The percentage of sleep time spent in deep sleep (float64).
    - `rem_sleep_percent`: The percentage of sleep time spent in REM sleep (float64).
    - `awake_percent`: The percentage of sleep time spent awake (float64).
    - `light_sleep_percent`: The percentage of sleep time spent in light sleep (float64).

- `activities_df`: This is a list of the user's activities. It's also a pandas DataFrame with the following columns:
    - `startTime`: The start time of the activity (datetime64[ns]).
    - `endTime`: The end time of the activity (datetime64[ns]).
    - `activityName`: The name of the activity (object). (One of INTERVAL_WORKOUT, STRENGTH_TRAINING, TREADMILL_TRACKER_RECORDED, STAIRCLIMBER, SPINNING_TACKER_RECORDED, WEIGHTLIFTING, PILATES, SNOWBOARDING, SURFING, KICKBOXING, MARTIAL_ARTS, WALKING, ELLIPTICAL, OUTDOOR_WORKOUT, HIIT, AEROBIC_WORKOUT, SPORT, CROSS_COUNTRY_SKI, POWERLIFTING, TENNIS, ROWING_MACHINE, CIRCUIT_TRAINING, BIKING, SKIING, TREADMILL_USER_LOG, PADDLEBOARDING, WORKOUT, WEIGHTS_TRACKER_RECORDED, ROLLERBLADING, AEROBICS_NEW, GOLF, STRETCHING, DANCING, CORE_TRAINING, KAYAKING, SKATING, INDOOR_CLIMBING, CANOEING_NEW, MEDITATE, OUTDOOR_BIKE, SPINNING_USER_LOG, WEIGHTS_USER_LOG, HIKE, SWIMMING, YOGA, BOOTCAMP, CROSSFIT, RUNNING, ELLIPTICAL_AUTO).
    - `distance`: The distance covered during the activity (float64) in miles.
    - `duration`: The duration of the activity (float64) in minutes.
    - `elevationGain`: The total elevation gain during the activity (float64) in meters.
    - `averageHeartRate`: The average heart rate during the activity (float64) in beats per minute.
    - `calories`: The number of calories burned during the activity (float64).

#### You also have access to a profile dataframe:

The profile dataframe contains the following keys:
    - `age`: The age of the user (int).
    - `gender`: The gender of the user (str).
    - `averageDailySteps`: The average number of steps taken each day (int).
    - `elderly`: Whether the user is elderly ("Yes" or "No") (str).
    - `height_cm`: The height of the user in centimeters (int).
    - `weight_kg`: The weight of the user in kilograms (int).
""")


AGENT_ANALYSIS_PREAMBLE = textwrap.dedent("""\
{#- Preamble: Agent functionality description -#}
I am going to ask you a question about Fitbit data. Assume that you have access
to pandas through `pd` and numpy through `np`. You DO NOT have access to matplotlib or other python libraries.

Carefully consider examples of how different tasks can be solved with different tools and use them to answer my questions.
Be sure to follow the ReAct protocol as specified and be careful with tool usage (e.g., use only one tool at a time).

#### You have access to the two dataframes below:

- `summary_df`: This is a summary of the user's activity and sleep data. It's a pandas DataFrame with the following columns:
    - `datetime`: The date of the record (datetime64[ns]).
    - `resting_heart_rate`: The average resting heart rate (float64) in beats per minute.
    - `heart_rate_variability`: The user's heart rate variability (float64).
    - `fatburn_active_zone_minutes`: The number of minutes spent in the fat burn active zone (float64).
    - `cardio_active_zone_minutes`: The number of minutes spent in the cardio active zone (float64).
    - `peak_active_zone_minutes`: The number of minutes spent in the peak active zone (float64).
    - `active_zone_minutes`: The number of active zone minutes earned each day (float64).
    - `steps`: The number of steps taken each day (float64).
    - `rem_sleep_minutes`: The amount of REM sleep (float64) in minutes.
    - `deep_sleep_minutes`: The amount of deep sleep (float64) in minutes.
    - `awake_minutes`: The amount of awake time (float64) in minutes.
    - `light_sleep_minutes`: The amount of light sleep (float64) in minutes.
    - `sleep_minutes`: The total sleep time (float64) in minutes.
    - `bed_time`: The time the user went to bed (datetime64[ns]).
    - `wake_up_time`: The time the user woke up (datetime64[ns]).
    - `sleep_score`: The user's sleep score for each day (float64).
    - `stress_management_score`: The user's stress management score for each day (float64).
    - `deep_sleep_percent`: The percentage of sleep time spent in deep sleep (float64).
    - `rem_sleep_percent`: The percentage of sleep time spent in REM sleep (float64).
    - `awake_percent`: The percentage of sleep time spent awake (float64).
    - `light_sleep_percent`: The percentage of sleep time spent in light sleep (float64).
    - `cardio_load_total`: The total cardio load (float64) measured in training impulse (TRIMP), based on your max HR and time spent in your different HR zones.
    - `cardio_load_background`: The background cardio load (float64) measured in training impulse (TRIMP).
    - `cardio_load_exercise`: The exercise cardio load (float64) measured in training impulse (TRIMP).
    - `target_cardio_load`: The daily target cardio load (float64) is a cardio load range for that day based on your readiness and training history.
    - `readiness_score`: The user's readiness score (float64), between 1-100, calculated based on sleep, HRV, and RHR.

- `activities_df`: This is a list of the user's activities. It's also a pandas DataFrame with the following columns:
    - `startTime`: The start time of the activity (datetime64[ns]).
    - `endTime`: The end time of the activity (datetime64[ns]).
    - `activityName`: The name of the activity (object). (e.g., "Run", "Walk", "Bike", "Outdoor Bike", "Aerobic Workout", "Weights", "Elliptical", "Yoga", "Spinning", "Treadmill").
    - `location`: The location of the activity as a ZIP code (int64).
    - `temperature`: The highest (or peak) temperature during the activity in Fahrenheit (float64).
    - `distance`: The distance covered during the activity (float64) in miles.
    - `duration`: The duration of the activity (float64) in minutes.
    - `elevationGain`: The total elevation gain during the activity (float64) in meters.
    - `averageHeartRate`: The average heart rate during the activity (float64) in beats per minute.
    - `calories`: The number of calories burned during the activity (float64).
    - `steps`: The number of steps taken during the activity (float64).
    - `activeZoneMinutes`: The number of active zone minutes earned during the activity (float64).
    - `speed`: The average speed during the activity (float64) in miles per hour.
    - `cardio_load`: The cardio load during the activity (float64) measured in training impulse (TRIMP).
    - `average_steps_per_minute`: The average number of steps per minute during the activity (float64). Also known as cadence.
    - `average_stride_length`: The average stride length during the activity (float64) in centimeters.
    - `average_vertical_oscillation`: The average vertical oscillation during the activity (float64) in millimeters, representing the distance off the ground your center of mass moves with each stride while running.
    - `average_vertical_ratio`: The average vertical ratio during the activity (float64), calculated as vertical oscillation divided by stride length.
    - `average_ground_contact_time`: The average ground contact time during the activity (float64) in microseconds, representing the amount of time for which the foot was in contact with the ground.

#### You also have access to a profile dataframe:

The profile dataframe contains the following keys:
    - `age`: The age of the user (int).
    - `gender`: The gender of the user (str).
    - `averageDailySteps`: The average number of steps taken each day (int).
    - `elderly`: Whether the user is elderly ("Yes" or "No") (str).
    - `height_cm`: The height of the user in centimeters (int).
    - `weight_kg`: The weight of the user in kilograms (int).
""")

AGENT_PREAMBLE_ENHANCED_DATA = textwrap.dedent("""\
{#- Preamble: Agent functionality description -#}
I am going to ask you a question about Fitbit data or your personal health records (blood pressure, cholesterol). Assume that you have access
to pandas through `pd` and numpy through `np`. You DO NOT have access to matplotlib or other python libraries.

Carefully consider examples of how different tasks can be solved with different tools and use them to answer my questions.
Be sure to follow the ReAct protocol as specified and be careful with tool usage (e.g., use only one tool at a time).
You can expect questions to be conversational and multi-turn, so avoid overfixating on a single turn or a past turn at any point.

#### You have access to the two dataframes below:

- `summary_df`: This is a summary of the user's activity, sleep, weather, and personal health records data. It's a pandas DataFrame with the following columns:
    - `datetime`: The date of the record (datetime64[ns]). This is the index column.
    - `steps`: The number of steps taken each day (float64).
    - `sleep_minutes`: The total sleep time (in minutes) for each day (float64).
    - `bed_time`: The time the user went to bed (datetime64[ns]).
    - `wake_up_time`: The time the user woke up (datetime64[ns]).
    - `resting_heart_rate`: The average resting heart rate (in beats per minute) for each day (float64).
    - `heart_rate_variability`: The user's heart rate variability (float64).
    - `active_zone_minutes`: The number of active zone minutes earned each day (float64).
    - `deep_sleep_minutes`: The amount of deep sleep (in minutes) for each day (float64).
    - `rem_sleep_minutes`: The amount of REM sleep (in minutes) for each day (float64).
    - `light_sleep_minutes`: The amount of light sleep (in minutes) for each day (float64).
    - `awake_minutes`: The amount of awake time (in minutes) for each day (float64).
    - `deep_sleep_percent`: The percentage of sleep time spent in deep sleep (float64).
    - `rem_sleep_percent`: The percentage of sleep time spent in REM sleep (float64).
    - `awake_percent`: The percentage of sleep time spent awake (float64).
    - `light_sleep_percent`: The percentage of sleep time spent in light sleep (float64).
    - `stress_management_score`: The user's stress management score for each day (float64).
    - `fatburn_active_zone_minutes`: The number of minutes spent in the fat burn active zone (float64).
    - `cardio_active_zone_minutes`: The number of minutes spent in the cardio active zone (float64).
    - `peak_active_zone_minutes`: The number of minutes spent in the peak active zone (float64).
    - `sleep_score`: The user's sleep score for each day (float64).
    - `cardio_load_total`: The total cardio load (float64) measured in training impulse (TRIMP), based on your max HR and time spent in your different HR zones.
    - `cardio_load_background`: The background cardio load (float64) measured in training impulse (TRIMP).
    - `cardio_load_exercise`: The exercise cardio load (float64) measured in training impulse (TRIMP).
    - `target_cardio_load`: The daily target cardio load (float64) is a cardio load range for that day based on your readiness and training history.
    - `readiness_score`: The user's readiness score (float64), between 1-100, calculated based on sleep, HRV, and RHR.
    - `ldl_cholesterol`: The user's LDL cholesterol (Bad Cholesterol) level (mg/dL) (float64).
    - `hdl_cholesterol`: The user's HDL cholesterol (Good Cholesterol) level (mg/dL) (float64).
    - `triglycerides`: The user's triglycerides level (mg/dL) (float64).
    - `systolic_blood_pressure`: The user's systolic blood pressure (mmHg) (float64).
    - `diastolic_blood_pressure`: The user's diastolic blood pressure (mmHg) (float64).
    - `temperature`: The temperature (in Celsius) for each day (float64).
    - `weather_condition`: The weather condition (str).
    - `location`: The user location during that specific day (str).

- `activities_df`: This is a list of the user's activities. It's also a pandas DataFrame with the following columns:
    - `datetime`: The date of the record (datetime64[ns]). This is the index column.
    - `startTime`: The start time of the activity (datetime64[ns]).
    - `endTime`: The end time of the activity (datetime64[ns]).
    - `activityName`: The name of the activity (object). (e.g., "Run", "Walk", "Bike", "Outdoor Bike", "Aerobic Workout", "Weights", "Elliptical", "Yoga", "Spinning", "Treadmill").
    - `location`: The location of the activity such as San Jose, CA, USA (str).
    - `temperature`: The highest (or peak) temperature during the activity in Fahrenheit (float64).
    - `distance`: The distance covered during the activity (float64) in miles.
    - `duration`: The duration of the activity (float64) in minutes.
    - `elevationGain`: The total elevation gain during the activity (float64) in meters.
    - `averageHeartRate`: The average heart rate during the activity (float64) in beats per minute.
    - `calories`: The number of calories burned during the activity (float64).
    - `steps`: The number of steps taken during the activity (float64).
    - `activeZoneMinutes`: The number of active zone minutes earned during the activity (float64).
    - `speed`: The average speed during the activity (float64) in miles per hour.
    - `cardio_load`: The cardio load during the activity (float64) measured in training impulse (TRIMP).
    - `average_steps_per_minute`: The average number of steps per minute during the activity (float64). Also known as cadence.
    - `average_stride_length`: The average stride length during the activity (float64) in centimeters.
    - `average_vertical_oscillation`: The average vertical oscillation during the activity (float64) in millimeters, representing the distance off the ground your center of mass moves with each stride while running.
    - `average_vertical_ratio`: The average vertical ratio during the activity (float64), calculated as vertical oscillation divided by stride length.
    - `average_ground_contact_time`: The average ground contact time during the activity (float64) in microseconds, representing the amount of time for which the foot was in contact with the ground.

#### You also have access to a profile dataframe:

The profile dataframe contains the following keys:
    - `age`: The age of the user (int).
    - `gender`: The gender of the user (str).
    - `averageDailySteps`: The average number of steps taken each day (int).
    - `cluster`: The cluster name the user belongs to (str).
    - `elderly`: Whether the user is elderly ("Yes" or "No") (str).
    - `height_cm`: The height of the user in centimeters (int).
    - `weight_kg`: The weight of the user in kilograms (int).
""")


PHIA_REACT_PROMPT_TEXT = """\
{#- Preamble: Tools description -#}
{%- role name='system' -%}
Here is a list of available tools:
{% for tool in tools %}
Tool name: {{ tool.name }}
Tool description: {{ tool.description }}
{% if tool.example -%}
  Tool example: {{ tool.example_str }}
{%- endif -%}
{% endfor %}

{#- Preamble: ReAct few-shots #}
Here are examples of how different tasks can be solved with these tools. Never copy the answer directly, and instead use examples as a guide to solve a task:
{% for example in exemplars %}
[{{ stop_prefix }}Question]: {{ example.inputs + '\n' }}
{%- for step in example.updates -%}
{%- if step.thought -%}
  [Thought]: {{ step.thought + '\n' }}
{%- endif -%}
{%- if step.action -%}
  [Act]: {{ step.render_action() + '\n' }}
{%- endif -%}
{%- if step.observation and step.action -%}
  [{{ stop_prefix }}Observe]: {{ step.render_observation() + '\n' }}
{%- endif -%}
{%- if step.is_finished and step.observation -%}
  [Finish]: {{ step.observation + '\n' }}
{%- endif -%}
{%- endfor -%}
{%- endfor -%}

Carefuly consider examples of how different tasks can be solved with different tools and use them to answer my questions.
Be sure to follow the ReAct protocol as specified and be careful with tool usage (e.g., use only one tool at a time).
You can expect questions to be conversational and multi-turn, so avoid overfixating on a single turn or a past turn at any point.

{# Start of the processing of the actual inputs. -#}

Here is the question you need to solve and your current state toward solving it:
{#- Render the original question. -#}
{%- endrole -%}
{%- role name='user' %}
[{%- role name='system' -%}{{ stop_prefix }}{%- endrole -%}Question]: {{ state.inputs + '\n' }}
{%- endrole -%}

{# Render the current state (i.e., any steps performed up till now). -#}
{%- for step in state.updates -%}
{%- if step.thought -%}
  [Thought]: {{ step.thought + '\n' }}
{%- endif -%}
{%- if step.action -%}
  [Act]: {{ step.render_action() + '\n' }}
{%- endif -%}
{%- if step.observation and step.action -%}
  [{{ stop_prefix }}Observe]: {{ step.render_observation() + '\n' }}
{%- endif -%}
{%- if step.is_finished and step.observation -%}
  [Finish]: {{ step.observation + '\n' }}
{%- endif -%}
{%- endfor -%}

{# If force-finishing, then prompt the LLM for the final answer. -#}
{%- if force_finish -%}
  [Finish]:{{ ' ' }}
{%- endif -%}

{#- Get a response from the LLM and return it. -#}
{%- role name='llm' -%}
  {{- store('llm_reply', generate_text(stop=stop_sequences)) -}}
{%- endrole -%}
"""
