# Virtual Manager

#### Video Demo:  https://youtu.be/ffEXanLAWes

#### Description:
Virtual Manager is an inventory and product management system developed as the final project for the CS50 course. Its primary goal is to simplify inventory tracking and streamline the management of items and products with recipe-based deduction capabilities.

### Features:
- **Inventory Tracking**: Monitor item quantities and set alerts for low stock levels.
- **Recipe-Based Deductions**: Automatically deduct required ingredients when creating products with associated recipes.
- **User Management**: Supports multiple users with secure authentication.
- **Data Integrity**: Includes triggers to maintain consistency when recipes are removed or modified.

### Technologies Used:
- **Back-End**: Flask (Python 3.12.8)
- **Database**: SQLite with a well-defined schema
- **Front-End**: HTML, CSS, Bootstrap 5.1.3, JavaScript (jQuery 3.7.1)

### Limitations:
- The sales functionality was omitted due to time constraints.
- The Repository Pattern was planned but not implemented for this version.

### Development Highlights:
- Focused on clean database interactions with modularized helper functions.
- Implemented dynamic form validation and error handling using custom macros.
- Designed with extensibility in mind, allowing future integration of sales tracking and additional features.
