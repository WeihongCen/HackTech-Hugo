from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from supabase import create_client
import pandas as pd
import dotenv
import os
dotenv.load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

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
TABLES = ["material_master", 
          "stock_levels",
          "stock_movements",
          "dispatch_parameters", 
          "material_orders", 
          "sales_orders", 
          "suppliers",
          "specs",
          ]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def query(input):
    print("Querying database")
    dataframes = []
    for table in TABLES:
        try:
            response = supabase.table(table).select("*").execute()
            if response.data:
                df = pd.DataFrame(response.data)
                dataframes.append(df)
        except Exception as e:
            print(f"Cannot find table {table}")

    print(f"Processing {len(dataframes)} dataframes")

    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model="gpt-4.1"),
        dataframes,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True
    )

    response = agent.invoke(input)
    return response["output"]