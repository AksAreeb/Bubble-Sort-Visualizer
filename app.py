import gradio as gr

# Main Logic for Buuble Sort

def parse_input_list(text: str):
    """
    Parse a comma or space separated string of numbers into a list of ints.
    """
    if not text.strip():
        raise ValueError("Please enter at least one number.")
    # Allow comma or space separated
    separators = [",", " "]
    for sep in separators:
        text = text.replace(sep, " ")
    parts = [p for p in text.split(" ") if p.strip() != ""]
    numbers = []
    for p in parts:
        try:
            numbers.append(int(p))
        except ValueError:
            raise ValueError(f"'{p}' is not a valid integer.")
    return numbers


def init_state(input_text: str):
    """
    Initialize the bubble sort state from user input.
    """
    try:
        arr = parse_input_list(input_text)
    except ValueError as e:
        return (
            None,  # state
            "Error: " + str(e),
            "",
            "",
        )

    n = len(arr)
    if n == 1:
        # Already sorted
        state = {
            "array": arr,
            "n": n,
            "i": 0,
            "j": 0,
            "step": 0,
            "comparisons": 0,
            "swaps": 0,
            "swapped_this_pass": False,
            "finished": True,
            "log": ["List has only one element. Already sorted."],
        }
        current_view = f"Current list: {arr}\n(Status: Sorted)"
        stats = (
            f"Steps: {state['step']} | Comparisons: {state['comparisons']} "
            f"| Swaps: {state['swaps']}"
        )
        log_text = "\n".join(state["log"])
        return state, current_view, stats, log_text

    state = {
        "array": arr,
        "n": n,
        "i": 0,  # current pass
        "j": 0,  # current index within pass
        "step": 0,
        "comparisons": 0,
        "swaps": 0,
        "swapped_this_pass": False,
        "finished": False,
        "log": [f"Initial list: {arr}"],
    }

    current_view = (
        f"Current list: {arr}\n"
        f"Pass: {state['i'] + 1} | Comparing indices {state['j']} and {state['j'] + 1}"
    )
    stats = (
        f"Steps: {state['step']} | Comparisons: {state['comparisons']} "
        f"| Swaps: {state['swaps']}"
    )
    log_text = "\n".join(state["log"])
    return state, current_view, stats, log_text


def bubble_step(state):
    """
    Perform a single bubble sort comparison (and possible swap).
    """
    if state is None:
        return (
            None,
            "Error: Please press 'Start / Reset' first.",
            "",
            "",
        )

    if state["finished"]:
        arr = state["array"]
        current_view = f"Current list: {arr}\n(Status: Sorted)"
        stats = (
            f"Steps: {state['step']} | Comparisons: {state['comparisons']} "
            f"| Swaps: {state['swaps']}"
        )
        log_text = "\n".join(state["log"])
        return state, current_view, stats, log_text

    arr = state["array"]
    n = state["n"]
    i = state["i"]
    j = state["j"]

    # Safety check
    if i >= n - 1:
        state["finished"] = True
        arr = state["array"]
        state["log"].append(f"All passes complete. Final sorted list: {arr}")
        current_view = f"Current list: {arr}\n(Status: Sorted)"
        stats = (
            f"Steps: {state['step']} | Comparisons: {state['comparisons']} "
            f"| Swaps: {state['swaps']}"
        )
        log_text = "\n".join(state["log"])
        return state, current_view, stats, log_text

    a = arr[j]
    b = arr[j + 1]
    state["step"] += 1
    state["comparisons"] += 1

    # Compare and possibly swap
    if a > b:
        arr[j], arr[j + 1] = arr[j + 1], arr[j]
        state["swaps"] += 1
        state["swapped_this_pass"] = True
        action = (
            f"Step {state['step']}: Compared {a} and {b} → swapped. "
            f"New list: {arr}"
        )
    else:
        action = (
            f"Step {state['step']}: Compared {a} and {b} → no swap. "
            f"List stays: {arr}"
        )

    state["log"].append(action)

    # Move j forward
    j += 1

    # End of pass?
    if j >= n - 1 - i:
        # We finished a pass
        pass_number = i + 1
        if not state["swapped_this_pass"]:
            # Optimization: no swaps → list is sorted
            state["finished"] = True
            state["log"].append(
                f"No swaps in pass {pass_number}. List is sorted early: {arr}"
            )
        else:
            # Next pass
            state["log"].append(
                f"End of pass {pass_number}. Largest element has bubbled to position {n - 1 - i}."
            )
            i += 1
            j = 0
            state["swapped_this_pass"] = False

        state["i"] = i
        state["j"] = j

        if i >= n - 1:
            state["finished"] = True
            state["log"].append(f"All passes complete. Final sorted list: {arr}")
    else:
        # Continue in current pass
        state["j"] = j

    # Prepare outputs
    if state["finished"]:
        status_line = "(Status: Sorted)"
    else:
        status_line = (
            f"(Status: In progress — Pass {state['i'] + 1}, "
            f"next comparison: indices {state['j']} and {state['j'] + 1})"
        )

    current_view = f"Current list: {arr}\n{status_line}"
    stats = (
        f"Steps: {state['step']} | Comparisons: {state['comparisons']} "
        f"| Swaps: {state['swaps']}"
    )
    log_text = "\n".join(state["log"])

    return state, current_view, stats, log_text


def bubble_run_to_end(state):
    """
    Run bubble sort steps until the list is fully sorted.
    """
    if state is None:
        return (
            None,
            "Error: Please press 'Start / Reset' first.",
            "",
            "",
        )

    # Keep stepping until finished
    safety_counter = 0
    max_steps = 10000  # just in case of unexpected loop
    while not state["finished"] and safety_counter < max_steps:
        state, _, _, _ = bubble_step(state)
        safety_counter += 1

    arr = state["array"]
    current_view = f"Current list: {arr}\n(Status: Sorted)"
    stats = (
        f"Steps: {state['step']} | Comparisons: {state['comparisons']} "
        f"| Swaps: {state['swaps']}"
    )
    log_text = "\n".join(state["log"])
    return state, current_view, stats, log_text


# -----------------------------
# Gradio UI
# -----------------------------

def build_interface():
    with gr.Blocks(title="Bubble Sort Step-by-Step Visualizer") as demo:
        gr.Markdown(
            """
# Bubble Sort Step-by-Step Visualizer
Enter a list of numbers and use **Next Step** to watch Bubble Sort in action.

- **Start / Reset**: initialize or reset with a new list  
- **Next Step**: perform one comparison (and possible swap)  
- **Run to End**: sort the entire list automatically  

This app is designed to help you **learn** how Bubble Sort works, not just see the final answer.
"""
        )

        with gr.Row():
            input_box = gr.Textbox(
                label="Enter numbers (comma or space separated)",
                value="45, 12, 88, 5, 60, 22, 75, 30",
                placeholder="Example: 45, 12, 88, 5, 60, 22, 75, 30",
            )

        start_button = gr.Button("Start / Reset")
        next_button = gr.Button("Next Step")
        run_to_end_button = gr.Button("Run to End")

        state = gr.State()

        current_view = gr.Textbox(
            label="Current List & Status",
            interactive=False,
            lines=4,
        )
        stats_box = gr.Textbox(
            label="Statistics (Steps, Comparisons, Swaps)",
            interactive=False,
        )
        log_box = gr.Textbox(
            label="Detailed Step Log",
            interactive=False,
            lines=15,
        )

        # Wire buttons
        start_button.click(
            fn=init_state,
            inputs=input_box,
            outputs=[state, current_view, stats_box, log_box],
        )

        next_button.click(
            fn=bubble_step,
            inputs=state,
            outputs=[state, current_view, stats_box, log_box],
        )

        run_to_end_button.click(
            fn=bubble_run_to_end,
            inputs=state,
            outputs=[state, current_view, stats_box, log_box],
        )

    return demo


demo = build_interface()

if __name__ == "__main__":
    demo.launch()

# add demo tests
# add sounds
# change on 5th