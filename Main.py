import streamlit as st
import pandas as pd
from io import BytesIO
import datetime
import base64
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
import requests
import os



st.set_page_config(layout="wide")

@st.cache_data
def load_investors():
    import os
    try:
        # Use the file downloaded by autodownload.py
        file_path = "Data/AUM_IndividualWise.xlsx"
        # Fallback to root directory if Data/ doesn't exist yet
        if not os.path.exists(file_path) and os.path.exists("AUM_IndividualWise.xlsx"):
            file_path = "AUM_IndividualWise.xlsx"
            
        df = pd.read_excel(file_path, sheet_name="Folio Wise")
        if "AUM" in df.columns:
            df["AUM"] = pd.to_numeric(df["AUM"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data
def load_scheme_wise():
    import os
    import glob
    try:
        files = glob.glob('Data/SchemeWise_Fund_*.xls')
        if not files:
            return pd.DataFrame()
        latest_file = max(files, key=os.path.getctime)
        df = pd.read_excel(latest_file, sheet_name="Folio Wise")
        if "AUM" in df.columns:
            df["AUM"] = pd.to_numeric(df["AUM"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_all_scheme_quartiles(data_file):
    if not data_file or not os.path.exists(data_file): return pd.DataFrame()
    try:
        if data_file.endswith(".xlsx"):
            excel_file = pd.ExcelFile(data_file, engine="openpyxl")
        else:
            excel_file = pd.ExcelFile(data_file, engine="xlrd")
            
        required_periods = ["1 Month", "3 Months", "6 Months", "YTD", "1 Year", "2 Years"]
        all_schemes = []
        
        for sheet_name in excel_file.sheet_names:
            try:
                raw = pd.read_excel(data_file, sheet_name=sheet_name, header=None, engine=excel_file.engine)
                header_mask = raw.astype(str).apply(lambda x: x.str.contains("^Scheme Name$", case=False, na=False)).any(axis=1)
                if not header_mask.any(): continue
                header_row = raw[header_mask].index[0]
                
                df = pd.read_excel(data_file, sheet_name=sheet_name, header=header_row, engine=excel_file.engine)
                df.columns = df.columns.astype(str).str.strip()
                if "Scheme Name" not in df.columns: continue
                
                df = df[df["Scheme Name"].notna()]
                df = df[~df["Scheme Name"].str.contains("To view Exit", na=False)]
                
                quartile_map = {}
                percent_map = {}
                for period in required_periods:
                    matches = [c for c in df.columns if c.startswith(period)]
                    if len(matches) >= 2:
                        percent_map[period] = matches[0]
                        quartile_map[period] = matches[1]
                
                if not quartile_map: continue
                
                selected_cols = ["Scheme Name"] + list(quartile_map.values()) + list(percent_map.values())
                temp_df = df[selected_cols].copy()
                
                rename_dict = {}
                for period, col_name in quartile_map.items():
                    rename_dict[col_name] = period
                for period, col_name in percent_map.items():
                    rename_dict[col_name] = f"{period}_pct"
                    
                temp_df.rename(columns=rename_dict, inplace=True)
                
                for col in required_periods:
                    if col in temp_df.columns:
                        temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
                
                all_schemes.append(temp_df)
            except:
                continue
                
        if all_schemes:
            master_df = pd.concat(all_schemes, ignore_index=True)
            master_df = master_df.drop_duplicates(subset=["Scheme Name"])
            return master_df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()


import base64
logo_path = os.path.join("logo", "AnandWealthLogo.jpg")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f"<div style='display:flex; align-items:center; gap:12px; margin-top:15px; margin-bottom:0px;'>"
        f"<img src='data:image/jpeg;base64,{logo_b64}' style='height:45px; border-radius:6px;'/>"
        f"<h3 style='margin:0;'>Quartile Fund Analysis</h3>"
        f"</div>",
        unsafe_allow_html=True
    )
else:
    st.markdown("<h3 style='margin-top: 15px; margin-bottom: 0px;'>Quartile Fund Analysis</h3>", unsafe_allow_html=True)
  
main_tab1, main_tab2, main_tab3 = st.tabs(['Dashboard', 'Client Wise', 'Scheme Wise'])

with main_tab1:
    
    # with header_col:
    #     st.markdown("<h3 style='margin-top: 15px; margin-bottom: 0px;'>Quartile  Fund Analysis</h3>", unsafe_allow_html=True)
    
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
        padding-top: 5rem;
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
            "📊",
            data=output.getvalue(),
            file_name=f"{filename}_{today}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download Combined Excel",
            key=f"excel_{button_key}"
        )
    
    def format_df_for_export(df, required_periods):
        display_df = pd.DataFrame(index=df.index)
        display_df["Sr."] = range(1, len(df) + 1)
        display_df["Scheme Name"] = df["Scheme Name"]
        
        for period in required_periods:
            if period in df.columns:
                pct_col = f"{period}_pct"
                if pct_col in df.columns:
                    def format_cell(row, p=period, pc=pct_col):
                        q = row[p]
                        pct = row[pc]
                        if pd.isna(q): return ""
                        q_str = str(int(q)) if pd.notna(q) and q == q // 1 else str(q)
                        if pd.isna(pct): return q_str
                        
                        if isinstance(pct, (int, float)):
                            pct_str = f"{pct:.2f}"
                        else:
                            pct_str = str(pct)
                        return f"{q_str} ({pct_str})"
                    
                    display_df[period] = df.apply(format_cell, axis=1)
                else:
                    display_df[period] = df[period]
        return display_df

    def render_export_pdf(df_dict, filename, category, subcategory, button_key):
        today = datetime.date.today().strftime("%d-%b-%Y")
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=pagesizes.landscape(pagesizes.A4),
            topMargin=75, bottomMargin=20, leftMargin=30, rightMargin=30
        )
        elements = []
        styles = getSampleStyleSheet()
        
        # Header row: Logo | Company Name | Date | Category/Sub — all on one line
        logo_path = os.path.join("logo", "AnandWealthLogo.jpg")
        header_cells = []
        if os.path.exists(logo_path):
            from reportlab.platypus import Image as RLImage
            try:
                logo = RLImage(logo_path, width=80, height=35)
                header_cells.append(logo)
            except Exception:
                header_cells.append(Paragraph("", styles["Normal"]))
        else:
            header_cells.append(Paragraph("", styles["Normal"]))
        
        header_cells.append(Paragraph("<b>Quartile Fund Report</b>", styles["Heading2"]))
        header_cells.append(Paragraph(f"<b>Date:</b> {today}", styles["Normal"]))
        header_cells.append(Paragraph(f"<b>Category:</b> {category}<br/><b>Subcategory:</b> {subcategory}", styles["Normal"]))
        
        page_width = pagesizes.landscape(pagesizes.A4)[0] - 60
        header_table = Table([header_cells], colWidths=[90, page_width * 0.35, page_width * 0.2, page_width * 0.35])
        header_table.setStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ])
        
        def draw_header(canvas, document):
            canvas.saveState()
            header_table.wrapOn(canvas, page_width, 40)
            header_table.drawOn(canvas, 30, 545)
            canvas.restoreState()
            
        required_periods = ["1 Month", "3 Months", "6 Months", "YTD", "1 Year", "2 Years"]
        
        from reportlab.lib.styles import ParagraphStyle
        cell_style_left = ParagraphStyle(
            'CellClassLeftMain1',
            parent=styles['Normal'],
            fontSize=6,
            leading=7.5,
            alignment=0  # Left aligned
        )
        cell_style_center = ParagraphStyle(
            'CellClassCenterMain1',
            parent=styles['Normal'],
            fontSize=6,
            leading=7.5,
            alignment=1  # Center aligned
        )
        header_style = ParagraphStyle(
            'HeaderClassMain1',
            parent=styles['Normal'],
            fontSize=6.5,
            leading=8.5,
            textColor=colors.white,
            alignment=1  # Center aligned
        )
        
        for name, df in df_dict.items():
            if not df.empty:
                elements.append(Paragraph(f"<b>{name}</b>", styles["Heading3"]))
                elements.append(Spacer(1, 6))
                
                # Format dataframe
                formatted_df = format_df_for_export(df, required_periods)
                formatted_df = formatted_df.fillna("").astype(str).replace("nan", "").replace("None", "")
                
                # Build table data with auto-wrapping Paragraphs
                headers = [Paragraph(f"<b>{col}</b>", header_style) for col in formatted_df.columns]
                table_data = [headers]
                
                text_cols = {"Scheme Name"}
                for _, row in formatted_df.iterrows():
                    row_cells = []
                    for col in formatted_df.columns:
                        val = row[col]
                        style = cell_style_left if col in text_cols else cell_style_center
                        row_cells.append(Paragraph(val, style))
                    table_data.append(row_cells)
                
                col_names = list(formatted_df.columns)
                avail_width = pagesizes.landscape(pagesizes.A4)[0] - 72
                
                narrow_cols = {"Sr.": 20}
                period_cols = {p: 45 for p in required_periods}
                
                col_widths = []
                fixed_total = 0
                has_scheme = "Scheme Name" in col_names
                
                for c in col_names:
                    if c == "Scheme Name":
                        col_widths.append(0)
                    elif c in narrow_cols:
                        col_widths.append(narrow_cols[c])
                        fixed_total += narrow_cols[c]
                    elif c in period_cols:
                        col_widths.append(period_cols[c])
                        fixed_total += period_cols[c]
                    else:
                        col_widths.append(50)
                        fixed_total += 50
                        
                if has_scheme:
                    scheme_idx = col_names.index("Scheme Name")
                    col_widths[scheme_idx] = max(avail_width - fixed_total, 120)
                
                table = Table(table_data, colWidths=col_widths, repeatRows=1)
                table.setStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ])
                elements.append(table)
                elements.append(Spacer(1, 15))
        
        doc.build(elements, onFirstPage=draw_header, onLaterPages=draw_header)
        
        st.download_button(
            "📕",
            data=buffer.getvalue(),
            file_name=f"{filename}_{today}.pdf",
            mime="application/pdf",
            help="Download Combined PDF",
            key=f"pdf_{button_key}"
        )
    
    def render_print_button(df_dict, filename, category, subcategory):
        today = datetime.date.today().strftime("%d-%b-%Y")
        
        logo_path = os.path.join("logo", "AnandWealthLogo.jpg")
        logo_html = ""
        if os.path.exists(logo_path):
            import base64 as b64mod
            with open(logo_path, "rb") as f:
                logo_b64 = b64mod.b64encode(f.read()).decode("utf-8")
            logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="height:50px;margin-bottom:10px;">'
        
        required_periods = ["1 Month", "3 Months", "6 Months", "YTD", "1 Year", "2 Years"]
        
        tables_html = ""
        for name, df in df_dict.items():
            if not df.empty:
                # Format dataframe for printing
                formatted_df = format_df_for_export(df, required_periods)
                formatted_df = formatted_df.fillna("").astype(str).replace("nan", "").replace("None", "")
                
                tables_html += f"<h3 style='color: #1f77b4; margin-top: 20px; border-bottom: 1px solid #1f77b4; padding-bottom: 4px;'>{name}</h3>"
                tables_html += formatted_df.to_html(index=False)
                tables_html += "<br>"
                
        html = f"""
        <html><head><title>{filename}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            
            /* Repeating Page Header */
            .header {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 50px;
                display: flex;
                align-items: center;
                gap: 20px;
                border-bottom: 2px solid #1f77b4;
                background-color: white;
                padding: 5px 20px;
                z-index: 1000;
            }}
            .header h2 {{ margin: 0; color: #1f77b4; white-space: nowrap; font-size: 18px; }}
            .header span {{ color: #555; white-space: nowrap; font-size: 12px; }}
            .header-space {{
                height: 65px;
            }}
            
            /* Outer layout table to handle printing page margins & repeating spacing */
            .layout-table {{
                width: 100%;
                border-collapse: collapse;
                border: none;
            }}
            .layout-cell {{
                border: none;
                padding: 0 20px;
            }}
            
            /* Data Table style (from pandas DataFrame) */
            table.dataframe {{
                border-collapse: collapse;
                width: 100%;
                font-size: 11px;
                margin-top: 10px;
            }}
            table.dataframe th, table.dataframe td {{
                border: 1px solid #ddd;
                padding: 6px 8px;
                text-align: left;
            }}
            table.dataframe th {{
                background-color: #1f77b4;
                color: white;
            }}
            table.dataframe tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            
            thead {{
                display: table-header-group;
            }}
            tbody {{
                display: table-row-group;
            }}
            tr {{
                page-break-inside: avoid;
            }}
            @page {{
                margin: 10mm;
                size: landscape;
            }}
        </style>
        </head><body>
        
        <div class="header">
            {logo_html}
            <h2>Quartile Fund Report</h2>
            <span><b>Date:</b> {today}</span>
            <span><b>Category:</b> {category}</span>
            <span><b>Subcategory:</b> {subcategory}</span>
        </div>
        
        <table class="layout-table">
            <thead>
                <tr>
                    <td class="layout-cell"><div class="header-space">&nbsp;</div></td>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="layout-cell">
                        {tables_html}
                    </td>
                </tr>
            </tbody>
        </table>
        
        <script>
            window.onload = function() {{
                window.print();
            }}
        </script>
        </body></html>
        """
        
        b64 = base64.b64encode(html.encode('utf-8')).decode('utf-8')
        href = f"data:text/html;base64,{b64}"
        
        st.markdown(
            f"""
            <a href="{href}" target="_blank" 
            style="padding:5px 10px;border-radius:8px;border:1px solid #90caf9;background-color:#e3f2fd;color:#1e88e5;cursor:pointer;text-decoration:none;display:inline-block;height:38px;line-height:26px;text-align:center;font-size:16px;"
            title="Print">
            🖨️
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
    
    col1, col2, col3, card1, card2, card3 = st.columns([1.2, 1.2, 1.2, 0.5, 0.5, 0.5])
    
    @st.cache_data(show_spinner=False)
    def get_fund_data():
        url = "https://research-ftp.bajajcapitalinsurance.com/Fund-Barometer.xls"
        filename = os.path.join("Data", "Fund-Barometer.xls")
        os.makedirs("Data", exist_ok=True)
        
        # Check if file already downloaded today
        import datetime
        if os.path.exists(filename):
            file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filename)).date()
            if file_mtime == datetime.date.today():
                return filename
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        return filename
    
    # Auto-download AUM data if not downloaded today
    import datetime
    aum_file_path = "Data/AUM_IndividualWise.xlsx"
    aum_needs_download = True
    if os.path.exists(aum_file_path):
        aum_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(aum_file_path)).date()
        if aum_mtime == datetime.date.today():
            aum_needs_download = False
    
    if aum_needs_download:
        import autodownload
        with st.spinner("Downloading AUM Data (first load of the day)..."):
            try:
                autodownload.run()
                load_investors.clear()
            except Exception as e:
                st.error(f"AUM Auto-Download Failed: {e}")
    
    with col1:
        st.markdown("<div style='padding-top: 10px;'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📈 Fetch Fund Data", help="Fetch and update the latest mutual fund performance and quartile data from FTP server"):
                get_fund_data.clear()
        with c2:
            if st.button("💼 Fetch AUM Data", help="Fetch and update the latest client assets under management (AUM) details"):
                import autodownload
                with st.spinner("Downloading AUM Data..."):
                    try:
                        autodownload.run()
                        load_investors.clear()
                        st.success("AUM Data Updated!")
                    except Exception as e:
                        st.error(f"AUM Download Failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    data_file = None
    try:
        with st.spinner("Loading Fund Barometer..."):
            data_file = get_fund_data()
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
    
    if data_file:
        file_name = os.path.basename(data_file)
    
        if file_name.endswith(".xlsx"):
            excel_file = pd.ExcelFile(data_file, engine="openpyxl")
        elif file_name.endswith(".xls"):
            excel_file = pd.ExcelFile(data_file, engine="xlrd")
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
    
        card1_placeholder = card1.empty()
        card2_placeholder = card2.empty()
        card3_placeholder = card3.empty()
    
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
    
                raw = pd.read_excel(data_file, sheet_name=actual_sheet_name, header=None, engine=excel_file.engine)
                header_row = raw[
                    raw.astype(str)
                    .apply(lambda x: x.str.contains("^Scheme Name$", case=False, na=False))
                    .any(axis=1)
                ].index[0]
    
                df = pd.read_excel(data_file, sheet_name=actual_sheet_name, header=header_row, engine=excel_file.engine)
            df.columns = df.columns.astype(str).str.strip()
    
            df = df[df["Scheme Name"].notna()]
            df = df[~df["Scheme Name"].str.contains("To view Exit", na=False)]
    
            required_periods = ["1 Month","3 Months","6 Months","YTD","1 Year","2 Years"]
    
            quartile_map = {}
            percent_map = {}
            for period in required_periods:
                matches = [c for c in df.columns if c.startswith(period)]
                if len(matches) >= 2:
                    percent_map[period] = matches[0]
                    quartile_map[period] = matches[1]
    
            selected_cols = ["Scheme Name"] + list(quartile_map.values()) + list(percent_map.values())
            final_df = df[selected_cols].copy()
    
            rename_dict = {}
            for period, col_name in quartile_map.items():
                rename_dict[col_name] = period
            for period, col_name in percent_map.items():
                rename_dict[col_name] = f"{period}_pct"
                
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
                <div style="background:#d4edda;padding:8px 12px;border-radius:10px;text-align:center;">
                    <div style="color:#155724; font-size:12px;">✅ Good</div>
                    <div style="color:#155724; font-size:22px; font-weight:bold;">{}</div>
                </div>
                """.format(len(good_df)), unsafe_allow_html=True)
    
            with card2_placeholder:
                st.markdown("""
                <div style="background:#fff3cd;padding:8px 12px;border-radius:10px;text-align:center;">
                    <div style="color:#856404; font-size:12px;">⚖ Neutral</div>
                    <div style="color:#856404; font-size:22px; font-weight:bold;">{}</div>
                </div>
                """.format(len(neutral_df)), unsafe_allow_html=True)
    
            with card3_placeholder:
                st.markdown("""
                <div style="background:#f8d7da;padding:8px 12px;border-radius:10px;text-align:center;">
                    <div style="color:#721c24; font-size:12px;">❌ Low</div>
                    <div style="color:#721c24; font-size:22px; font-weight:bold;">{}</div>
                </div>
                """.format(len(low_df)), unsafe_allow_html=True)
    
            # -------------------------------------------------------
            # TABS
            # -------------------------------------------------------
    
            tabs_col, clients_col = st.columns([1.05, 1], gap="large")
    
            with tabs_col:
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
                left, spacer, right = st.columns([3, 3, 2])
    
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
                        render_export_pdf(master_df_dict, "Good_and_Low_Performing", selected_category, selected_sub, key)
    
                    with btn2:
                        render_export_excel(master_df_dict, "Good_and_Low_Performing", selected_category, selected_sub, key)
    
                    with btn3:
                        render_print_button(master_df_dict, "Good_and_Low_Performing", selected_category, selected_sub)
    
                # ---------------------------
                # Apply Search
                if search:
                    df_data = df_data[
                        df_data["Scheme Name"].str.contains(search, case=False, na=False)
                    ]
    
                display_df = pd.DataFrame(index=df_data.index)
                display_df["Sr."] = range(1, len(df_data) + 1)
                display_df["Scheme Name"] = df_data["Scheme Name"]
                
                for period in required_periods:
                    if period in df_data.columns:
                        pct_col = f"{period}_pct"
                        if pct_col in df_data.columns:
                            def format_cell(row, p=period, pc=pct_col):
                                q = row[p]
                                pct = row[pc]
                                if pd.isna(q): return ""
                                q_str = str(int(q)) if pd.notna(q) and q == q // 1 else str(q)
                                if pd.isna(pct): return q_str
                                
                                if isinstance(pct, (int, float)):
                                    pct_str = f"{pct:.2f}"
                                else:
                                    pct_str = str(pct)
                                return f"{q_str} ({pct_str})"
                            
                            display_df[period] = df_data.apply(format_cell, axis=1)
                        else:
                            display_df[period] = df_data[period]
    
                def color_cells(val):
                    if isinstance(val, str) and '(' in val and ')' in val:
                        try:
                            p_str = val.split('(')[1].split(')')[0]
                            p_str = p_str.replace('%', '').strip()
                            p_val = float(p_str)
                            if p_val > 0:
                                return 'color: green;'
                            elif p_val < 0:
                                return 'color: red;'
                        except:
                            pass
                    return ''
    
                if hasattr(display_df.style, 'map'):
                    styled_df = display_df.style.map(color_cells, subset=[c for c in required_periods if c in display_df.columns])
                else:
                    styled_df = display_df.style.applymap(color_cells, subset=[c for c in required_periods if c in display_df.columns])
    
                event = st.dataframe(
                    styled_df, 
                    use_container_width=False, 
                    hide_index=True, 
                    height=400,
                    on_select="rerun",
                    selection_mode="single-row",
                    key=f"grid_{key}",
                    column_config={
                        "Sr.": st.column_config.NumberColumn("Sr.", format="%d", width=15),
                        "Scheme Name": st.column_config.TextColumn("Scheme Name", width="medium")
                    }
                )
    
                if len(event.selection.rows) > 0:
                    selected_idx = event.selection.rows[0]
                    return display_df.iloc[selected_idx]["Scheme Name"]
                return None
    
            # -------------------------------------------------------
            # RENDER TABS
            # -------------------------------------------------------
    
            with tabs_col:
                with tab1:
                    sel_good = render_tab(good_df, "Good_Performing", "good")
    
                with tab2:
                    sel_neutral = render_tab(neutral_df, "Neutral", "neutral")
    
                with tab3:
                    sel_low = render_tab(low_df, "Low_Performing", "low")
    
            if "last_fund" not in st.session_state:
                st.session_state.last_fund = None
            if "fund_selections" not in st.session_state:
                st.session_state.fund_selections = {"good": None, "neutral": None, "low": None}
    
            current_selections = {"good": sel_good, "neutral": sel_neutral, "low": sel_low}
            
            for k, v in current_selections.items():
                if v != st.session_state.fund_selections.get(k):
                    st.session_state.last_fund = v
                    st.session_state.fund_selections[k] = v
    
            selected_fund = st.session_state.last_fund
    
            with clients_col:
                if selected_fund:
                    st.markdown(f"#### Clients holding: **{selected_fund}**")
                    
                    investor_df = load_investors()
                    if not investor_df.empty and "Scheme Name" in investor_df.columns:
                        matched_clients = investor_df[investor_df["Scheme Name"].astype(str).str.strip().str.lower() == str(selected_fund).strip().lower()]
                        if not matched_clients.empty:
                            cols_to_show = ["Client Name", "Folio",  "ARN No","AUM"]
                            cols_to_show = [c for c in cols_to_show if c in matched_clients.columns]
                            
                            display_df = matched_clients[cols_to_show].copy() if cols_to_show else matched_clients.copy()
                            
                            display_df.insert(0, "Sr.", range(1, len(display_df) + 1))
                            
                            if "AUM" in display_df.columns:
                                total_aum = display_df["AUM"].sum()
                                total_row = {col: "" for col in display_df.columns}
                                if "Client Name" in display_df.columns:
                                    total_row["Client Name"] = "TOTAL"
                                elif len(display_df.columns) > 0:
                                    total_row[display_df.columns[0]] = "TOTAL"
                                total_row["AUM"] = total_aum
                                total_row["Sr."] = None
                                
                                display_df = pd.concat([display_df, pd.DataFrame([total_row])], ignore_index=True)
                                
                            def highlight_total(row):
                                if row.get("Client Name", "") == "TOTAL" or (len(display_df.columns) > 0 and row.get(display_df.columns[0], "") == "TOTAL"):
                                    return ['background-color: rgba(255, 255, 255, 0.1); font-weight: bold; color: #4CAF50'] * len(row)
                                return [''] * len(row)
    
                            styled_display_df = display_df.style.apply(highlight_total, axis=1)
                            st.dataframe(
                                styled_display_df, 
                                use_container_width=True, 
                                hide_index=True,
                                height=600,
                                column_config={
                                    "Sr.": st.column_config.NumberColumn("Sr.", format="%d", width=15),
                                    "Client Name": st.column_config.TextColumn("Client Name", width="medium"),
                                    "AUM": st.column_config.NumberColumn("AUM", format="%,.2f")
                                }
                            )
                        else:
                            st.info("No clients found holding this fund.")
                    else:
                        st.warning("Could not load investor data or 'Scheme Name' column missing.")
                else:
                    st.markdown("<div style='margin-top: 50px; text-align: center; color: gray;'>Select a fund from the tables to view clients.</div>", unsafe_allow_html=True)
with main_tab2:
    #st.markdown("### Client Wise Details")
    investor_df = load_investors()
    if not investor_df.empty and "Client Name" in investor_df.columns:
        client_names = sorted(investor_df["Client Name"].dropna().unique().tolist())
        
        # --- Client-wise export helper functions ---
        def client_export_excel(display_data, client_name, button_key):
            today = datetime.date.today().strftime("%d-%b-%Y")
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Clean data for export
                export_df = display_data.copy()
                if "AUM" in export_df.columns:
                    export_df["AUM"] = export_df["AUM"].apply(lambda x: f"{x:,.2f}" if pd.notna(x) and x != "" else "")
                if "Sr." in export_df.columns:
                    export_df["Sr."] = export_df["Sr."].apply(lambda x: str(int(x)) if pd.notna(x) and x != "" else "")
                export_df = export_df.fillna("").astype(str).replace("nan", "").replace("None", "")
                export_df.to_excel(writer, index=False, startrow=3, sheet_name='Client Report')
                ws = writer.sheets['Client Report']
                
                # Insert logo
                logo_path = os.path.join("logo", "AnandWealthLogo.jpg")
                if os.path.exists(logo_path):
                    from openpyxl.drawing.image import Image as XlImage
                    img = XlImage(logo_path)
                    img.width = 80
                    img.height = 35
                    ws.add_image(img, 'A1')
                
                ws.cell(row=1, column=3, value="Quartile Fund Report")
                ws.cell(row=1, column=5, value=f"Date: {today}")
                ws.cell(row=1, column=7, value=f"Client: {client_name}")
            
            st.download_button(
                "📊",
                data=output.getvalue(),
                file_name=f"Client_{client_name}_{today}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download Excel",
                key=f"client_excel_{button_key}"
            )
        
        def client_export_pdf(display_data, client_name, button_key):
            today = datetime.date.today().strftime("%d-%b-%Y")
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer, pagesize=pagesizes.landscape(pagesizes.A4),
                topMargin=75, bottomMargin=20, leftMargin=30, rightMargin=30
            )
            elements = []
            styles = getSampleStyleSheet()
            
            # Header row: Logo | Company Name | Date | Client — all on one line
            logo_path = os.path.join("logo", "AnandWealthLogo.jpg")
            header_cells = []
            if os.path.exists(logo_path):
                from reportlab.platypus import Image as RLImage
                try:
                    logo = RLImage(logo_path, width=80, height=35)
                    header_cells.append(logo)
                except Exception:
                    header_cells.append(Paragraph("", styles["Normal"]))
            else:
                header_cells.append(Paragraph("", styles["Normal"]))
            
            header_cells.append(Paragraph("<b>Quartile Fund Report</b>", styles["Heading2"]))
            header_cells.append(Paragraph(f"<b>Date:</b> {today}", styles["Normal"]))
            header_cells.append(Paragraph(f"<b>Client:</b> {client_name}", styles["Normal"]))
            
            page_width = pagesizes.landscape(pagesizes.A4)[0] - 60
            header_table = Table([header_cells], colWidths=[90, page_width * 0.4, page_width * 0.2, page_width * 0.3])
            header_table.setStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ])
            
            def draw_header(canvas, document):
                canvas.saveState()
                header_table.wrapOn(canvas, page_width, 40)
                header_table.drawOn(canvas, 30, 545)
                canvas.restoreState()
            
            if not display_data.empty:
                from reportlab.lib.styles import ParagraphStyle
                # Prepare data: format AUM with commas, replace None/nan with blank
                pdf_df = display_data.copy()
                if "AUM" in pdf_df.columns:
                    pdf_df["AUM"] = pdf_df["AUM"].apply(lambda x: f"{x:,.2f}" if pd.notna(x) and x != "" else "")
                if "Sr." in pdf_df.columns:
                    pdf_df["Sr."] = pdf_df["Sr."].apply(lambda x: str(int(x)) if pd.notna(x) and x != "" else "")
                pdf_df = pdf_df.fillna("").astype(str).replace("nan", "").replace("None", "")
                
                # Define paragraph styles for auto-wrapping inside table cells
                cell_style_left = ParagraphStyle(
                    'CellClassLeftClient',
                    parent=styles['Normal'],
                    fontSize=6,
                    leading=7.5,
                    alignment=0  # Left aligned
                )
                cell_style_center = ParagraphStyle(
                    'CellClassCenterClient',
                    parent=styles['Normal'],
                    fontSize=6,
                    leading=7.5,
                    alignment=1  # Center aligned
                )
                header_style = ParagraphStyle(
                    'HeaderClassClient',
                    parent=styles['Normal'],
                    fontSize=6.5,
                    leading=8.5,
                    textColor=colors.white,
                    alignment=1  # Center aligned
                )
                
                # Build table data with auto-wrapping Paragraphs for all columns
                headers = [Paragraph(f"<b>{col}</b>", header_style) for col in pdf_df.columns]
                table_data = [headers]
                
                text_cols = {"Scheme Name"}
                for _, row in pdf_df.iterrows():
                    row_cells = []
                    for col in pdf_df.columns:
                        val = row[col]
                        style = cell_style_left if col in text_cols else cell_style_center
                        row_cells.append(Paragraph(val, style))
                    table_data.append(row_cells)
                
                # Smart column widths: explicit sizes per column type
                n_cols = len(pdf_df.columns)
                avail_width = pagesizes.landscape(pagesizes.A4)[0] - 72
                col_names = list(pdf_df.columns)
                
                # Define explicit widths for known columns
                narrow_cols = {"Sr.": 20, "XIRR": 42}
                period_cols = {"1 Month": 42, "3 Months": 42, "6 Months": 42, "YTD": 42, "1 Year": 42, "2 Years": 42}
                medium_cols = {"Folio": 55, "ARN No": 55, "AUM": 55}
                
                col_widths = []
                fixed_total = 0
                has_scheme = "Scheme Name" in col_names
                
                for c in col_names:
                    if c == "Scheme Name":
                        col_widths.append(0)  # placeholder, calculated below
                    elif c in narrow_cols:
                        col_widths.append(narrow_cols[c])
                        fixed_total += narrow_cols[c]
                    elif c in period_cols:
                        col_widths.append(period_cols[c])
                        fixed_total += period_cols[c]
                    elif c in medium_cols:
                        col_widths.append(medium_cols[c])
                        fixed_total += medium_cols[c]
                    else:
                        col_widths.append(50)
                        fixed_total += 50
                
                # Give Scheme Name all remaining width
                if has_scheme:
                    scheme_idx = col_names.index("Scheme Name")
                    col_widths[scheme_idx] = max(avail_width - fixed_total, 120)
                
                table = Table(table_data, colWidths=col_widths, repeatRows=1)
                table.setStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ])
                elements.append(table)
            
            doc.build(elements, onFirstPage=draw_header, onLaterPages=draw_header)
            
            st.download_button(
                "📕",
                data=buffer.getvalue(),
                file_name=f"Client_{client_name}_{today}.pdf",
                mime="application/pdf",
                help="Download PDF",
                key=f"client_pdf_{button_key}"
            )
        
        def client_print_button(display_data, client_name, button_key):
            today = datetime.date.today().strftime("%d-%b-%Y")
            
            logo_path = os.path.join("logo", "AnandWealthLogo.jpg")
            logo_html = ""
            if os.path.exists(logo_path):
                import base64 as b64mod
                with open(logo_path, "rb") as f:
                    logo_b64 = b64mod.b64encode(f.read()).decode("utf-8")
                logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="height:50px;margin-bottom:10px;">'
            
            # Clean data for print: format AUM, remove None
            print_df = display_data.copy()
            if "AUM" in print_df.columns:
                print_df["AUM"] = print_df["AUM"].apply(lambda x: f"{x:,.2f}" if pd.notna(x) and x != "" else "")
            if "Sr." in print_df.columns:
                print_df["Sr."] = print_df["Sr."].apply(lambda x: str(int(x)) if pd.notna(x) and x != "" else "")
            print_df = print_df.fillna("").astype(str).replace("nan", "").replace("None", "")
            
            table_html = print_df.to_html(index=False) if not print_df.empty else ""
            
            html = f"""
            <html><head><title>Client Report - {client_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                
                /* Repeating Page Header */
                .header {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 50px;
                    display: flex;
                    align-items: center;
                    gap: 20px;
                    border-bottom: 2px solid #1f77b4;
                    background-color: white;
                    padding: 5px 20px;
                    z-index: 1000;
                }}
                .header h2 {{ margin: 0; color: #1f77b4; white-space: nowrap; }}
                .header span {{ color: #555; white-space: nowrap; font-size: 14px; }}
                .header-space {{
                    height: 65px;
                }}
                
                /* Outer layout table to handle printing page margins & repeating spacing */
                .layout-table {{
                    width: 100%;
                    border-collapse: collapse;
                    border: none;
                }}
                .layout-cell {{
                    border: none;
                    padding: 0 20px;
                }}
                
                /* Data Table style (from pandas DataFrame) */
                table.dataframe {{
                    border-collapse: collapse;
                    width: 100%;
                    font-size: 12px;
                    margin-top: 10px;
                }}
                table.dataframe th, table.dataframe td {{
                    border: 1px solid #ddd;
                    padding: 6px 8px;
                    text-align: left;
                }}
                table.dataframe th {{
                    background-color: #1f77b4;
                    color: white;
                }}
                table.dataframe tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                
                /* Instruct browser to repeat table headers and avoid orphan rows */
                thead {{
                    display: table-header-group;
                }}
                tbody {{
                    display: table-row-group;
                }}
                tr {{
                    page-break-inside: avoid;
                }}
                @page {{
                    margin: 10mm;
                    size: landscape;
                }}
            </style>
            </head><body>
            
            <div class="header">
                {logo_html}
                <h2>Quartile Fund Report</h2>
                <span><b>Date:</b> {today}</span>
                <span><b>Client:</b> {client_name}</span>
            </div>
            
            <table class="layout-table">
                <thead>
                    <tr>
                        <td class="layout-cell"><div class="header-space">&nbsp;</div></td>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="layout-cell">
                            {table_html}
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <script>
                window.onload = function() {{
                    window.print();
                }}
            </script>
            </body></html>
            """
            
            b64_data = base64.b64encode(html.encode('utf-8')).decode('utf-8')
            href = f"data:text/html;base64,{b64_data}"
            
            st.markdown(
                f"""
                <a href="{href}" target="_blank" 
                style="padding:5px 10px;border-radius:8px;border:1px solid #90caf9;background-color:#e3f2fd;color:#1e88e5;cursor:pointer;text-decoration:none;display:inline-block;height:38px;line-height:26px;text-align:center;font-size:16px;"
                title="Print">
                🖨️
                </a>
                """,
                unsafe_allow_html=True
            )
        
        # --- Layout: Selectbox + Export buttons ---
        sel_col, btn_pdf_col, btn_excel_col, btn_print_col = st.columns([4, 0.3, 0.3, 0.3])
        with sel_col:
            selected_client = st.selectbox("Select Client", ["Select"] + client_names)
        if selected_client != "Select":
            client_data = investor_df[investor_df["Client Name"] == selected_client]
            
            master_q_df = pd.DataFrame()
            if 'data_file' in globals() and data_file:
                with st.spinner("Loading quartile data for all schemes..."):
                    master_q_df = load_all_scheme_quartiles(data_file)
            
            if not master_q_df.empty:
                master_q_df["_match_name"] = master_q_df["Scheme Name"].astype(str).str.strip().str.lower()
                client_data["_match_name"] = client_data["Scheme Name"].astype(str).str.strip().str.lower()
                client_data = pd.merge(client_data, master_q_df.drop(columns=["Scheme Name"]), on="_match_name", how="left")
                client_data.drop(columns=["_match_name"], inplace=True)
            
            cols_to_show = ["Scheme Name", "Folio",  "ARN No","AUM"]
            required_periods = ["1 Month", "3 Months", "6 Months",  "YTD", "1 Year", "2 Years"]
            
            if not master_q_df.empty:
                cols_to_show.extend([p for p in required_periods if p in client_data.columns])
                
            cols_to_show = [c for c in cols_to_show if c in client_data.columns]
            
            display_df = client_data[cols_to_show].copy() if cols_to_show else client_data.copy()
            
            safe_name = "".join([c if c.isalnum() else "_" for c in selected_client])
            client_file_path = os.path.join("Data", f"Portfolio_{safe_name}.xls")
            
            needs_download = True
            if os.path.exists(client_file_path):
                import datetime
                file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(client_file_path)).date()
                if file_mtime == datetime.date.today():
                    needs_download = False
            
            if needs_download:
                import autodownload
                with st.spinner(f"Downloading latest Portfolio for {selected_client}..."):
                    try:
                        autodownload.download_client_portfolio(selected_client)
                    except Exception as e:
                        st.error(f"Failed to download portfolio: {e}")
            
            if os.path.exists(client_file_path):
                
                
                try:
                    # Try openpyxl first, fall back to xlrd for genuine .xls files
                    try:
                        port_df = pd.read_excel(client_file_path, engine="openpyxl", header=4)
                    except Exception:
                        port_df = pd.read_excel(client_file_path, engine="xlrd", header=4)
                    
                    if "Scheme Name" in port_df.columns and "XIRR" in port_df.columns:
                        port_df["_match_name"] = port_df["Scheme Name"].astype(str).str.strip().str.lower()
                        display_df["_match_name"] = display_df["Scheme Name"].astype(str).str.strip().str.lower()
                        
                        port_df_clean = port_df.dropna(subset=["XIRR"]).drop_duplicates(subset=["_match_name"])
                        display_df = pd.merge(display_df, port_df_clean[["_match_name", "XIRR"]], on="_match_name", how="left")
                        display_df.drop(columns=["_match_name"], inplace=True)
                        display_df["XIRR"] = pd.to_numeric(display_df["XIRR"], errors="coerce")
                        
                        # Reorder columns to put XIRR before AUM
                        cols = list(display_df.columns)
                        print(cols)
                        # # Ensure XIRR exists and is before AUM
                        # if "XIRR" in display_df.columns:
                        #     cols = list(display_df.columns)
                        #     cols.remove("XIRR")
                            
                        #     if "AUM" in cols:
                        #         aum_index = cols.index("AUM")
                        #         cols.insert(aum_index, "XIRR")
                        #     else:
                        #         cols.append("XIRR")
                            
                        #     display_df = display_df[cols]
                    else:
                        st.warning(f"Portfolio file loaded but missing columns. Found: {list(port_df.columns[:8])}")
                except Exception as e:
                    st.warning(f"Could not read portfolio file: {e}")
            
            if not master_q_df.empty:
                for period in required_periods:
                    if period in client_data.columns:
                        pct_col = f"{period}_pct"
                        if pct_col in client_data.columns:
                            def format_cell(row, p=period, pc=pct_col):
                                q = row.get(p)
                                pct = row.get(pc)
                                if pd.isna(q): return ""
                                q_str = str(int(q)) if pd.notna(q) and q == q // 1 else str(q)
                                if pd.isna(pct): return q_str
                                
                                if isinstance(pct, (int, float)):
                                    pct_str = f"{pct:.2f}"
                                else:
                                    pct_str = str(pct)
                                return f"{q_str} ({pct_str})"
                            
                            display_df[period] = client_data.apply(format_cell, axis=1).values
            
            display_df.sort_values(by="Scheme Name", inplace=True, ignore_index=True)
            display_df.insert(0, "Sr.", range(1, len(display_df) + 1))
            
            if "AUM" in display_df.columns:
                total_aum = display_df["AUM"].sum()
                total_row = {col: "" for col in display_df.columns}
                if "Scheme Name" in display_df.columns:
                    total_row["Scheme Name"] = "TOTAL"
                elif len(display_df.columns) > 0:
                    total_row[display_df.columns[0]] = "TOTAL"
                total_row["AUM"] = total_aum
                total_row["Sr."] = ""
                
                display_df = pd.concat([display_df, pd.DataFrame([total_row])], ignore_index=True)
                
            def highlight_and_color(row):
                if row.get("Scheme Name", "") == "TOTAL" or (len(display_df.columns) > 0 and row.get(display_df.columns[0], "") == "TOTAL"):
                    return ['background-color: rgba(255, 255, 255, 0.1); font-weight: bold; color: #4CAF50'] * len(row)
                
                styles = [''] * len(row)
                for i, col in enumerate(display_df.columns):
                    val = row.get(col)
                    if isinstance(val, str) and '(' in val and ')' in val and col in required_periods:
                        try:
                            # The string is "Q_val (Pct_val)", extract the Quartile (Q_val)
                            q_str = val.split('(')[0].strip()
                            q_val = int(float(q_str))
                            if q_val == 1:
                                styles[i] = 'color: green;'
                            elif q_val in [3, 4]:
                                styles[i] = 'color: red;'
                        except:
                            pass
                    elif col == "XIRR" and pd.notna(val):
                        try:
                            if float(val) > 0:
                                styles[i] = 'color: green;'
                            elif float(val) < 0:
                                styles[i] = 'color: red;'
                        except:
                            pass
                return styles

            # Ensure XIRR exists and is before AUM
            if "XIRR" in display_df.columns:
                cols = list(display_df.columns)
                cols.remove("XIRR")
                
                if "AUM" in cols:
                    aum_index = cols.index("AUM")
                    cols.insert(aum_index, "XIRR")
                else:
                    cols.append("XIRR")
                
                display_df = display_df[cols]

            styled_display_df = display_df.style.apply(highlight_and_color, axis=1)
            
            # Render export buttons (use columns defined earlier)
            with btn_excel_col:
                st.markdown("<div style='padding-top: 28px;'>", unsafe_allow_html=True)
                client_export_excel(display_df, selected_client, "tab2")
                st.markdown("</div>", unsafe_allow_html=True)
            with btn_pdf_col:
                st.markdown("<div style='padding-top: 28px;'>", unsafe_allow_html=True)
                client_export_pdf(display_df, selected_client, "tab2")
                st.markdown("</div>", unsafe_allow_html=True)
            with btn_print_col:
                st.markdown("<div style='padding-top: 28px;'>", unsafe_allow_html=True)
                client_print_button(display_df, selected_client, "tab2")
                st.markdown("</div>", unsafe_allow_html=True)
            
            client_tab1, client_tab2 = st.tabs(["Client Details", "Quartile Report"])
            
            with client_tab1:
                st.dataframe(
                    styled_display_df, 
                    use_container_width=True, 
                    hide_index=True,
                    height=600,
                    column_config={
                        "Sr.": st.column_config.NumberColumn("Sr.", format="%d", width=15),
                        "Scheme Name": st.column_config.TextColumn("Scheme Name", width="medium"),
                        "XIRR": st.column_config.NumberColumn("XIRR (%)", format="%.2f"),
                        "AUM": st.column_config.NumberColumn("AUM", format="%,.2f")
                    }
                )
            
            with client_tab2:
                st.markdown("#### 📊 Performance Visualizations")
                
                if not master_q_df.empty:
                    avail_periods = [p for p in required_periods if p in client_data.columns]
                    avail_pcts = [f"{p}_pct" for p in avail_periods if f"{p}_pct" in client_data.columns]
                    
                    if avail_periods:
                        import plotly.express as px
                        import plotly.graph_objects as go
                        
                        chart_col1, chart_col2 = st.columns(2)
                        
                        with chart_col1:
                            st.markdown("##### Quartile Heatmap")
                            st.markdown("<small style='color:gray;'>Green = Q1 (Best), Red = Q4 (Worst)</small>", unsafe_allow_html=True)
                            
                            heatmap_df = client_data[["Scheme Name"] + avail_periods].copy()
                            heatmap_df = heatmap_df.drop_duplicates(subset=["Scheme Name"]).set_index("Scheme Name")
                            
                            fig_heat = go.Figure(data=go.Heatmap(
                                z=heatmap_df.values,
                                x=heatmap_df.columns,
                                y=heatmap_df.index,
                                colorscale=[[0, '#4CAF50'], [0.33, '#8BC34A'], [0.66, '#FFC107'], [1, '#F44336']], 
                                zmin=1, zmax=4,
                                text=heatmap_df.values,
                                texttemplate="%{text}",
                                hoverinfo="x+y+z",
                                showscale=False,
                                xgap=2, ygap=2
                            ))
                            fig_heat.update_layout(
                                margin=dict(l=0, r=0, t=10, b=0),
                                height=max(250, len(heatmap_df) * 45),
                                xaxis_title="",
                                yaxis_title="",
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)"
                            )
                            st.plotly_chart(fig_heat, use_container_width=True)
                        
                        with chart_col2:
                            if avail_pcts:
                                st.markdown("##### Absolute Returns (%)")
                                st.markdown("<small style='color:gray;'>Period-wise percentage returns</small>", unsafe_allow_html=True)
                                
                                pct_df = client_data[["Scheme Name"] + avail_pcts].copy()
                                pct_df = pct_df.drop_duplicates(subset=["Scheme Name"]).set_index("Scheme Name")
                                pct_df.columns = [c.replace('_pct', '') for c in pct_df.columns]
                                
                                pct_melt = pct_df.reset_index().melt(id_vars="Scheme Name", var_name="Period", value_name="Return (%)")
                                
                                fig_bar = px.bar(
                                    pct_melt, 
                                    x="Period", y="Return (%)", color="Scheme Name", barmode="group",
                                    text_auto='.1f'
                                )
                                fig_bar.update_layout(
                                    xaxis_title="", yaxis_title="Returns (%)",
                                    margin=dict(l=0, r=0, t=10, b=0),
                                    height=max(250, len(heatmap_df) * 45),
                                    legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(0,0,0,0)"
                                )
                                st.plotly_chart(fig_bar, use_container_width=True)
                            else:
                                st.info("No percentage return data available.")
                        
                    else:
                        st.info("No quartile data found for these schemes.")
                else:
                    st.info("Master fund barometer data not available for chart.")
    else:
        st.warning("Client data not available.")

with main_tab3:
    # --- Scheme-wise export helper functions ---
    def scheme_export_excel(display_data, filter_text, button_key):
        today = datetime.date.today().strftime("%d-%b-%Y")
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Clean data for export
            export_df = display_data.copy()
            if "AUM" in export_df.columns:
                export_df["AUM"] = export_df["AUM"].apply(lambda x: f"{x:,.2f}" if pd.notna(x) and x != "" else "")
            if "Sr." in export_df.columns:
                export_df["Sr."] = export_df["Sr."].apply(lambda x: str(int(x)) if pd.notna(x) and x != "" else "")
            export_df = export_df.fillna("").astype(str).replace("nan", "").replace("None", "")
            export_df.to_excel(writer, index=False, startrow=3, sheet_name='Scheme Report')
            ws = writer.sheets['Scheme Report']
            
            # Right align AUM column dynamically
            if "AUM" in export_df.columns:
                aum_col_idx = list(export_df.columns).index("AUM") + 1
                from openpyxl.styles import Alignment
                for r in range(4, ws.max_row + 1):
                    ws.cell(row=r, column=aum_col_idx).alignment = Alignment(horizontal='right')
            
            # Insert logo
            logo_path = os.path.join("logo", "AnandWealthLogo.jpg")
            if os.path.exists(logo_path):
                from openpyxl.drawing.image import Image as XlImage
                img = XlImage(logo_path)
                img.width = 80
                img.height = 35
                ws.add_image(img, 'A1')
            
            ws.cell(row=1, column=3, value="Quartile Fund Report (Scheme Wise)")
            ws.cell(row=1, column=5, value=f"Date: {today}")
            ws.cell(row=1, column=7, value=f"Filters: {filter_text}")
        
        st.download_button(
            "📊",
            data=output.getvalue(),
            file_name=f"SchemeWise_{today}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download Excel",
            key=f"scheme_excel_{button_key}"
        )
    
    def scheme_export_pdf(display_data, filter_text, button_key):
        today = datetime.date.today().strftime("%d-%b-%Y")
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=pagesizes.landscape(pagesizes.A4),
            topMargin=75, bottomMargin=20, leftMargin=30, rightMargin=30
        )
        elements = []
        styles = getSampleStyleSheet()
        
        # Header row: Logo | Company Name | Date | Filters — all on one line
        logo_path = os.path.join("logo", "AnandWealthLogo.jpg")
        header_cells = []
        if os.path.exists(logo_path):
            from reportlab.platypus import Image as RLImage
            try:
                logo = RLImage(logo_path, width=80, height=35)
                header_cells.append(logo)
            except Exception:
                header_cells.append(Paragraph("", styles["Normal"]))
        else:
            header_cells.append(Paragraph("", styles["Normal"]))
        
        header_cells.append(Paragraph("<b>Quartile Fund Report (Scheme Wise)</b>", styles["Heading2"]))
        header_cells.append(Paragraph(f"<b>Date:</b> {today}", styles["Normal"]))
        
        from reportlab.lib.styles import ParagraphStyle
        filter_style = ParagraphStyle(
            'FilterStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=10
        )
        header_cells.append(Paragraph(f"<b>Active Filters:</b><br/>{filter_text}", filter_style))
        
        page_width = pagesizes.landscape(pagesizes.A4)[0] - 60
        header_table = Table([header_cells], colWidths=[90, page_width * 0.35, page_width * 0.15, page_width * 0.4])
        header_table.setStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ])
        
        def draw_header(canvas, document):
            canvas.saveState()
            header_table.wrapOn(canvas, page_width, 40)
            header_table.drawOn(canvas, 30, 545)
            canvas.restoreState()
        
        if not display_data.empty:
            from reportlab.lib.units import inch
            
            # Prepare data: format AUM with commas, replace None/nan with blank
            pdf_df = display_data.copy()
            if "AUM" in pdf_df.columns:
                pdf_df["AUM"] = pdf_df["AUM"].apply(lambda x: f"{x:,.2f}" if pd.notna(x) and x != "" else "")
            if "Sr." in pdf_df.columns:
                pdf_df["Sr."] = pdf_df["Sr."].apply(lambda x: str(int(x)) if pd.notna(x) and x != "" else "")
            pdf_df = pdf_df.fillna("").astype(str).replace("nan", "").replace("None", "")
            
            # Define paragraph styles for auto-wrapping inside table cells
            cell_style_left = ParagraphStyle(
                'CellClassLeft',
                parent=styles['Normal'],
                fontSize=6,
                leading=7.5,
                alignment=0  # Left aligned
            )
            cell_style_center = ParagraphStyle(
                'CellClassCenter',
                parent=styles['Normal'],
                fontSize=6,
                leading=7.5,
                alignment=1  # Center aligned
            )
            cell_style_right = ParagraphStyle(
                'CellClassRight',
                parent=styles['Normal'],
                fontSize=6,
                leading=7.5,
                alignment=2  # Right aligned
            )
            header_style_center = ParagraphStyle(
                'HeaderClassCenter',
                parent=styles['Normal'],
                fontSize=6.5,
                leading=8.5,
                textColor=colors.white,
                alignment=1  # Center aligned
            )
            header_style_right = ParagraphStyle(
                'HeaderClassRight',
                parent=styles['Normal'],
                fontSize=6.5,
                leading=8.5,
                textColor=colors.white,
                alignment=2  # Right aligned
            )
            
            # Build table data with auto-wrapping Paragraphs for all columns
            headers = []
            for col in pdf_df.columns:
                style = header_style_right if col == "AUM" else header_style_center
                headers.append(Paragraph(f"<b>{col}</b>", style))
            table_data = [headers]
            
            text_cols = {"Category Name", "Sector", "Scheme Name"}
            for _, row in pdf_df.iterrows():
                row_cells = []
                for col in pdf_df.columns:
                    val = row[col]
                    if col in text_cols:
                        style = cell_style_left
                    elif col == "AUM":
                        style = cell_style_right
                    else:
                        style = cell_style_center
                    row_cells.append(Paragraph(val, style))
                table_data.append(row_cells)
            
            # Smart column widths: explicit sizes per column type
            n_cols = len(pdf_df.columns)
            avail_width = pagesizes.landscape(pagesizes.A4)[0] - 72
            col_names = list(pdf_df.columns)
            
            # Define explicit widths for known columns
            narrow_cols = {"Sr.": 25, "XIRR": 42}
            period_cols = {"1 Month": 42, "3 Months": 42, "6 Months": 42, "YTD": 42, "1 Year": 42, "2 Years": 42}
            medium_cols = {"Category Name": 45, "Sector": 147, "AUM": 55}
            
            col_widths = []
            fixed_total = 0
            has_scheme = "Scheme Name" in col_names
            
            for c in col_names:
                if c == "Scheme Name":
                    col_widths.append(0)  # placeholder, calculated below
                elif c in narrow_cols:
                    col_widths.append(narrow_cols[c])
                    fixed_total += narrow_cols[c]
                elif c in period_cols:
                    col_widths.append(period_cols[c])
                    fixed_total += period_cols[c]
                elif c in medium_cols:
                    col_widths.append(medium_cols[c])
                    fixed_total += medium_cols[c]
                else:
                    col_widths.append(50)
                    fixed_total += 50
            
            # Give Scheme Name all remaining width
            if has_scheme:
                scheme_idx = col_names.index("Scheme Name")
                col_widths[scheme_idx] = max(avail_width - fixed_total, 120)
            
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ])
            elements.append(table)
        
        doc.build(elements, onFirstPage=draw_header, onLaterPages=draw_header)
        
        st.download_button(
            "📕",
            data=buffer.getvalue(),
            file_name=f"SchemeWise_{today}.pdf",
            mime="application/pdf",
            help="Download PDF",
            key=f"scheme_pdf_{button_key}"
        )
    
    def scheme_print_button(display_data, filter_text, button_key):
        today = datetime.date.today().strftime("%d-%b-%Y")
        
        logo_path = os.path.join("logo", "AnandWealthLogo.jpg")
        logo_html = ""
        if os.path.exists(logo_path):
            import base64 as b64mod
            with open(logo_path, "rb") as f:
                logo_b64 = b64mod.b64encode(f.read()).decode("utf-8")
            logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="height:50px;margin-bottom:10px;">'
        
        # Clean data for print
        print_df = display_data.copy()
        if "AUM" in print_df.columns:
            print_df["AUM"] = print_df["AUM"].apply(lambda x: f"{x:,.2f}" if pd.notna(x) and x != "" else "")
        if "Sr." in print_df.columns:
            print_df["Sr."] = print_df["Sr."].apply(lambda x: str(int(x)) if pd.notna(x) and x != "" else "")
        print_df = print_df.fillna("").astype(str).replace("nan", "").replace("None", "")
        
        table_html = print_df.to_html(index=False) if not print_df.empty else ""
        
        html = f"""
        <html><head><title>Scheme Summary Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            
            /* Repeating Page Header */
            .header {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 50px;
                display: flex;
                align-items: center;
                gap: 20px;
                border-bottom: 2px solid #1f77b4;
                background-color: white;
                padding: 5px 20px;
                z-index: 1000;
            }}
            .header h2 {{ margin: 0; color: #1f77b4; white-space: nowrap; }}
            .header span {{ color: #555; white-space: nowrap; font-size: 14px; }}
            .header-space {{
                height: 65px;
            }}
            
            /* Outer layout table to handle printing page margins & repeating spacing */
            .layout-table {{
                width: 100%;
                border-collapse: collapse;
                border: none;
            }}
            .layout-cell {{
                border: none;
                padding: 0 20px;
            }}
            
            /* Data Table style */
            table.dataframe {{
                border-collapse: collapse;
                width: 100%;
                font-size: 12px;
                margin-top: 10px;
            }}
            table.dataframe th, table.dataframe td {{
                border: 1px solid #ddd;
                padding: 6px 8px;
                text-align: left;
            }}
            table.dataframe th {{
                background-color: #1f77b4;
                color: white;
            }}
            table.dataframe tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            table.dataframe th:nth-child(5), table.dataframe td:nth-child(5) {{
                text-align: right !important;
            }}
            
            thead {{
                display: table-header-group;
            }}
            tbody {{
                display: table-row-group;
            }}
            tr {{
                page-break-inside: avoid;
            }}
            @page {{
                margin: 10mm;
                size: landscape;
            }}
        </style>
        </head><body>
        
        <div class="header">
            {logo_html}
            <h2>Quartile Fund Report (Scheme Wise)</h2>
            <span><b>Date:</b> {today}</span>
            <span><b>Filters:</b> {filter_text}</span>
        </div>
        
        <table class="layout-table">
            <thead>
                <tr>
                    <td class="layout-cell"><div class="header-space">&nbsp;</div></td>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="layout-cell">
                        {table_html}
                    </td>
                </tr>
            </tbody>
        </table>
        
        <script>
            window.onload = function() {{
                window.print();
            }}
        </script>
        </body></html>
        """
        
        b64_data = base64.b64encode(html.encode('utf-8')).decode('utf-8')
        href = f"data:text/html;base64,{b64_data}"
        
        st.markdown(
            f"""
            <a href="{href}" target="_blank" 
            style="padding:5px 10px;border-radius:8px;border:1px solid #90caf9;background-color:#e3f2fd;color:#1e88e5;cursor:pointer;text-decoration:none;display:inline-block;height:38px;line-height:26px;text-align:center;font-size:16px;"
            title="Print">
            🖨️
            </a>
            """,
            unsafe_allow_html=True
        )
    
    col_refresh, col_cat, col_sec, col_sch, btn_pdf_col, btn_excel_col, btn_print_col = st.columns([0.3, 1.8, 1.8, 1.8, 0.3, 0.3, 0.3])
    with col_refresh:
        st.markdown("<div style='padding-top: 28px;'>", unsafe_allow_html=True)
        if st.button("🔄", key="refresh_scheme_wise", help="Refresh Scheme Wise Data"):
            import autodownload
            with st.spinner("Downloading Scheme Wise Data..."):
                try:
                    autodownload.MyFundList()
                    load_scheme_wise.clear()
                    st.success("Scheme Wise Data Downloaded!")
                except Exception as e:
                    st.error(f"Failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
                    
    scheme_df = load_scheme_wise()
    if not scheme_df.empty:
        #st.markdown("##### Filter Options")
        categories = scheme_df["Category Name"].dropna().unique().tolist()
        sectors = scheme_df["Sector"].dropna().unique().tolist()
        schemes = scheme_df["Scheme Name"].dropna().unique().tolist()
        
        with col_cat:
            sel_cat = st.multiselect("Category Name", options=categories)
        with col_sec:
            sel_sec = st.multiselect("Sector", options=sectors)
        with col_sch:
            sel_sch = st.multiselect("Scheme Name", options=schemes)
            
        filtered_raw = scheme_df.copy()
        if sel_cat: filtered_raw = filtered_raw[filtered_raw["Category Name"].isin(sel_cat)]
        if sel_sec: filtered_raw = filtered_raw[filtered_raw["Sector"].isin(sel_sec)]
        if sel_sch: filtered_raw = filtered_raw[filtered_raw["Scheme Name"].isin(sel_sch)]
        
        # Group to get unique Category Name, Sector, Scheme Name with AUM sum
        grouped_scheme = filtered_raw.groupby(["Category Name", "Sector", "Scheme Name"])["AUM"].sum().reset_index()
        
        # Merge with quartile details
        master_q_df = load_all_scheme_quartiles(data_file)
        required_periods = ["1 Month", "3 Months", "6 Months", "YTD", "1 Year", "2 Years"]
        
        if not master_q_df.empty:
            grouped_scheme["_match_name"] = grouped_scheme["Scheme Name"].astype(str).str.strip().str.lower()
            master_q_copy = master_q_df.copy()
            master_q_copy["_match_name"] = master_q_copy["Scheme Name"].astype(str).str.strip().str.lower()
            
            merged_scheme = pd.merge(grouped_scheme, master_q_copy.drop(columns=["Scheme Name"]), on="_match_name", how="left")
            merged_scheme.drop(columns=["_match_name"], inplace=True)
            
            # Format quartile and percentage together
            for period in required_periods:
                if period in merged_scheme.columns:
                    pct_col = f"{period}_pct"
                    if pct_col in merged_scheme.columns:
                        def format_cell(row, p=period, pc=pct_col):
                            q = row[p]
                            pct = row[pc]
                            if pd.isna(q): return ""
                            q_str = str(int(q)) if pd.notna(q) and q == q // 1 else str(q)
                            if pd.isna(pct): return q_str
                            
                            if isinstance(pct, (int, float)):
                                pct_str = f"{pct:.2f}"
                            else:
                                pct_str = str(pct)
                            return f"{q_str} ({pct_str})"
                        
                        merged_scheme[period] = merged_scheme.apply(format_cell, axis=1)

            # Drop percentage columns to keep the table clean
            cols_to_drop = [c for c in merged_scheme.columns if str(c).endswith("_pct")]
            merged_scheme.drop(columns=cols_to_drop, inplace=True, errors="ignore")
        else:
            merged_scheme = grouped_scheme
            
        # Sort and add Sr. column
        merged_scheme.sort_values(by=["Category Name", "Sector", "Scheme Name"], inplace=True, ignore_index=True)
        merged_scheme.insert(0, "Sr.", range(1, len(merged_scheme) + 1))
        
        # Apply quartile coloring
        def color_cells_quartile(val):
            val_str = str(val).strip()
            if val_str.startswith("1"): return 'background-color: rgba(39, 174, 96, 0.4)'
            elif val_str.startswith("2"): return 'background-color: rgba(241, 196, 15, 0.4)'
            elif val_str.startswith("3"): return 'background-color: rgba(230, 126, 34, 0.4)'
            elif val_str.startswith("4"): return 'background-color: rgba(231, 76, 60, 0.4)'
            return ''
            
        # applymap is deprecated in newer pandas, use map, but applymap works if map doesn't exist
        try:
            styled_df = merged_scheme.style.map(color_cells_quartile, subset=[c for c in required_periods if c in merged_scheme.columns])
        except AttributeError:
            styled_df = merged_scheme.style.applymap(color_cells_quartile, subset=[c for c in required_periods if c in merged_scheme.columns])
        # Generate filter text for the report
        active_filters = []
        if sel_cat: active_filters.append(f"Category: {', '.join(sel_cat)}")
        if sel_sec: active_filters.append(f"Sector: {', '.join(sel_sec)}")
        if sel_sch: active_filters.append(f"Scheme: {', '.join(sel_sch)}")
        filter_text = " | ".join(active_filters) if active_filters else "All Funds"
        
        # Render export buttons
        with btn_excel_col:
            st.markdown("<div style='padding-top: 28px;'>", unsafe_allow_html=True)
            scheme_export_excel(merged_scheme, filter_text, "tab3")
            st.markdown("</div>", unsafe_allow_html=True)
        with btn_pdf_col:
            st.markdown("<div style='padding-top: 28px;'>", unsafe_allow_html=True)
            scheme_export_pdf(merged_scheme, filter_text, "tab3")
            st.markdown("</div>", unsafe_allow_html=True)
        with btn_print_col:
            st.markdown("<div style='padding-top: 28px;'>", unsafe_allow_html=True)
            scheme_print_button(merged_scheme, filter_text, "tab3")
            st.markdown("</div>", unsafe_allow_html=True)
            
        #st.markdown("##### Schemes Summary")
        event = st.dataframe(
            styled_df, 
            use_container_width=True, 
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "Sr.": st.column_config.NumberColumn("Sr.", format="%d", width=15),
                "AUM": st.column_config.NumberColumn("AUM", format="%,.2f")
            }
        )
        
        selected_rows = event.selection.rows
        if selected_rows:
            selected_idx = selected_rows[0]
            selected_scheme_name = merged_scheme.iloc[selected_idx]["Scheme Name"]
            
            st.markdown(f"### Clients holding: {selected_scheme_name}")
            
            # Filter original scheme_df to find all clients holding this scheme
            detail_df = scheme_df[scheme_df["Scheme Name"] == selected_scheme_name].copy()
            
            # Fetch XIRR from ScriptWise Client Report
            detail_display = detail_df.copy()
            detail_display.sort_values(by="Client Name", inplace=True, ignore_index=True)
            
            # Download scheme-wise client report via autodownload
            import autodownload
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            scriptwise_file = os.path.join("Data", f"ScriptWise_ClientDetails_{today_str}.xls")
            
            # Download the report for the selected scheme
            with st.spinner(f"Downloading client details for {selected_scheme_name}..."):
                try:
                    result_path = autodownload.ScriptWiseClient(selected_scheme_name)
                except Exception as e:
                    st.error(f"Failed to download ScriptWise data: {e}")
                    result_path = None
            
            # Read the downloaded file and merge ClientXirr
            if result_path and os.path.exists(result_path):
                try:
                    try:
                        sw_df = pd.read_excel(result_path, engine="openpyxl")
                    except Exception:
                        sw_df = pd.read_excel(result_path, engine="xlrd")
                    
                    if "ClientXirr" in sw_df.columns:
                        # Normalize client name for matching
                        # ScriptWise file uses 'clientname' column (lowercase, no space)
                        sw_client_col = "clientname" if "clientname" in sw_df.columns else "Client Name"
                        sw_df["_sw_client"] = sw_df[sw_client_col].astype(str).str.strip().str.lower()
                        detail_display["_sw_client"] = detail_display["Client Name"].astype(str).str.strip().str.lower()
                        
                        # Merge XIRR from the ScriptWise report
                        sw_xirr = sw_df[["_sw_client", "ClientXirr"]].drop_duplicates(subset=["_sw_client"])
                        detail_display = detail_display.merge(sw_xirr, on="_sw_client", how="left")
                        detail_display.rename(columns={"ClientXirr": "XIRR"}, inplace=True)
                        detail_display.drop(columns=["_sw_client"], inplace=True)
                    else:
                        st.warning("ClientXirr column not found in downloaded file.")
                        detail_display["XIRR"] = pd.NA
                except Exception as e:
                    st.warning(f"Could not read ScriptWise file: {e}")
                    detail_display["XIRR"] = pd.NA
            else:
                st.warning("ScriptWise client data could not be downloaded.")
                detail_display["XIRR"] = pd.NA
            
            # Enforce column order: Client Name, Family Head Name, Folio, ARN No, XIRR, AUM
            base_cols = ["Client Name", "Family Head Name", "Folio", "ARN No", "XIRR", "AUM"]
            cols_to_show = [c for c in base_cols if c in detail_display.columns]
            
            detail_display = detail_display[cols_to_show].copy()
            
            # Merge with quartile data for this scheme
            if not master_q_df.empty:
                detail_display["_match_name"] = selected_scheme_name.strip().lower()
                detail_merged = pd.merge(detail_display, master_q_copy.drop(columns=["Scheme Name"]), on="_match_name", how="left")
                detail_merged.drop(columns=["_match_name"], inplace=True)
                
                # Format quartile and percentage together for details
                for period in required_periods:
                    if period in detail_merged.columns:
                        pct_col = f"{period}_pct"
                        if pct_col in detail_merged.columns:
                            def format_cell_detail(row, p=period, pc=pct_col):
                                q = row[p]
                                pct = row[pc]
                                if pd.isna(q): return ""
                                q_str = str(int(q)) if pd.notna(q) and q == q // 1 else str(q)
                                if pd.isna(pct): return q_str
                                if isinstance(pct, (int, float)): pct_str = f"{pct:.2f}"
                                else: pct_str = str(pct)
                                return f"{q_str} ({pct_str})"
                            detail_merged[period] = detail_merged.apply(format_cell_detail, axis=1)

                cols_to_drop = [c for c in detail_merged.columns if str(c).endswith("_pct")]
                detail_merged.drop(columns=cols_to_drop, inplace=True, errors="ignore")
            else:
                detail_merged = detail_display
                
            # Add Sr. column
            detail_merged.insert(0, "Sr.", range(1, len(detail_merged) + 1))
            
            try:
                detail_styled = detail_merged.style.map(color_cells_quartile, subset=[c for c in required_periods if c in detail_merged.columns])
            except AttributeError:
                detail_styled = detail_merged.style.applymap(color_cells_quartile, subset=[c for c in required_periods if c in detail_merged.columns])
                
            st.dataframe(
                detail_styled, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Sr.": st.column_config.NumberColumn("Sr.", format="%d", width=15),
                    "XIRR": st.column_config.NumberColumn("XIRR (%)", format="%.2f"),
                    "AUM": st.column_config.NumberColumn("AUM", format="%,.2f")
                }
            )
            
    else:
        st.info("No Scheme Wise Data found. Please click 'Refresh Scheme Wise Data' above to download.")
