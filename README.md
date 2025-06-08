# ESF Extraction and Analysis Tool

A Streamlit-based web application for analyzing and visualizing student academic performance data from ESF (Escola Sant Feliu) reports.

## Features

- Interactive data visualization of student performance
- Subject-wise analysis and statistics
- Individual student performance tracking
- Comparative analysis between academic terms
- Detailed grade distribution visualization
- Student evolution tracking
- Comprehensive subject-wise comments and feedback

## Project Structure

```
├── app.py                 # Main Streamlit application
├── acta_processor.py      # Processing logic for academic records
├── acta_statistics.py     # Statistical analysis functions
├── json_viewer.py         # JSON data visualization utilities
├── requirements.txt       # Project dependencies
├── components/           # Reusable UI components
├── sections/            # Main application sections
├── utils/               # Utility functions and helpers
├── docs/               # Documentation and data files
└── calc_scripts/       # Calculation and processing scripts
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd esfextraction
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Access the application through your web browser at `http://localhost:8501`

## Main Features

### Data Visualization
- Classroom performance tables
- Subject-wise statistics
- Student mark frequency visualization
- Individual student performance tracking
- Comparative analysis between terms

### Student Analysis
- Individual student performance tracking
- Grade evolution visualization
- Subject-wise grade breakdown
- Detailed feedback and comments

## Dependencies

The project uses several key Python packages:
- Streamlit for the web interface
- Pandas for data manipulation
- Altair and Plotly for visualizations
- PDF processing libraries (pdf2image, pdfplumber)
- Various data analysis and visualization tools

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Specify your license here]

## Contact

[Your contact information] 