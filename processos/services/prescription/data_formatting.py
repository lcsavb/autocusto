"""
Prescription Data Formatting Service

Handles medical prescription data preparation and formatting.
Contains business logic for Brazilian prescription date formatting.

Extracted from prescription_services.py to follow single responsibility principle.
"""

import logging
from datetime import datetime, timedelta


class PrescriptionDataFormatter:
    """
    Handles medical prescription data preparation and formatting.
    
    Contains business logic for Brazilian prescription date formatting.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def format_prescription_date(self, raw_data: dict) -> dict:
        """
        Generate sequential prescription dates (30 days apart) per Brazilian regulations.
        
        Args:
            raw_data: Prescription form data
            
        Returns:
            dict: Data with formatted sequential dates
        """
        self.logger.debug(f"PrescriptionDataFormatter: Starting format with {len(raw_data)} fields")
        
        # Create a copy to avoid modifying original
        data = raw_data.copy()
        
        if 'data_1' not in data or not data['data_1']:
            self.logger.debug("PrescriptionDataFormatter: No data_1 found, skipping date formatting")
            return data
            
        initial_date = data['data_1']
        self.logger.debug(f"PrescriptionDataFormatter: Initial date type: {type(initial_date)}, value: {initial_date}")
        
        # Ensure initial_date is a datetime object
        if isinstance(initial_date, str):
            try:
                initial_date = datetime.strptime(initial_date, "%d/%m/%Y")
                self.logger.debug(f"PrescriptionDataFormatter: Parsed string date to datetime: {initial_date}")
            except ValueError:
                self.logger.warning(f"PrescriptionDataFormatter: Invalid date format: {initial_date}")
                return data
        
        # Generate sequential dates for 6-month prescription
        for month in range(1, 7):
            date_obj = initial_date + timedelta(days=30 * (month - 1))
            formatted_date = date_obj.strftime("%d/%m/%Y")
            data[f"data_{month}"] = formatted_date
            self.logger.debug(f"PrescriptionDataFormatter: Set data_{month} = {formatted_date}")
        
        self.logger.debug(f"PrescriptionDataFormatter: Formatting complete, {len(data)} fields in output")
        return data