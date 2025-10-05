import dash
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dcc, html

URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
df = pd.read_csv(URL)
df_rec = df[df["Recession"] == 1]


# Label and mapping
vehicle_type_names = {
    "Supperminicar": "Super Mini Car",
    "Mediumfamilycar": "Medium Family Car",
    "Smallfamiliycar": "Small Family Car",
    "Sports": "Sports Car",
    "Executivecar": "Executive Car",
}
label_names = {
    "Automobile_Sales": "Automobile Sales",
    "Vehicle_Type": "Vehicle Type",
    "Advertising_Expenditure": "Advertising Expenditure",
    "unemployment_rate": "Unemployment Rate",
}

# Dash setup
external_scripts = [{"src": "https://cdn.tailwindcss.com"}]
app = Dash(__name__, external_scripts=external_scripts)
app.config.suppress_callback_exceptions = True

app.layout = html.Main(
    className="min-h-screen bg-gray-50 flex flex-col items-center p-6 space-y-8",
    children=[
        html.H1(
            "🚗 Automobile Sales Statistics Dashboard",
            className="text-5xl font-bold text-center text-indigo-800 drop-shadow-lg",
        ),
        html.Div(
            className="bg-white shadow-lg rounded-2xl p-6 w-full max-w-2xl",
            children=[
                html.Label(
                    "Select Report Type:",
                    className="text-lg font-semibold text-gray-800",
                    htmlFor="input-report",
                ),
                dcc.Dropdown(
                    options=[
                        {"label": "Yearly Statistics", "value": "Yearly"},
                        {"label": "Recession Period Statistics", "value": "Recession"},
                    ],
                    value="Yearly",
                    id="input-report",
                    className="mt-2 text-gray-700",
                ),
                html.Br(),
                html.Label(
                    "Year:",
                    className="text-lg font-semibold text-gray-800",
                    htmlFor="input-year",
                ),
                dcc.Dropdown(
                    sorted(df.Year.unique()),
                    value=2005,
                    id="input-year",
                    disabled=True,
                    className="mt-2 text-gray-700",
                ),
            ],
        ),
        html.Section(
            className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-7xl",
            children=[
                html.Div(className="bg-white p-4 shadow rounded-2xl", children=[dcc.Graph(id="plot-1")]),
                html.Div(className="bg-white p-4 shadow rounded-2xl", children=[dcc.Graph(id="plot-2")]),
                html.Div(className="bg-white p-4 shadow rounded-2xl", children=[dcc.Graph(id="plot-3")]),
                html.Div(className="bg-white p-4 shadow rounded-2xl", children=[dcc.Graph(id="plot-4")]),
            ],
        ),
    ],
)

# Disable year dropdown when "Recession" is selected
@callback(Output("input-year", "disabled"), Input("input-report", "value"))
def disable_year(report_value):
    return report_value == "Recession"

# Update plots
@callback(
    [Output("plot-1", "figure"), Output("plot-2", "figure"), Output("plot-3", "figure"), Output("plot-4", "figure")],
    [Input("input-report", "value"), Input("input-year", "value")],
)
def display_graphs(report_value, entered_year):
    if report_value == "Recession":
        return recession_graphs()
    else:
        return year_graphs(entered_year)

# Recession period graphs
def recession_graphs():
    template = "plotly_white"
    accent = "#6A1B9A"

    fig_line = px.line(
        df_rec.groupby("Year")["Automobile_Sales"].mean().reset_index(),
        x="Year",
        y="Automobile_Sales",
        title="Average Automobile Sales by Year (Recession)",
        template=template,
        color_discrete_sequence=[accent],
        labels=label_names,
    )

    bar_df = df_rec.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
    bar_df["Vehicle_Type"] = bar_df["Vehicle_Type"].map(vehicle_type_names)
    fig_bar_1 = px.bar(
        bar_df,
        x="Vehicle_Type",
        y="Automobile_Sales",
        title="Average Automobile Sales by Vehicle Type (Recession)",
        template=template,
        color_discrete_sequence=[accent],
        labels=label_names,
    )

    pie_df = df_rec.groupby("Vehicle_Type")["Advertising_Expenditure"].sum().reset_index()
    pie_df["Vehicle_Type"] = pie_df["Vehicle_Type"].map(vehicle_type_names)
    fig_pie = px.pie(
        pie_df,
        values="Advertising_Expenditure",
        names="Vehicle_Type",
        title="Advertising Expenditure by Vehicle Type (Recession)",
        template=template,
    )

    bar2_df = df_rec.groupby(["Vehicle_Type", "unemployment_rate"])["Automobile_Sales"].sum().reset_index()
    fig_bar_2 = px.bar(
        bar2_df,
        x="unemployment_rate",
        y="Automobile_Sales",
        color="Vehicle_Type",
        title="Automobile Sales vs Unemployment Rate (Recession)",
        template=template,
        labels=label_names,
    )

    fig_bar_2.for_each_trace(
        lambda t: t.update(
            name=vehicle_type_names.get(t.name, t.name),
            legendgroup=vehicle_type_names.get(t.name, t.name),
        )
    )
    return [fig_line, fig_bar_1, fig_pie, fig_bar_2]

# Yearly graphs
def year_graphs(entered_year):
    template = "plotly_white"
    accent = "#6A1B9A"

    df_year = df[df["Year"] == entered_year]

    fig_line = px.line(
        df.groupby("Year")["Automobile_Sales"].mean().reset_index(),
        x="Year",
        y="Automobile_Sales",
        title="Yearly Average Automobile Sales",
        template=template,
        color_discrete_sequence=[accent],
        labels=label_names,
    )

    fig_line_2 = px.line(
        df_year,
        x="Month",
        y="Automobile_Sales",
        title=f"Total Monthly Automobile Sales in {entered_year}",
        template=template,
        color_discrete_sequence=[accent],
        labels=label_names,
    )

    df_bar = df_year.groupby("Vehicle_Type")["Automobile_Sales"].sum().reset_index()
    df_bar["Automobile_Sales"] /= 12
    df_bar["Vehicle_Type"] = df_bar["Vehicle_Type"].map(vehicle_type_names)
    fig_bar = px.bar(
        df_bar,
        x="Vehicle_Type",
        y="Automobile_Sales",
        title=f"Average Monthly Automobile Sales by Vehicle Type in {entered_year}",
        template=template,
        color_discrete_sequence=[accent],
        labels=label_names,
    )

    pie_df = df_year.groupby("Vehicle_Type")["Advertising_Expenditure"].sum().reset_index()
    pie_df["Vehicle_Type"] = pie_df["Vehicle_Type"].map(vehicle_type_names)
    fig_pie = px.pie(
        pie_df,
        values="Advertising_Expenditure",
        names="Vehicle_Type",
        title=f"Advertising Expenditure by Vehicle Type in {entered_year}",
        template=template,
    )

    return [fig_line, fig_line_2, fig_bar, fig_pie]

if __name__ == "__main__":
    app.run(port=2222)
