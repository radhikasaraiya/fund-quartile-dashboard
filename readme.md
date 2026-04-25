# 📊 Mutual Fund Quartile Performance Dashboard

A powerful Streamlit-based dashboard that analyzes mutual fund performance using Quartile rankings across multiple time periods.

This application allows users to:
- Upload multi-sheet Excel files
- Filter by Fund Category and Sub-Category
- Classify funds into Good, Neutral, and Low Performing
- Search schemes instantly
- Export filtered results to Excel, PDF, or Print
- View performance summary cards and visual charts

---

## 🚀 Features

### ✅ Multi-Sheet Excel Support
- Automatically detects header row containing "Scheme Name"
- Extracts Quartile columns for:
  - 1 Month
  - 3 Months
  - 6 Months
  - YTD
  - 1 Year
  - 2 Years

### ✅ Smart Classification Logic
Funds are categorized as:

- **Good Performing** → All selected period quartiles ≤ 1
- **Neutral** → Mixed quartiles (not fully Good or Low)
- **Low Performing** → All selected period quartiles ≥ 3

### ✅ Interactive Filters
- Fund Category dropdown (Debt, Equity, Hybrid, etc.)
- Sub-Category dropdown (Overnight, Multi Cap, etc.)
- Live search by Scheme Name

### ✅ Export Options
Per active tab:
- 📥 Excel Export
- 📄 PDF Export
- 🖨 Direct Print

### ✅ Visual Insights
- Performance Summary Cards
- Category Distribution Charts
- Quartile Trend Analysis

---

## 🛠 Installation

### 1️⃣ Clone the Repository

```
git clone https://github.com/your-username/fund-quartile-dashboard.git
cd fund-quartile-dashboard
```

### 2️⃣ Create Virtual Environment (Recommended)

```
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux
```

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

## 📦 Requirements

Create a `requirements.txt` file with:

```
streamlit
pandas
openpyxl
xlsxwriter
reportlab
```

---

## ▶️ Run the Application

```
streamlit run Main.py
```

The app will open in your browser at:

```
http://localhost:8501
```

---

## 📁 Project Structure

```
Fund-Quartile-Dashboard/
│
├── Main.py
├── requirements.txt
├── README.md
└── sample_data.xlsx (optional)
```

---

## 📊 How It Works

1. Upload the mutual fund Excel file
2. Select Fund Category
3. Select Sub-Category
4. View categorized tabs:
   - Good Performing
   - Neutral
   - Low Performing
5. Use search and export as needed

---

## ☁ Deployment Options

### Streamlit Cloud (Recommended)
- Push code to GitHub
- Deploy via Streamlit Cloud
- Share public URL with clients

### Local Deployment
- Share source code + requirements.txt
- Client runs using `streamlit run Main.py`

### Executable (Optional)
- Can be packaged using PyInstaller
- Requires Python environment setup consideration

---

## 🔐 Notes

- Ensure Excel sheets follow expected format
- Header row must contain "Scheme Name"
- Quartile columns must be consistently labeled

---

## 📌 Future Enhancements

- Add database integration
- Add historical comparison
- Add downloadable summary reports
- Add authentication layer

---

## 👩‍💻 Developed With

- Python
- Streamlit
- Pandas
- ReportLab

---

## 📞 Support

For issues or improvements, please raise an issue in the repository.

---

**Happy Analyzing! 📈**