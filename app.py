import faicons as fa
import plotly.express as px

# Load data and compute static values
from shared import app_dir, shopping_trends
from shiny import reactive, render
from shiny.express import input, ui
from shinywidgets import render_plotly

purchase_range = (min(shopping_trends.Purchase_Amount_USD), max(shopping_trends.Purchase_Amount_USD))

# Add page title and sidebar
ui.page_opts(title="Shopping Trends Analysis by Jorge", fillable=True)

with ui.sidebar(open="desktop"):
    ui.input_slider(
        "Purchase_Amount_USD",
        "Purchase Amount",
        min=purchase_range[0],
        max=purchase_range[1],
        value=purchase_range,
        pre="$",
    )
    ui.input_checkbox_group(
        "Gender",
        "Gender",
        ["Male", "Female"],
        selected=["Male", "Female"],
        inline=True,
    )
    ui.input_action_button("reset", "Reset filter")

# Add main content
ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("address-book"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["user"]):
        "Total tippers"

        @render.express
        def total_tippers():
            shopping_trends_data().shape[0]

    with ui.value_box(showcase=ICONS["wallet"]):
        "Average tip"

        @render.express
        def average_tip():
            d = shopping_trends_data()
            if d.shape[0] > 0:
                perc = d.tip / d.Purchase_Amount_USD
                f"{perc.mean():.1%}"

    with ui.value_box(showcase=ICONS["currency-dollar"]):
        "Average bill"

        @render.express
        def average_bill():
            d = shopping_trends_data()
            if d.shape[0] > 0:
                bill = d.Purchase_Amount_USD.mean()
                f"${bill:.2f}"


with ui.layout_columns(col_widths=[6, 6, 12]):
    with ui.card(full_screen=True):
        ui.card_header("Shopping Trends data") # updated card title

        @render.data_frame
        def table():
            return render.DataGrid(shopping_trends_data())

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "total purchase amount versus age"
            with ui.popover(title="Add a color variable", placement="top"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "scatter_color",
                    None,
                    ["None", "Location", "Color", "Gender", "Season", "Category"], 
                    inline=True,
                )

        @render_plotly
        def scatterplot():
            color = input.scatter_color()
            return px.scatter(
                shopping_trends_data(),
                x="Purchase_Amount_USD",
                y="Age",
                color=None if color == "None" else color, # updated none -> None to match what was listed
                trendline="lowess",
            )

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Previous Purchase percentage" # Tip -> Previous Purchase
            with ui.popover(title="Add a color variable"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "pp_perc_y", # tip -> pp
                    "Split by:",
                    ["Location", "Color", "Gender", "Season", "Category"], # updated categories
                    selected="Season", # updated default to Season
                    inline=True,
                )

        @render_plotly
        def tip_perc():
            from ridgeplot import ridgeplot

            dat = shopping_trends_data()
            dat["percent"] = dat.Previous_Purchases / dat.Purchase_Amount_USD # dat.tip -> dat.Previous_Purchases
            yvar = input.pp_perc_y() # input.tip_perc_y() -> input.pp_perc_y()
            uvals = dat[yvar].unique()

            samples = [[dat.percent[dat[yvar] == val]] for val in uvals]

            plt = ridgeplot(
                samples=samples,
                labels=uvals,
                bandwidth=0.01,
                colorscale="viridis",
                colormode="row-index",
            )

            plt.update_layout(
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
                )
            )

            return plt


ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


@reactive.calc
def shopping_trends_data():
    bill = input.Purchase_Amount_USD()
    idx1 = shopping_trends.Purchase_Amount_USD.between(bill[0], bill[1])
    idx2 = shopping_trends.Gender.isin(input.Gender()) # updated Age -> Gender because this filter should match what's on the left side
    return shopping_trends[idx1 & idx2]


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("Purchase_Amount_USD", value=purchase_range)
    ui.update_checkbox_group("Gender", selected=["Male", "Female"])
