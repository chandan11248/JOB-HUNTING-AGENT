"""Google Sheets writer using gspread."""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import Optional
from config import Config


class SheetsWriter:
    """Google Sheets writer for exporting job data."""
    
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    def __init__(self):
        self.client: Optional[gspread.Client] = None
        self.sheet: Optional[gspread.Spreadsheet] = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the Google Sheets client."""
        self.error = None
        try:
            if not Config.GOOGLE_SERVICE_ACCOUNT_FILE:
                self.error = "Missing GOOGLE_SERVICE_ACCOUNT_FILE in .env"
                return
                
            creds = Credentials.from_service_account_file(
                Config.GOOGLE_SERVICE_ACCOUNT_FILE,
                scopes=self.SCOPES
            )
            self.client = gspread.authorize(creds)
            
            # Open the spreadsheet from URL
            if Config.GOOGLE_SHEET_URL:
                try:
                    self.sheet = self.client.open_by_url(Config.GOOGLE_SHEET_URL)
                except gspread.exceptions.SpreadsheetNotFound:
                    self.error = "Spreadsheet not found. Check the URL in .env."
                except gspread.exceptions.APIError as e:
                    self.error = f"Google API Error: {str(e)}"
                except Exception as e:
                    self.error = f"Error opening sheet: {str(e)}"
            else:
                self.error = "Missing GOOGLE_SHEET_URL in .env"
                
        except Exception as e:
            import traceback
            print(f"Error initializing Google Sheets: {e}")
            print(traceback.format_exc())
            self.error = f"Initialization Error: {str(e)}"
            self.client = None
            self.sheet = None
    
    def ensure_worksheet(self, name: str = "Jobs") -> Optional[gspread.Worksheet]:
        """Ensure a worksheet exists with the given name.
        
        Args:
            name: Worksheet name
            
        Returns:
            Worksheet object or None
        """
        if not self.sheet:
            return None
            
        try:
            return self.sheet.worksheet(name)
        except gspread.WorksheetNotFound:
            worksheet = self.sheet.add_worksheet(title=name, rows=1000, cols=10)
            # Add header row
            headers = [
                "Title", "Company", "Location", "Salary", 
                "URL", "Added Date", "Applied", "Notes"
            ]
            worksheet.insert_row(headers, 1)
            return worksheet
    
    def add_job(self, job: dict, worksheet_name: str = "Jobs") -> bool:
        """Add a single job to the spreadsheet.
        
        Args:
            job: Job dictionary from Jooble API
            worksheet_name: Name of the worksheet
            
        Returns:
            True if successful, False otherwise
        """
        worksheet = self.ensure_worksheet(worksheet_name)
        if not worksheet:
            return False
        
        try:
            row = [
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("salary", ""),
                job.get("link", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                "No",  # Applied status
                ""     # Notes
            ]
            worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"Error adding job to sheet: {e}")
            return False
    
    def add_jobs_batch(self, jobs: list, worksheet_name: str = "Jobs") -> int:
        """Add multiple jobs to the spreadsheet.
        
        Args:
            jobs: List of job dictionaries
            worksheet_name: Name of the worksheet
            
        Returns:
            Number of jobs successfully added
        """
        worksheet = self.ensure_worksheet(worksheet_name)
        if not worksheet:
            print("Export failed: Worksheet not found and could not be created.")
            return 0
        
        try:
            rows = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            for job in jobs:
                rows.append([
                    job.get("title", ""),
                    job.get("company", ""),
                    job.get("location", ""),
                    job.get("salary", ""),
                    job.get("link", ""),
                    timestamp,
                    "No",
                    ""
                ])
            
            if rows:
                # Insert starting at row 2 (just below headers)
                # This ensures visibility even if there are many empty rows at the bottom
                print(f"Attempting to insert {len(rows)} jobs into sheet...")
                worksheet.insert_rows(rows, row=2)
                print("Successfully inserted rows.")
            
            return len(rows)
        except Exception as e:
            import traceback
            print(f"Error adding jobs batch: {e}")
            print(traceback.format_exc())
            return 0
    
    def get_sheet_url(self) -> str:
        """Get the URL of the spreadsheet.
        
        Returns:
            Spreadsheet URL or error message
        """
        if self.sheet:
            return self.sheet.url
        return "Sheet not initialized. Check your Google credentials."
    
    def mark_as_applied(self, row_number: int, worksheet_name: str = "Jobs") -> bool:
        """Mark a job as applied.
        
        Args:
            row_number: Row number (1-indexed, excluding header)
            worksheet_name: Worksheet name
            
        Returns:
            True if successful
        """
        worksheet = self.ensure_worksheet(worksheet_name)
        if not worksheet:
            return False
        
        try:
            # Column G is "Applied" (7th column)
            worksheet.update_cell(row_number + 1, 7, "Yes")
            return True
        except Exception as e:
            print(f"Error marking as applied: {e}")
            return False
