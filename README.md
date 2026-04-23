# Property Rental/Relocation App

## Setup

run this is a python virtualenv

### Generating Sample Data

To generate the sample SQLite database with mock properties:

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the data generation script:

```bash
python generate_sample_data.py
```

This will create a `sample-data.db` SQLite database file with approximately 100
properties, including:

- Property details (name, description, type, location, etc.)
- Amenities
- Pricing rules for dynamic pricing
- Bookings for calendar/availability
- Image references

## Database Schema

The database contains the following tables:

- **properties**: Main property information
- **property_amenities**: Many-to-many relationship for amenities
- **pricing_rules**: Seasonal/dynamic pricing rules
- **bookings**: Booking/availability data
- **property_images**: Image URLs for properties
