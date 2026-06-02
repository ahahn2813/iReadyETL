# iReadyETL

A user-friendly ETL (Extract, Transform, Load) tool that transforms iReady diagnostic CSV exports into comprehensive, multi-term Excel reports with visualizations—designed specifically for elementary school teachers.

## ⚠️ The Problem

Teachers use **iReady** for homework assignments and diagnostic assessments (administered each term: Fall, Winter, and Spring). While iReady provides valuable assessment data, the platform has significant limitations:

1. **📊 Fragmented Data**: Teachers can only download diagnostic data for a single term at a time (Fall *or* Winter *or* Spring), making it difficult to track and compare student progress across the school year.

2. **❓ Missing Growth Analysis**: Winter and Spring diagnostic files don't automatically show whether students met their growth goals. Teachers can only see:
   - Raw scores
   - Grade placement levels
   - Percentiles
   - Lexile levels
   - Other subject-specific skills

3. **⏰ Manual Workarounds**: To determine if a student achieved their "typical" or "stretch" growth goals, teachers must manually:
   - Calculate score differences between terms
   - Compare against goals (which are only visible in Fall data)
   - Click through individual student profiles to find missing information
   - Combine data from multiple downloads into a single workable document

**Result**: What should be a quick data review becomes hours of tedious manual work.

## ✨ The Solution

**iReadyETL** eliminates this workflow by automating the entire process. Simply upload your iReady CSV files (for any combination of terms), and get back a beautifully formatted, feature-rich Excel report plus visualization charts.

### 📋 What You Get

A single Excel file containing:

- **Student Information**: Name and student identifier
- **Term Scores**: Fall, Winter, and/or Spring diagnostic scores
- **Growth Tracking**: 
  - Typical growth goals and whether they were met (✓ YES / ✗ NO)
  - Stretch growth goals and whether they were met (✓ YES / ✗ NO)
  - Quantified growth amounts between terms
- **Performance Metrics**: Percentiles, grade level placements, core standard assessments (Reading: Phonemic Awareness, Phonics, High Frequency Words, Vocabulary, Comprehension; Math: Number Operations, Algebra and Algebraic Thinking, Measurement and Data, Geometry)
- **Color-Coded Visualization**:
  - 🟢 Green for met growth goals and positive progress
  - 🔴 Red for unmet goals and negative progress
  - Color-coded grade level placements for easy visual scanning
- **Note**: This was created with fourth grade in mind (i.e., fourth grade standards are hard-coded for a school's specific abbreviations). Please reach out if you would like to use this with your grade level.

### 📊 Automatically Generated Charts

The tool also generates professional visualization charts:

- **Goals Met Analysis**: Pie/bar charts showing the percentage of students who met typical and stretch growth goals
- **Growth Amount Distribution**: Box plots and histograms showing score change distributions
- **Term Comparison**: Side-by-side growth analysis comparing Fall→Winter, Winter→Spring, and Fall→Spring progress

All charts are automatically saved as PNG files in your output folder.

### 📁 Supported Formats

- **Subjects**: Reading and Math
- **Terms**: Fall, Winter, Spring (any combination—one term, two terms, or all three)
- **Input**: iReady CSV exports
- **Output**: Formatted Excel file with conditional styling + PNG visualization charts

## 🚀 Quick Start (Windows Users)

**No Python required!**

1. Download `iready_etl.exe` from this repository
2. Double-click to launch
3. A configuration window will open with a user-friendly GUI
4. Select your subject (Math or Reading)
5. Check which terms you want to process (Fall, Winter, and/or Spring)
6. Browse and select your CSV files in order (Fall first, then Winter, then Spring if applicable)
7. Choose where to save your output Excel file
8. Done! The tool generates your Excel report and visualization charts automatically.

**⚠️ Important**: File upload order matters! If you are uploading Fall and Winter, upload the Fall CSV first and Winter second. Similar order applies for Fall, Winter, and Spring (i.e., chronological order).

### 🎯 GUI Features

The new interactive configuration window makes setup simple:
- Clear step-by-step layout
- Visual confirmation of selected files
- Subject and term selection checkboxes
- Browse buttons for easy file selection
- Status indicators showing which files are selected

My personal machine is MacOS, but most school districts utilize Windows. Thus, the `.exe` interface was configured for Windows using GitHub Actions. Please reach out if you would like the MacOS version!

### 🛡️ Windows Defender SmartScreen Warning

You may see a Windows Defender SmartScreen warning when downloading or running `iready_etl.exe`. **This is safe to ignore.**

**Why does this happen?**
- Your .exe is new and not yet recognized by Microsoft's reputation system
- PyInstaller-built executables sometimes trigger false positives
- The tool is 100% open source—you can review the code on GitHub to verify it's safe

**How to proceed:**
1. Click **"More info"** on the SmartScreen warning
2. Click **"Run anyway"**
3. Your file will run normally and the warning will not appear again

**What we're doing about it:**
- The warning will automatically disappear as more people safely download and run the tool (Microsoft builds reputation over time)
- We may implement code signing in the future for complete elimination of this warning

**If you're concerned:**
- Review the open-source code yourself on GitHub
- Run the Python version instead (see "Manual Installation" below—no .exe needed)
- Contact us with questions

### 🧪 Test with Example Data

Want to try the tool before using your actual student data? This repository includes **synthetic iReady CSV files** in the `iReady_Data_Example_Synthetic/` folder:

- `synthetic_FA_iready_math.csv` - Fall Math example
- `synthetic_FA_iready_reading.csv` - Fall Reading example
- `synthetic_WI_iready_math.csv` - Winter Math example
- `synthetic_WI_iready_reading.csv` - Winter Reading example
- `synthetic_SP_iready_math.csv` - Spring Math example
- `synthetic_SP_iready_reading.csv` - Spring Reading example

**Quick Test Workflow:**
1. Download the `.exe` and launch it
2. Select Math or Reading and check the terms you want (e.g., Fall + Winter)
3. When prompted, select the corresponding synthetic CSV files from `iReady_Data_Example_Synthetic/`
4. Save your test output file
5. Review the formatted Excel report and generated charts to see how the tool works

This is a risk-free way to explore all features without worrying about student data!

## 💻 Or: Manual Installation (if you prefer)

### Requirements

- Python 3.7+
- Dependencies:
  - `pandas` - Data manipulation and analysis
  - `openpyxl` - Excel file handling
  - `seaborn` - Data visualization utilities
  - `matplotlib` - Plotting library
  - `numpy` - Numerical computing

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ahahn2813/iReadyETL.git
   cd iReadyETL
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install pandas openpyxl seaborn matplotlib numpy
   ```

3. Run the application:
   ```bash
   python iready_etl.py
   ```

## 📖 Usage

### Step 1: Launch the Configuration Window

Running the script opens a desktop GUI where you'll configure your analysis:

```
ETL Tool Configuration
├─ 1. Select Subject
│  └─ Math or Reading
├─ 2. Select Terms to Process
│  ├─ Fall Scores
│  ├─ Winter Scores
│  └─ Spring Scores
└─ 3. Select Your Files
   ├─ Browse for Fall CSV
   ├─ Browse for Winter CSV (if selected)
   └─ Browse for Spring CSV (if selected)
```

### Step 2: Select Your CSV Files

The tool will prompt you to select iReady CSV exports in chronological order (Fall → Winter → Spring). Select the files from your downloads.

### Step 3: Choose Output Location

Select where you'd like to save the final Excel report and charts.

### Step 4: Review Your Report and Charts

The tool generates:
- A professionally formatted Excel file with all student data merged across terms, growth goals calculated, and color-coded cells
- Multiple PNG chart files showing:
  - Goals Met percentages
  - Growth amount distributions
  - Term-by-term comparisons

## 📈 Example Workflow

**Scenario**: A teacher downloads Fall, Winter, and Spring Math diagnostic CSVs and wants to see which students met their yearly growth goals.

1. Run `python iready_etl.py` (or double-click `iready_etl.exe` on Windows)
2. Select "Math" and check Fall, Winter, and Spring
3. Upload the three CSV files when prompted (in order: Fall, Winter, Spring)
4. Save the output file (e.g., `Class_Math_Progress_2024.xlsx`)
5. Open the Excel file and view the generated charts to see:
   - Each student's Fall, Winter, and Spring scores
   - Whether they met typical growth goals by Winter and Spring
   - Exact growth amounts (+15 points, -8 points, etc.)
   - Color-coded visual summary
   - Visual analysis of class-wide progress

**⏱️ Time Saved**: Approximately 2-3 hours of manual data entry, calculation, and charting reduced to **1-2 minutes**.

## 🔧 How It Works

### Data Processing Pipeline

1. **Cleaning Phase**:
   - Normalizes column names across iReady exports
   - Removes irrelevant fields (e.g., language flags, relative growth projections, date flags)
   - Standardizes placement level abbreviations (e.g., "Surpassed Level" → "S")

2. **Merging Phase**:
   - Performs outer joins to capture all students across terms
   - Handles students who may only appear in certain terms

3. **Feature Engineering**:
   - Calculates growth goals based on Fall baseline + growth measures
   - Evaluates whether Winter/Spring scores meet typical and stretch goals
   - Computes growth deltas (score changes between terms)
   - Reorganizes columns for readability

4. **Formatting Phase**:
   - Applies conditional formatting with color coding in Excel
   - Green cells for positive growth/met goals
   - Red cells for no growth/unmet goals
   - Rounds numeric values for cleaner presentation

5. **Visualization Phase**:
   - Generates professional charts using Seaborn and Matplotlib
   - Creates multiple PNG files showing growth analysis and goal achievement
   - Saves charts to the same directory as the Excel output

## 🔐 Security & Privacy

**Your student data is safe.**

iReadyETL is a **100% local application**—all processing happens on your personal device or school computer. 

- ✅ **No data transmission**: CSV files are never uploaded to external servers  
- ✅ **No data collection**: iReadyETL does not collect, store, or track any user information  
- ✅ **No third-party sharing**: Student data never leaves your device  
- ✅ **FERPA compliant**: Works entirely within your school's existing data security protocols  
- ✅ **Open source**: Full transparency—review the code to see exactly what the tool does with your data  

**How it works:**
- You select files from your local device using the GUI
- The tool processes them locally using only the libraries on your computer
- Output files (Excel report and PNG charts) are saved wherever you choose on your local device
- That's it—no network calls, no uploads, no cloud storage

This makes iReadyETL particularly suited for schools with strict data privacy requirements and FERPA compliance obligations.

## ⭐ Key Features

✅ **No Coding Required** - Simple GUI for non-technical users  
✅ **Flexible Term Selection** - Process any combination of Fall, Winter, and/or Spring data  
✅ **Automatic Growth Calculation** - No manual math needed  
✅ **Visual Analytics** - Color-coded Excel cells AND professional chart visualizations  
✅ **Class or Grade-Level** - Works with individual class rosters or full grade data  
✅ **Fast** - Converts hours of manual work to seconds  
✅ **Accessible** - Designed specifically for teachers with no coding experience  
✅ **Secure & Private** - All processing happens locally on your device

## 🛠️ Technical Architecture

- **Language**: Python 3
- **Core Libraries**: Pandas (data manipulation), OpenPyXL (Excel export), Seaborn & Matplotlib (visualization)
- **Interface**: Tkinter (desktop GUI)
- **Data Format**: CSV input, XLSX output + PNG charts
- **Data Processing**: 100% local (no external APIs or network communication)

## 📋 Limitations & Future Enhancements

### Current Limitations
- `.exe` is Windows-only; Python users can run on any operating system (Windows, MacOS, Linux)
- Works with iReady CSV format only (other assessment platforms not yet supported)
- Single-subject processing (process Math and Reading separately)
- Hard-coded for fourth grade standards (customization available upon request)

### 🚀 Potential Enhancements
- Standalone executables for MacOS and Linux
- Support for additional assessment platforms (Fountas & Pinnell, NWEA MAP, etc.)
- Dashboard/web-based visualization features for district-level analysis
- Batch processing for multiple classes/grades
- Google Sheets integration
- Automatic email delivery of reports
- Customizable grade-level standards
- Interactive visualization dashboard

## 🤝 Contributing

This project was created to solve a real problem for educators. Contributions are welcome! If you have suggestions for improvements or encounter issues, please feel free to open an issue or submit a pull request.

## 📜 License

This project is open source and available for educational use.

## 💬 Support

For questions or issues:
1. Check the repository's [Issues](https://github.com/ahahn2813/iReadyETL/issues) section
2. Review the usage examples above
3. Verify your CSV files match the iReady export format
4. Test with the synthetic data files provided in `iReady_Data_Example_Synthetic/`

## 🎓 Acknowledgments

Built for elementary school teachers who spend countless hours analyzing student assessment data. This tool was created to give teachers back their time.

All data cleaning, merging, feature engineering, and code structure is original and created without use of AI (lines 1-210). Gemini was used to debug the GUI implementation and chart generation portions of the code.

---

**Questions?** Open an issue on this repository or feel free to reach out to the maintainer!
