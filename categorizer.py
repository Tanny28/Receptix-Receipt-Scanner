import re
import logging
from collections import defaultdict

# Predefined category keywords
CATEGORY_KEYWORDS = {
    'Food & Dining': ['restaurant', 'cafe', 'coffee', 'food', 'meal', 'snack', 'burger', 'pizza'],
    'Transportation': ['uber', 'lyft', 'taxi', 'gasoline', 'metro', 'bus', 'train'],
    'Shopping': ['store', 'retail', 'amazon', 'shopping', 'walmart', 'electronics'],
    'Utilities': ['electric', 'internet', 'bill', 'water'],
    'Entertainment': ['movie', 'ticket', 'music', 'netflix'],
    'Healthcare': ['pharmacy', 'medicine', 'doctor', 'hospital'],
    'Office & Business': ['design', 'package', 'mouse pad', 'office'],
    'Miscellaneous': ['fee', 'total', 'gst', 'other']
}


def parse_amounts_and_items(text):
    amounts = []
    items = []

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    amount_patterns = [
        r'₹\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',     # ₹13,715.52
        r'(\d{1,3}(?:,\d{3})+(?:\.\d{2})?)',         # 9,999.00
        r'(\d+\.\d{2})',                             # 975.00
        r'(\d+)\s*\.\s*(\d{2})'                      # 99 . 00
    ]

    for line in lines:
        found_amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                try:
                    if isinstance(match, tuple):
                        amount = float(f"{match[0]}.{match[1]}")
                    else:
                        amount = float(match.replace(',', ''))
                    if 1 <= amount <= 999999:
                        found_amounts.append(amount)
                except:
                    continue

        if found_amounts:
            item_text = line
            for pattern in amount_patterns:
                item_text = re.sub(pattern, '', item_text)
            item_text = re.sub(r'[^\w\s-]', ' ', item_text)
            item_text = re.sub(r'\s+', ' ', item_text).strip()
            if len(item_text) > 2:
                items.append(item_text)
                amounts.extend(found_amounts)

    logging.info(f"✅ Found {len(amounts)} amounts and {len(items)} item lines.")
    return amounts, items


def categorize_expenses(items):
    categorized = defaultdict(lambda: {'items': [], 'amounts': []})

    for item in items:
        matched = False
        item_lower = item.lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in item_lower for keyword in keywords):
                categorized[category]['items'].append(item)
                matched = True
                break
        if not matched:
            categorized['Miscellaneous']['items'].append(item)

    return categorized


def assign_amounts_to_categories(amounts, categorized):
    all_items = sum(len(data['items']) for data in categorized.values())
    if all_items == 0 or not amounts:
        return categorized

    if all_items == len(amounts):
        index = 0
        for category in categorized:
            num_items = len(categorized[category]['items'])
            categorized[category]['amounts'] = amounts[index:index + num_items]
            index += num_items
    else:
        total_amount = sum(amounts)
        for category in categorized:
            item_count = len(categorized[category]['items'])
            if item_count > 0:
                portion = item_count / all_items
                amount_share = total_amount * portion
                avg = amount_share / item_count
                categorized[category]['amounts'] = [round(avg, 2)] * item_count

    return categorized


def smart_categorize(text):
    amounts, items = parse_amounts_and_items(text)
    categorized = categorize_expenses(items)
    categorized = assign_amounts_to_categories(amounts, categorized)
    return categorized, sum(amounts)
