import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page config
st.set_page_config(
    page_title="India Workforce Dashboard",
    page_icon="📊",
    layout="wide"
)

# App title
st.title("📊 India Workforce Analytics Dashboard")
st.markdown("Visualizing Main and Marginal Workers by State with Detailed Insights")

# Load data function
@st.cache_data
def load_data():
    # Replace with your actual data loading
    df = pd.read_csv(r"C:/Users/mutha/Downloads/clustered_nic_data_with_state.csv")
    
    # Aggregate data by state
    state_data = df.groupby('State').agg({
        'Main Workers - Total -  Persons': 'sum',
        'Marginal Workers - Total -  Persons': 'sum'
    }).reset_index()
    
    state_name_mapping = {
    'MAHARASHTRA' : 'Maharashtra',
    'GOA' : 'Goa',
    'BIHAR' : 'Bihar',
    'KERALA' : 'Kerala',
    'SIKKIM' : 'Sikkim',
    'JHARKHAND' : 'Jharkhand',
    'TRIPURA' : 'Tripura',
    'ODISHA' : 'Odisha',
    'UTTAR' : 'Uttar Pradesh',
    'HIMACHAL' : 'Himachal Pradesh',
    'MIZORAM' : 'Mizoram',
    'NCT' : 'Delhi',
    'MANIPUR' : 'Manipur',
    'GUJARAT' : 'Gujarat',
    'NAGALAND' : 'Nagaland',
    'RAJASTHAN' : 'Rajasthan',
    'UTTARAKHAND' : 'Uttarakhand',
    'ARUNACHAL' : 'Arunachal Pradesh',
    'WEST' : 'West Bengal',
    'KARNATAKA' : 'Karnataka',
    'PUDUCHERRY' : 'Puducherry',
    'ASSAM' : 'Assam',
    'TAMIL' : 'Tamil Nadu',
    
    }
    
    state_data['State'] = state_data['State'].map(state_name_mapping)
    state_data['Total Workers'] = (state_data['Main Workers - Total -  Persons'] + 
                                 state_data['Marginal Workers - Total -  Persons'])
    state_data['Worker Ratio'] = (state_data['Marginal Workers - Total -  Persons'] / 
                                 state_data['Main Workers - Total -  Persons'])
    
    return state_data.sort_values('Total Workers', ascending=False)

# Load the data
state_data = load_data()

# Sidebar controls
with st.sidebar:
    st.header("Dashboard Controls")
    view_option = st.radio(
        "Map View:",
        ("Main Workers", "Marginal Workers", "Both", "Ratio"),
        index=2
    )
    
    color_scale_main = st.selectbox(
        "Main Workers Color Scale",
        ["Blues", "Viridis", "Plasma", "Inferno"],
        index=0
    )
    
    color_scale_marginal = st.selectbox(
        "Marginal Workers Color Scale",
        ["Reds", "Oranges", "Hot", "Magma"],
        index=0
    )
    
    selected_state = st.selectbox(
        "Select State for Detailed Analysis:",
        state_data['State'].unique()
    )
    
    st.markdown("---")
    st.markdown("**Nationwide Summary**")
    st.metric("Total Main Workers", f"{state_data['Main Workers - Total -  Persons'].sum():,}")
    st.metric("Total Marginal Workers", f"{state_data['Marginal Workers - Total -  Persons'].sum():,}")
    st.metric("Average Ratio", f"{state_data['Worker Ratio'].mean():.2f}")

# Main map visualization
def create_map(view, scale_main, scale_marginal):
    fig = go.Figure()
    
    if view in ["Main Workers", "Both"]:
        fig.add_trace(go.Choropleth(
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            locations=state_data['State'],
            featureidkey='properties.ST_NM',
            z=state_data['Main Workers - Total -  Persons'],
            colorscale=scale_main,
            name='Main Workers',
            colorbar_title="Main Workers",
            marker_line_color='gray',
            marker_line_width=0.5,
            visible=view != "Marginal Workers",
            hovertemplate="<b>%{location}</b><br>Main Workers: %{z:,}<extra></extra>"
        ))
    
    if view in ["Marginal Workers", "Both"]:
        fig.add_trace(go.Choropleth(
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            locations=state_data['State'],
            featureidkey='properties.ST_NM',
            z=state_data['Marginal Workers - Total -  Persons'],
            colorscale=scale_marginal,
            name='Marginal Workers',
            colorbar_title="Marginal Workers",
            marker_opacity=0.7 if view == "Both" else 1,
            marker_line_color='gray',
            marker_line_width=0.5,
            visible=view != "Main Workers",
            hovertemplate="<b>%{location}</b><br>Marginal Workers: %{z:,}<extra></extra>"
        ))
    
    if view == "Ratio":
        fig.add_trace(go.Choropleth(
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            locations=state_data['State'],
            featureidkey='properties.ST_NM',
            z=state_data['Worker Ratio'],
            colorscale='RdBu',
            name='Marginal/Main Ratio',
            colorbar_title="Ratio",
            marker_line_color='gray',
            marker_line_width=0.5,
            hovertemplate="<b>%{location}</b><br>Ratio: %{z:.2f}<extra></extra>",
            zmid=0.5
        ))
    
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
        lonaxis_range=[68, 98],
        lataxis_range=[6, 38]
    )
    
    fig.update_layout(
        title_text=f'India Workforce Distribution - {view} View',
        title_x=0.5,
        margin={"r":0,"t":40,"l":0,"b":0},
        height=600,
        geo=dict(scope='asia')
    )
    
    return fig

# Create state insights section
def show_state_insights(state):
    state_df = state_data[state_data['State'] == state].iloc[0]
    
    st.subheader(f"📌 Detailed Analysis: {state}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Main Workers", f"{state_df['Main Workers - Total -  Persons']:,}")
    col2.metric("Marginal Workers", f"{state_df['Marginal Workers - Total -  Persons']:,}")
    col3.metric("Marginal/Main Ratio", f"{state_df['Worker Ratio']:.2f}")

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "xy"}]],  # First subplot is pie, second is XY
        subplot_titles=(
            f"Workforce Composition in {state}", 
            f"{state} vs National Average"
        )
    )

    # Ensure we're using scalar values for pie chart
    main_workers = state_df['Main Workers - Total -  Persons'].sum()
    marginal_workers = state_df['Marginal Workers - Total -  Persons'].sum()

    # Pie chart (now in proper pie-type subplot)
    fig.add_trace(go.Pie(
        labels=['Main Workers', 'Marginal Workers'],
        values=[main_workers, marginal_workers],
        name="Composition",
        hole=0.4,
        marker_colors=['#1f77b4', '#ff7f0e']
    ), row=1, col=1)

    # Bar chart comparison
    national_avg = state_data.mean(numeric_only=True)
    fig.add_trace(go.Bar(
        x=['Main Workers', 'Marginal Workers', 'Ratio'],
        y=[state_df['Main Workers - Total -  Persons']/national_avg['Main Workers - Total -  Persons'],
           state_df['Marginal Workers - Total -  Persons']/national_avg['Marginal Workers - Total -  Persons'],
           state_df['Worker Ratio']/national_avg['Worker Ratio']],
        name=state,
        marker_color='#2ca02c'
    ), row=1, col=2)

    # Update layout
    fig.update_layout(
        #title_text=f"Workforce Analysis: {state}",
        showlegend=True,
        barmode='group'
    )

    
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(t=40, b=0, l=0, r=0)
    )
    
    fig.update_yaxes(title_text="Ratio to National Average", row=1, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # State ranking information
    st.markdown("### State Rankings")
    rank_col1, rank_col2, rank_col3 = st.columns(3)
    
    main_rank = state_data['Main Workers - Total -  Persons'].rank(ascending=False).loc[state_data['State'] == state].values[0]
    rank_col1.metric("Main Workers Rank", f"{int(main_rank)}/{len(state_data)}")
    
    marginal_rank = state_data['Marginal Workers - Total -  Persons'].rank(ascending=False).loc[state_data['State'] == state].values[0]
    rank_col2.metric("Marginal Workers Rank", f"{int(marginal_rank)}/{len(state_data)}")
    
    ratio_rank = state_data['Worker Ratio'].rank(ascending=False).loc[state_data['State'] == state].values[0]
    rank_col3.metric("Ratio Rank", f"{int(ratio_rank)}/{len(state_data)}")

# Main layout
tab1, tab2 = st.tabs(["🗺️ National Overview", "📈 State Insights"])

with tab1:
    st.plotly_chart(create_map(view_option, color_scale_main, color_scale_marginal), 
                   use_container_width=True)
   
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.metric("Top State (Main Workers)", 
                f"{state_data.iloc[0]['State']}: {state_data.iloc[0]['Main Workers - Total -  Persons']:,}")
        
    with row1_col2:
        st.metric("Top State (Marginal Workers)", 
                f"{state_data.iloc[0]['State']}: {state_data.iloc[0]['Marginal Workers - Total -  Persons']:,}")

    # Row 2
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.metric("Highest Worker Ratio", 
                f"{state_data.loc[state_data['Worker Ratio'].idxmax()]['State']}: {state_data['Worker Ratio'].max():.2f}")
        
    with row2_col2:
        st.metric("Lowest Worker Ratio", 
                f"{state_data.loc[state_data['Worker Ratio'].idxmin()]['State']}: {state_data['Worker Ratio'].min():.2f}")
        # Data table
    with st.expander("📋 View All State Data"):
            st.dataframe(state_data, use_container_width=True)

with tab2:
    show_state_insights(selected_state)
    
    # Comparative analysis
    st.subheader("Comparative Analysis")
    
    # Top 5 states by different metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top 5 States by Main Workers**")
        st.dataframe(state_data.nlargest(5, 'Main Workers - Total -  Persons')[['State', 'Main Workers - Total -  Persons']]
                    .rename(columns={'Main Workers - Total -  Persons': 'Count'}),
                    hide_index=True)
    
    with col2:
        st.markdown("**Top 5 States by Marginal Workers**")
        st.dataframe(state_data.nlargest(5, 'Marginal Workers - Total -  Persons')[['State', 'Marginal Workers - Total -  Persons']]
                    .rename(columns={'Marginal Workers - Total -  Persons': 'Count'}),
                    hide_index=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("**Top 5 States by Worker Ratio**")
        st.dataframe(state_data.nlargest(5, 'Worker Ratio')[['State', 'Worker Ratio']],
                    hide_index=True)
    
    with col4:
        st.markdown("**Bottom 5 States by Worker Ratio**")
        st.dataframe(state_data.nsmallest(5, 'Worker Ratio')[['State', 'Worker Ratio']],
                    hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
**Data Insights:**
- States with higher marginal worker ratios may indicate more informal or seasonal employment
- Worker ratios can help identify states needing employment stability programs
- Compare states against national averages for context
""")