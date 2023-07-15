# ImageByCategory

This is simple Python web service that show image based on required category(-ies).

# Explanation

This service show you different images based on three things:
1. Your requested categories.
2. Number of views. Every image has a maximum value that means how much times it can be showed.
3. History of views. Service tries to avoid repetitions.

Main idea is that every thing above has its own coefficient. It can be from 0.0 to 1.0 and means probability for viewing.
All coefficients are multiplied with each other.

The coefficient for the category is calculated by the formula `matched_category/requested_category`
History coefficient is calculated by the formula `1/(1 + ((x1) ^ 3)*((x2) ^ 3)*...((xn) ^ 3))` where x is serial numbers when the image was last in history.
The coefficient on the number of views is calculated by the formula: `ramaining_vies/max_vies`

Based on the obtained probability, an image is selected randomly.

# Dependencies

First you need to install project dependecies. Use the command: `pip install -r requirements.txt` 

# Usage

1. Place images you want to see to app/static
2. Edit content.csv - add new line like this: url_to_image;view_count;category1;category2;...
1. Run `uvicorn uvicorn app.main:app --reload`
2. Go to http://127.0.0.1:[port]/?cateroty=Category1&cateroty=Category2... and enjoy.

