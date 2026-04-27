import streamlit as st
import pandas as pd
from io import BytesIO
import datetime
import base64
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes

st.set_page_config(layout="wide")

header_col, card1, card2, card3 = st.columns([1.5, 1, 1, 1])

with header_col:
    st.markdown("<h3 style='margin-top: 15px; margin-bottom: 0px;'>Anand Wealth Fund Analysis</h3>", unsafe_allow_html=True)

card1_placeholder = card1.empty()
card2_placeholder = card2.empty()
card3_placeholder = card3.empty()
# ----------------------------
# Custom Styling
# ----------------------------
st.markdown("""
<style>

/* ===== Tabs Styling ===== */
.stTabs [data-baseweb="tab"] {
    font-size:16px;
    padding:10px 20px;
    border-radius:8px;
}

.stTabs [aria-selected="true"] {
    background-color:#1f77b4 !important;
    color:white !important;
}

/* ===== Metric Card Styling ===== */
div[data-testid="metric-container"] {
    background-color: #f8f9fa;
    border-radius: 12px;
    padding: 15px;
    border-left: 8px solid #1f77b4;
}

/* Remove top spacing */
.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] > div {
    gap: 0rem !important;
}

button {
    margin: 0px !important;
    border-radius: 4px !important;
}

/* File Uploader small height */
div[data-testid="stFileUploader"] section {
    padding: 2px !important;
    min-height: 40px !important;
}
div[data-testid="stFileUploader"] section > div {
    padding: 2px !important;
}
div[data-testid="stFileUploader"] small {
    display: none !important; /* hide the 'Limit 200MB per file' text */
}
</style>
""", unsafe_allow_html=True)



# -------------------------------------------------------
# EXPORT FUNCTIONS (NO COLUMNS INSIDE THESE)
# -------------------------------------------------------

def create_combined_df(df_dict):
    combined_list = []
    for name, df in df_dict.items():
        if not df.empty:
            header_row = {col: "" for col in df.columns}
            header_row[df.columns[0]] = f"--- {name.upper()} ---"
            
            combined_list.append(pd.DataFrame([header_row]))
            combined_list.append(df)
            combined_list.append(pd.DataFrame([{col: "" for col in df.columns}]))
    
    if combined_list:
        return pd.concat(combined_list, ignore_index=True)
    return pd.DataFrame()

def render_export_excel(df_dict, filename, category, subcategory, button_key):
    today = datetime.date.today().strftime("%d-%b-%Y")
    output = BytesIO()
    
    combined_df = create_combined_df(df_dict)
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        combined_df.to_excel(writer, index=False, startrow=5, sheet_name='Report')
        worksheet = writer.sheets['Report']
        worksheet.cell(row=1, column=1, value=f"Category: {category}")
        worksheet.cell(row=2, column=1, value=f"Subcategory: {subcategory}")
        worksheet.cell(row=3, column=1, value=f"Date: {today}")
        worksheet.cell(row=4, column=1, value=f"Report: {filename}")

    st.download_button(
        "📥",
        data=output.getvalue(),
        file_name=f"{filename}_{today}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Download Combined Excel",
        key=f"excel_{button_key}"
    )

def render_export_pdf(df_dict, filename, category, subcategory, button_key):
    today = datetime.date.today().strftime("%d-%b-%Y")
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=pagesizes.A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"{filename}", styles["Heading2"]))
    elements.append(Paragraph(f"<b>Category:</b> {category} &nbsp;&nbsp;&nbsp; <b>Subcategory:</b> {subcategory} &nbsp;&nbsp;&nbsp; <b>Date:</b> {today}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    for name, df in df_dict.items():
        if not df.empty:
            elements.append(Paragraph(f"<b>{name}</b>", styles["Heading3"]))
            elements.append(Spacer(1, 6))
            table_data = [df.columns.tolist()] + df.values.tolist()
            table = Table(table_data)
            table.setStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black)
            ])
            elements.append(table)
            elements.append(Spacer(1, 12))

    doc.build(elements)

    st.download_button(
        "📄",
        data=buffer.getvalue(),
        file_name=f"{filename}_{today}.pdf",
        mime="application/pdf",
        help="Download Combined PDF",
        key=f"pdf_{button_key}"
    )

def render_print_button(df_dict, filename, category, subcategory):
    today = datetime.date.today().strftime("%d-%b-%Y")
    
    tables_html = ""
    for name, df in df_dict.items():
        if not df.empty:
            tables_html += f"<h3>{name}</h3>"
            tables_html += df.to_html(index=False)
            tables_html += "<br>"

    html = f"""
    <html><head><title>{filename}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
    </head><body>
    <h2>{filename}</h2>
    <p><b>Category:</b> {category} &nbsp;|&nbsp; <b>Subcategory:</b> {subcategory} &nbsp;|&nbsp; <b>Date:</b> {today}</p>
    {tables_html}
    <script>window.print();</script>
    </body></html>
    """
    
    b64 = base64.b64encode(html.encode('utf-8')).decode('utf-8')
    href = f"data:text/html;base64,{b64}"
    
    st.markdown(
        f"""
        <a href="{href}" target="_blank" 
        style="padding:6px 10px;border-radius:6px;border:1px solid #ccc;background:#f0f0f0;cursor:pointer;text-decoration:none;color:black;display:inline-block;"
        title="Print">
        🖨
        </a>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------------
# CATEGORY MAP
# -------------------------------------------------------

category_map = {
    "DEBT FUNDS": [
        "OVERNIGHT FUND",
        "MONEY MARKET FUND",
        "LIQUID FUND",
        "ULTRA SHORT DURATION FUND",
        "LOW DURATION FUND",
        "SHORT DURATION FUND",
        "MEDIUM DURATION FUND",
        "MEDIUM TO LONG DURATION FUND",
        "LONG DURATION FUND",
        "DYNAMIC BOND",
        "CORPORATE BOND FUND",
        "CREDIT RISK FUND",
        "BANKING AND PSU FUND",
        "GILT FUND",
        "GILT FUND WITH 10 YR CONSTANT",
        "TARGET MATURITY FUND",
        "FLOATER FUND"
    ],
    "HYBRID FUNDS": [
        "ARBITRAGE FUND",
        "CONSERVATIVE HYBRID FUND",
        "AGGRESSIVE HYBRID FUND",
        "DYNAMIC ASSET ALLOCATION",
        "BALANCED ADVANTAGE FUND",
        "BALANCED HYBRID FUND",
        "EQUITY SAVINGS",
        "MULTI ASSET ALLOCATION"
    ],
    "SOLUTION ORIENTED FUNDS": [
        "RETIREMENT FUND",
        "CHILDRENS FUNDS"
    ],
    "EQUITY FUNDS": [
        "MULTI CAP FUND",
        "FLEXI CAP FUND",
        "LARGE CAP FUND",
        "LARGE & MID CAP FUND",
        "MID CAP FUND",
        "SMALL CAP FUND",
        "DIVIDEND YIELD FUND",
        "VALUE / CONTRA FUND",
        "FOCUSED FUND",
        "SECTOR-BANKING FUND",
        "SECTOR-CONSUMPTION FUND",
        "SECTOR-ENERGY & POWER FUND",
        "SECTOR-MNC FUND",
        "SECTOR-PHARMA & HEALTHCARE FUND",
        "SECTOR-SERVICE INDUSTRY FUND",
        "SECTOR-TECHNOLOGY",
        "THEMATIC FUND",
        "THEMATIC-INFRASTRUCTURE FUND",
        "ELSS FUND",
        "INTERNATIONAL FUND"
    ],
    "OTHER FUNDS": [
        "INDEX FUNDS",
        "INDEX NIFTY FUND",
        "INDEX NIFTY NEXT 50 FUND",
        "INDEX SENSEX FUND",
        "INDEX OTHERS FUND",
        "ETFS - GOLD FUND",
        "ETFS - SILVER FUND",
        "ETFS - OTHERS",
        "FOF - DEBT ORIENTED FUND",
        "FOF - EQUITY ORIENTED FUND",
        "FOF - OVERSEAS / ETFs",
        "FOF - DOMESTIC / ETFs"
    ]
}

col1, col2, col3 = st.columns(3)

with col1:
    uploaded_file = st.file_uploader("Upload Excel File", type=["xls", "xlsx"])

if uploaded_file:

   # excel_file = pd.ExcelFile(uploaded_file)
    #excel_file = pd.ExcelFile(uploaded_file, engine="openpyxl")
    file_name = uploaded_file.name

    if file_name.endswith(".xlsx"):
        excel_file = pd.ExcelFile(uploaded_file, engine="openpyxl")
    elif file_name.endswith(".xls"):
        excel_file = pd.ExcelFile(uploaded_file, engine="xlrd")
    else:
        st.error("Unsupported file format")
        st.stop()
    with col2:
        fund_categories = ["All"] + list(category_map.keys())
        selected_category = st.selectbox("Fund Category", fund_categories)

    with col3:
        if selected_category == "All":
            sub_options = []
            for v in category_map.values():
                sub_options.extend(v)
        else:
            sub_options = category_map[selected_category]

        selected_sub = st.selectbox("Sub Category", ["Select"] + sub_options)

    if selected_sub != "Select":
        sheet_map = {
            "OVERNIGHT FUND": "Overnight Fund",
            "MONEY MARKET FUND": "Money Market Fund",
            "LIQUID FUND": "Liquid Fund",
            "ULTRA SHORT DURATION FUND": "Ultra Short Duration Fund",
            "LOW DURATION FUND": "Low Duration Fund",
            "SHORT DURATION FUND": "Short Duration Fund",
            "MEDIUM DURATION FUND": "Medium Duration Fund",
            "MEDIUM TO LONG DURATION FUND": "Medium to Long Duration Fund",
            "LONG DURATION FUND": "Long Duration Fund",
            "DYNAMIC BOND": "Dynamic Bond",
            "CORPORATE BOND FUND": "Corporate Bond Fund",
            "CREDIT RISK FUND": "Credit Risk Fund",
            "BANKING AND PSU FUND": "Banking and PSU Fund",
            "GILT FUND": "Gilt Fund",
            "GILT FUND WITH 10 YR CONSTANT": "Gilt Fund with 10 yr constant",
            "TARGET MATURITY FUND": "Target Maturity Fund",
            "FLOATER FUND": "Floater Fund",
            "ARBITRAGE FUND": "Arbitrage Fund",
            "CONSERVATIVE HYBRID FUND": "Conservative Hybrid Fund",
            "AGGRESSIVE HYBRID FUND": "Aggressive Hybrid Fund",
            "DYNAMIC ASSET ALLOCATION": "Dynamic Asset Allocation",
            "BALANCED ADVANTAGE FUND": "Balanced Advantage",
            "BALANCED HYBRID FUND": "Balanced Hybrid",
            "EQUITY SAVINGS": "Equity Savings",
            "MULTI ASSET ALLOCATION": "Multi Asset Allocation",
            "RETIREMENT FUND": "Retirement Fund",
            "CHILDRENS FUNDS": "Childrens Funds",
            "MULTI CAP FUND": "Multi Cap Fund",
            "FLEXI CAP FUND": "Flexi Cap Fund",
            "LARGE CAP FUND": "Large Cap Fund",
            "LARGE & MID CAP FUND": "Large & Mid Cap Fund",
            "MID CAP FUND": "Mid Cap Fund",
            "SMALL CAP FUND": "Small Cap Fund",
            "DIVIDEND YIELD FUND": "Dividend Yield Fund",
            "VALUE / CONTRA FUND": "Value Fund",
            "FOCUSED FUND": "Focused Fund",
            "SECTOR-BANKING FUND": "Sec-Bank",
            "SECTOR-CONSUMPTION FUND": "Sec-Consumption",
            "SECTOR-ENERGY & POWER FUND": "Sec-Energy & Power",
            "SECTOR-MNC FUND": "Sec-MNC",
            "SECTOR-PHARMA & HEALTHCARE FUND": "Sec-Pharma",
            "SECTOR-SERVICE INDUSTRY FUND": "Sec-Service",
            "SECTOR-TECHNOLOGY": "Sec-Tech",
            "THEMATIC FUND": "Thematic",
            "THEMATIC-INFRASTRUCTURE FUND": "Them-Infra",
            "ELSS FUND": "ELSS",
            "INTERNATIONAL FUND": "Global",
            "INDEX FUNDS": "Index Funds",
            "INDEX NIFTY FUND": "Index Nifty",
            "INDEX NIFTY NEXT 50 FUND": "Index-Nifty Next 50",
            "INDEX SENSEX FUND": "Index - Sensex",
            "INDEX OTHERS FUND": "Index Fund Others",
            "ETFS - GOLD FUND": "ETFs - Gold",
            "ETFS - SILVER FUND": "ETFs - Silver",
            "ETFS - OTHERS": "ETFs - Others",
            "FOF - DEBT ORIENTED FUND": "FOF-Debt Oriented",
            "FOF - EQUITY ORIENTED FUND": "FOF-Equity Oriented",
            "FOF - OVERSEAS / ETFs": "FoF - Overseas",
            "FOF - DOMESTIC / ETFs": "FOF-Domestic"
        }
        actual_sheet_name = sheet_map.get(selected_sub, selected_sub)

        if actual_sheet_name in excel_file.sheet_names:

            # -------------------------------------------------------
            # LOAD DATA
            # -------------------------------------------------------

            raw = pd.read_excel(uploaded_file, sheet_name=actual_sheet_name, header=None, engine=excel_file.engine)
            header_row = raw[
                raw.astype(str)
                .apply(lambda x: x.str.contains("^Scheme Name$", case=False, na=False))
                .any(axis=1)
            ].index[0]

            df = pd.read_excel(uploaded_file, sheet_name=actual_sheet_name, header=header_row, engine=excel_file.engine)
        df.columns = df.columns.astype(str).str.strip()

        df = df[df["Scheme Name"].notna()]
        df = df[~df["Scheme Name"].str.contains("To view Exit", na=False)]

        required_periods = ["1 Month","3 Months","6 Months","YTD","1 Year","2 Years"]

        quartile_map = {}
        for period in required_periods:
            matches = [c for c in df.columns if c.startswith(period)]
            if len(matches) >= 2:
                quartile_map[period] = matches[1]

        selected_cols = ["Scheme Name"] + list(quartile_map.values())
        final_df = df[selected_cols].copy()

        rename_dict = {v: k for k, v in quartile_map.items()}
        final_df.rename(columns=rename_dict, inplace=True)

        for col in required_periods:
            final_df[col] = pd.to_numeric(final_df[col], errors="coerce")

        final_df = final_df.dropna(subset=required_periods, how="all")

        # -------------------------------------------------------
        # CATEGORIZATION
        # -------------------------------------------------------

        good_df = final_df[(final_df[required_periods] <= 1).all(axis=1)]
        low_df = final_df[(final_df[required_periods] >= 3).all(axis=1)]
        neutral_df = final_df.drop(good_df.index.union(low_df.index))

        # -------------------------------------------------------
        # SUMMARY CARDS
        # -------------------------------------------------------

        with card1_placeholder:
            st.markdown("""
            <div style="background:#d4edda;padding:15px;border-radius:12px; height:100%;">
                <h6 style="color:#155724; margin:0px; font-size:14px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="Good Performing">✅ Good</h6>
                <h3 style="color:#155724; margin:0px;">{}</h3>
            </div>
            """.format(len(good_df)), unsafe_allow_html=True)

        with card2_placeholder:
            st.markdown("""
            <div style="background:#fff3cd;padding:15px;border-radius:12px; height:100%;">
                <h6 style="color:#856404; margin:0px; font-size:14px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="Neutral">⚖ Neutral</h6>
                <h3 style="color:#856404; margin:0px;">{}</h3>
            </div>
            """.format(len(neutral_df)), unsafe_allow_html=True)

        with card3_placeholder:
            st.markdown("""
            <div style="background:#f8d7da;padding:15px;border-radius:12px; height:100%;">
                <h6 style="color:#721c24; margin:0px; font-size:14px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="Low Performing">❌ Low</h6>
                <h3 style="color:#721c24; margin:0px;">{}</h3>
            </div>
            """.format(len(low_df)), unsafe_allow_html=True)

        # -------------------------------------------------------
        # TABS
        # -------------------------------------------------------

        tab_charts, tab1, tab2, tab3 = st.tabs([
            "Analytics",
            f"Good ({len(good_df)})",
            f"Neutral ({len(neutral_df)})",
            f"Low ({len(low_df)})"
        ])

        with tab_charts:
            st.markdown("#### Performance Analytics")
            ch1, ch2, ch3 = st.columns(3)

            periods = required_periods.copy()

            with ch1:
                st.markdown("##### 📈 Avg Quartile")
                avg_quartile = final_df[periods].mean()
                st.line_chart(
                    pd.DataFrame({"Average Quartile Score": avg_quartile}),
                    use_container_width=True
                )

            with ch2:
                st.markdown("##### 📊 Quartile Dist")
                q_counts = pd.DataFrame(index=periods)
                q_counts["Q1 (Best)"] = (final_df[periods] <= 1).sum()
                q_counts["Q2 (Good)"] = (final_df[periods] == 2).sum()
                q_counts["Q3 (Fair)"] = (final_df[periods] == 3).sum()
                q_counts["Q4 (Worst)"] = (final_df[periods] >= 4).sum()

                st.bar_chart(
                    q_counts,
                    use_container_width=True
                )

            with ch3:
                st.markdown("##### 📉 Consistency")
                final_df["Avg Quartile Score"] = final_df[periods].mean(axis=1)
                consistency_counts = final_df["Avg Quartile Score"].round(1).value_counts().sort_index()

                st.bar_chart(
                    pd.DataFrame({"Number of Funds": consistency_counts}),
                    use_container_width=True
                )

       
        def render_tab(df_data, name, key):

            # Main Row
            left, spacer, right = st.columns([2, 5 ,1])

            # ---------------------------
            # LEFT → Search Box
            # ---------------------------
            with left:
                search = st.text_input(
                    "Search",
                    placeholder="🔍 Search Scheme",
                    key=key,
                    label_visibility="collapsed"
                )

            # ---------------------------
            # RIGHT → Buttons (No Gap)
            # ---------------------------
            with right:
                btn1, btn2, btn3 = st.columns(3, gap="small")
                
                master_df_dict = {
                    "Good Performing": good_df,
                    "Low Performing": low_df
                }

                with btn1:
                    render_export_excel(master_df_dict, "Good_and_Low_Performing", selected_category, selected_sub, key)

                with btn2:
                    render_export_pdf(master_df_dict, "Good_and_Low_Performing", selected_category, selected_sub, key)

                with btn3:
                    render_print_button(master_df_dict, "Good_and_Low_Performing", selected_category, selected_sub)

            # ---------------------------
            # Apply Search
            # ---------------------------
            if search:
                df_data = df_data[
                    df_data["Scheme Name"].str.contains(search, case=False, na=False)
                ]

            st.dataframe(df_data, use_container_width=True, hide_index=True, height=700)

        # -------------------------------------------------------
        # RENDER TABS
        # -------------------------------------------------------

        with tab1:
            
            render_tab(good_df, "Good_Performing", "good")

        with tab2:
            render_tab(neutral_df, "Neutral", "neutral")

        with tab3:
            render_tab(low_df, "Low_Performing", "low")