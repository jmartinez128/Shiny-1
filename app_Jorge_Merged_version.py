from shiny import App, ui, render
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.express as px
import numpy as np

# Load your dataset (update the path accordingly)
df = pd.read_csv("./data/shopping_trends_imputed.csv")

# Handling missing values: Fill NaNs or drop them based on the context
df.fillna(0, inplace=True)  # Replace NaNs with 0 (or use dropna() if preferred)

# UI Section
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h2("Filters"),
        ui.input_slider("age_range", "Age Range", min=18, max=80, value=(35, 60)),
        ui.input_select("category", "Product Category", 
                        choices=["All", "Accessories", "Clothing", "Footwear", "Outerwear"]),
        ui.input_select("season", "Season", 
                        choices=["All", "Spring", "Summer", "Fall", "Winter"]),
        ui.input_checkbox_group("gender", "Gender", ["Male", "Female"]),
        ui.input_checkbox_group("payment_method", "Payment Method",
                                choices=["Credit Card", "Debit Card", "PayPal", "Venmo"]),
        ui.input_checkbox("show_discounts", "Show Discount/Promo Code Impact"),
    ),
    ui.h2("Shopping Trends Analysis"),
    ui.navset_tab(
        ui.nav_panel("Overview", 
            ui.output_text("key_findings_summary"),
            output_widget("age_vs_spending_scatter"),
            output_widget("gender_spending_comparison"),
            output_widget("category_spending_comparison")
        ),
        ui.nav_panel("Seasonal and Category Analysis",
            output_widget("seasonal_category_heatmap"),
            output_widget("seasonal_spending_trends"),
            ui.output_text("category_season_insights")
        ),
        ui.nav_panel("Customer Behavior",
            output_widget("payment_method_comparison"),
            ui.panel_conditional(
                "input.show_discounts",
                output_widget("discount_promo_impact")
            ),
            output_widget("subscription_discount_correlation")
        ),  
    )
)

# Server Section
def server(input, output, session):
    # Apply filters across all graphs
    def apply_filters(df):
        # Filter dataset by selected age range
        filtered_df = df[(df['Age'] >= input.age_range()[0]) & (df['Age'] <= input.age_range()[1])]
        # Filter by gender
        if input.gender():
            filtered_df = filtered_df[filtered_df['Gender'].isin(input.gender())]
        # Filter by product category
        if input.category() != "All":
            filtered_df = filtered_df[filtered_df['Category'] == input.category()]
        # Filter by season
        if input.season() != "All":
            filtered_df = filtered_df[filtered_df['Season'] == input.season()]
        # Return the filtered dataframe
        return filtered_df

    # Age vs spending scatter plot
    @output
    @render_widget
    def age_vs_spending_scatter():
        filtered_df = apply_filters(df)
        fig = px.scatter(filtered_df, x="Age", y="Purchase_Amount_USD", color="Gender", title="Age vs Spending")
        return fig

    # Gender spending comparison plot
    @output
    @render_widget
    def gender_spending_comparison():
        filtered_df = apply_filters(df)
        gender_df = filtered_df.groupby("Gender")["Purchase_Amount_USD"].mean().reset_index()
        fig = px.bar(gender_df, x="Gender", y="Purchase_Amount_USD", title="Gender Spending Comparison")
        return fig

    # Category spending comparison plot
    @output
    @render_widget
    def category_spending_comparison():
        filtered_df = apply_filters(df)
        category_df = filtered_df.groupby("Category")["Purchase_Amount_USD"].mean().reset_index()
        fig = px.bar(category_df, x="Category", y="Purchase_Amount_USD", title="Category Spending Comparison")
        return fig
    
# Seasonal category heatmap
    @output
    @render_widget
    def seasonal_category_heatmap():
        filtered_df = apply_filters(df)
        seasonal_category_df = filtered_df.groupby(["Season", "Category"])["Purchase_Amount_USD"].mean().unstack()
        
        # Calculate the overall mean across all seasons and categories
        overall_mean = filtered_df["Purchase_Amount_USD"].mean()
        
        # Calculate percentage difference from mean
        diff_from_mean = ((seasonal_category_df - overall_mean) / overall_mean * 100).round(1)
        
        # Create basic heatmap
        fig = px.imshow(seasonal_category_df,
                       title="Seasonal Category Spending Heatmap",
                       color_continuous_scale=["white", "blue"],
                       aspect="auto"
                       )
        
        # Add annotations
        for i in range(len(seasonal_category_df.index)):
            for j in range(len(seasonal_category_df.columns)):
                fig.add_annotation(
                    x=j,
                    y=i,
                    text=f"{diff_from_mean.iloc[i, j]:.1f}%",
                    showarrow=False,
                    font=dict(color="black")
                )
        
        return fig
    
    # Seasonal spending trends
    @output
    @render_widget
    def seasonal_spending_trends():
        filtered_df = apply_filters(df)
        seasonal_df = filtered_df.groupby("Season")["Purchase_Amount_USD"].mean().reset_index()
        fig = px.line(seasonal_df, x="Season", y="Purchase_Amount_USD", title="Seasonal Spending Trends")
        return fig

    @output
    @render_widget
    def payment_method_comparison():
        filtered_df = apply_filters(df)
        
        # Filter by selected payment methods
        if input.payment_method():
            filtered_df = filtered_df[filtered_df['Payment_Method'].isin(input.payment_method())]
        
        # Group by Payment_Method and sum the Purchase_Amount_USD
        payment_df = filtered_df.groupby("Payment_Method")["Purchase_Amount_USD"].mean().reset_index()
        
        # Check if we have any data after filtering
        if payment_df.empty:
            fig = px.pie(title="No data available for the selected filters")
        else:
            fig = px.pie(payment_df, names="Payment_Method", values="Purchase_Amount_USD", 
                        title="Payment Method Comparison")
        
        return fig


    # Discount/promo impact
    @output
    @render_widget
    def discount_promo_impact():
        filtered_df = apply_filters(df)
        promo_df = filtered_df.groupby("Discount_Applied")["Purchase_Amount_USD"].mean().reset_index()
        fig = px.bar(promo_df, x="Discount_Applied", y="Purchase_Amount_USD", title="Discount/Promo Impact")
        return fig

    # Subscription discount correlation
    @output
    @render_widget
    def subscription_discount_correlation():
        filtered_df = apply_filters(df)
        subscription_df = filtered_df.groupby(["Subscription_Status", "Discount_Applied"])["Purchase_Amount_USD"].mean().unstack()
        fig = px.imshow(subscription_df, title="Subscription Status vs Discount Correlation")
        return fig

    # Key findings summary
    @output
    @render.text
    def key_findings_summary():
        return "Key findings will be summarized here."

    # Category season insights
    @output
    @render.text
    def category_season_insights():
        return "Category and season-related insights will be displayed here."


# Create the Shiny app
app = App(app_ui, server)

