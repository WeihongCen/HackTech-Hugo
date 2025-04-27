import collections
from pydantic import BaseModel
from typing import Union


SCHEMA_DESCRIPTION = """
We have a procurement database with the following tables:

**Table 1: dispatch_parameters**
Description: This table contains information about the minimum stock levels, reorder quantities, and reorder intervals for different parts.
Columns:
- part_id
- min_stock_level
- reorder_quantity
- reorder_interval_days

**Table 2: material_master**
Description: This table provides detailed information about each part, including its name, type, models it is used in, dimensions, weight, and any related parts.
Columns:
- part_id
- part_name
- part_type
- used_in_models
- weight
- blocked_parts
- successor_parts
- comment

**Table 3: material_orders**
Description: This table records purchase orders for parts, including order details, supplier information, and delivery status.
Columns:
- order_id
- part_id
- quantity_ordered
- order_date
- expected_delivery_date
- supplier_id
- status
- actual_delivered_at

**Table 4: sales_orders**
Description: This table contains information about sales orders, including the model, version, quantity, order type, and dates related to the order process.
Columns:
- sales_order_id
- model
- version
- quantity
- order_type
- requested_date
- created_at
- accepted_request_date

**Table 5: stock_levels**
Description: This table provides the current inventory levels of parts in different warehouse locations.
Columns:
- part_id
- part_name
- location
- quantity_available

**Table 6: stock_movements**
Description: This table records transactions related to inventory movements, including inbound and outbound quantities.
Columns:
- date
- part_id
- type
- quantity

**Table 7: suppliers**
Description: This table contains information about suppliers, including pricing, lead times, minimum order quantities, and reliability ratings for different parts.
Columns:
- supplier_id
- part_id
- price_per_unit
- lead_time_days
- min_order_qty
- reliability_rating

**Table 7: specs**
Description: This table contains information about the required parts to assemble a product, including the part name and the quantity required.
Columns:
- product_id
- product_name
- part_id
- quantity
"""
FOREIGN_KEYS = {"part_id": "material_master"}

class Column(BaseModel):
    column_name: str
    value: Union[str, int, float, None]

class Row(BaseModel):
    table_name: str
    columns: list[Column]

class Response(BaseModel):
    rows: list[Row]


def generate_data_rows(client_openai, input):
    prompt = f"""
    {SCHEMA_DESCRIPTION}

    Based on the schema description above and the input data below:
    {input}

    Your task is to:
    - Decide which rows need to be edited or inserted into the database.
    - For each row, clearly specify:
      - `table_name`: the table to insert or update
      - `columns`: a list of columns to modify, where each column has:
        - `column_name`: the exact field name from the schema
        - `value`: the new value to set for that column (can be a string, number, or null)

    Important rules:
    - Only use tables and column names defined in the provided schema.
    - Fill missing information intelligently if the input clearly implies it.
    - Keep values consistent with their expected data types.
    - Return the final structured response strictly matching the given Response model format.

    Think carefully before constructing the rows.
    """

    completion = client_openai.beta.chat.completions.parse(
        model="gpt-4.1-2025-04-14",
        response_format=Response,
        messages=[
            {
                "role": "system", 
                "content": 
                """
                You are a highly accurate procurement assistant. Your role is to map freeform input 
                into structured schema edits according to strict schema definitions. 
                You must not invent extra tables or columns.
                You must return clean, structured row edits exactly matching the database schema.
                """
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    rows = completion.choices[0].message.parsed.rows
    print(rows)
    return rows


def verify_foreign_key(client_supabase, foreign_key, rows):
    foreign_keys = set()
    for row in rows:
        if foreign_key in row:
            foreign_keys.add(row[foreign_key])
    
    if not foreign_keys:
        return set()
    
    response = client_supabase.table(FOREIGN_KEYS[foreign_key]).select(foreign_key).in_(foreign_key, list(foreign_keys)).execute()
    
    existing_keys = set()
    if response.data:
        existing_keys = {item[foreign_key] for item in response.data}

    missing_keys = foreign_keys - existing_keys
    missing_data = [{foreign_key: key} for key in missing_keys]

    if len(missing_data) > 0:
        response = client_supabase.table(FOREIGN_KEYS[foreign_key]).insert(missing_data).execute()
    

def upsert(client_supabase, rows):
    tables = collections.defaultdict(list)
    for row in rows:
        data = {}
        for column in row.columns:
            data[column.column_name] = column.value
        tables[row.table_name].append(data)


    for table_name, data in tables.items():
        for foreign_key in FOREIGN_KEYS:
            verify_foreign_key(client_supabase, foreign_key, data)
        print(data)
        client_supabase.table(table_name).upsert(data).execute()