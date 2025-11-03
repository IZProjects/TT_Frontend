# pip install dash dash-mantine-components pandas
from dash import Dash, dcc, html, Input, Output, State, no_update
import dash_mantine_components as dmc
import pandas as pd
from datetime import datetime
import re

app = Dash(__name__)

CHECK_OPTIONS = [
    {"label": "UI/Design", "value": "ui"},
    {"label": "Speed/Performance", "value": "speed"},
    {"label": "Features", "value": "features"},
    {"label": "Docs/Examples", "value": "docs"},
]

def records_to_df(records: list[dict]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=[
            "timestamp", "email", "comments",
            "ui", "speed", "features", "docs", "selected"
        ])
    return pd.DataFrame.from_records(records)

app.layout = dmc.MantineProvider(
    children=dmc.Container(
        size="sm",
        pt=24,
        children=[
            dmc.Title("Feedback Form", order=2, mb="md"),
            dmc.Stack(
                gap="md",
                children=[
                    dmc.TextInput(
                        id="email",
                        label="Email",
                        placeholder="you@example.com",
                        withAsterisk=True,
                        required=True,
                        description="We'll only use this to follow up if needed."
                    ),
                    dmc.Textarea(
                        id="comments",
                        label="Comments",
                        placeholder="Tell us what went well or what could be improved...",
                        autosize=True, minRows=3, maxRows=8
                    ),
                    dmc.Group(
                        align="center",
                        gap="xs",
                        children=[
                            dmc.Checkbox(
                                id="select-all",
                                label="Select all",
                                checked=False,
                                indeterminate=False,
                            ),
                            dmc.CheckboxGroup(
                                id="topics",
                                label="What are you giving feedback on?",
                                value=[],
                                children=[dmc.Checkbox(o["label"], value=o["value"]) for o in CHECK_OPTIONS],
                            ),
                        ],
                    ),
                    dmc.Button("Submit", id="submit", variant="filled"),
                    dmc.Alert(
                        id="form-status",
                        title="",
                        color="blue",
                        variant="light",
                        children="",
                        style={"display": "none"},
                    ),
                    dcc.Store(id="feedback-store", data=[]),
                    dmc.Divider(label="Submissions (preview)", labelPosition="center"),
                    html.Div(id="preview-table"),
                ]
            ),
        ],
    )
)

# --- Select-all → update group selection ---
@app.callback(
    Output("topics", "value"),
    Input("select-all", "checked"),
    prevent_initial_call=True,
)
def toggle_all(checked):
    return [o["value"] for o in CHECK_OPTIONS] if checked else []

# --- Group selection → reflect back to select-all checked/indeterminate ---
@app.callback(
    Output("select-all", "checked"),
    Output("select-all", "indeterminate"),
    Input("topics", "value"),
)
def reflect_master_state(selected):
    all_values = [o["value"] for o in CHECK_OPTIONS]
    if not selected:
        return False, False
    if set(selected) == set(all_values):
        return True, False
    return False, True

# --- Submit handler ---
@app.callback(
    Output("feedback-store", "data"),
    Output("form-status", "children"),
    Output("form-status", "title"),
    Output("form-status", "color"),
    Output("form-status", "style"),
    Input("submit", "n_clicks"),
    State("email", "value"),
    State("comments", "value"),
    State("topics", "value"),
    State("feedback-store", "data"),
    prevent_initial_call=True,
)
def handle_submit(n_clicks, email, comments, topics, store_records):
    # Basic email validation
    email_ok = bool(email) and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or "")
    if not email_ok:
        return no_update, "Please enter a valid email address.", "Validation error", "red", {"display": "block"}

    topics = topics or []
    # Build a row with boolean flags for each checkbox + a readable list
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "email": email.strip(),
        "comments": (comments or "").strip(),
        "ui": "ui" in topics,
        "speed": "speed" in topics,
        "features": "features" in topics,
        "docs": "docs" in topics,
        "selected": ", ".join(topics) if topics else "",
    }

    updated = (store_records or []) + [row]
    return (
        updated,
        "Thank you! Your feedback has been recorded.",
        "Success",
        "green",
        {"display": "block"},
    )

# --- Preview table (renders the current in-memory DataFrame) ---
@app.callback(
    Output("preview-table", "children"),
    Input("feedback-store", "data"),
)
def render_preview(records):
    df = records_to_df(records or [])
    print(df)
    if df.empty:
        return dmc.Text("No submissions yet.", c="dimmed")
    # Render a simple scrollable table
    header = html.Thead(html.Tr([html.Th(col) for col in df.columns]))
    body_rows = [
        html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
        for i in range(len(df))
    ]
    table = dmc.ScrollArea(
        h=240,
        children=dmc.Table(
            striped=True,
            highlightOnHover=True,
            withTableBorder=True,
            withColumnBorders=True,
            children=[header, html.Tbody(body_rows)],
        ),
    )
    return table

if __name__ == "__main__":
    app.run(debug=True)
