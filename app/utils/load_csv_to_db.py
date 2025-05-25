import pandas as pd
from app import db, create_app
from app.models import SupplyChain
import os

def load_csv_to_db(csv_path):
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        record = SupplyChain(
            payment_type=row['Type'],
            days_for_shipping_real=row['Days for shipping (real)'],
            days_for_shipment_scheduled=row['Days for shipment (scheduled)'],
            benefit_per_order=row['Benefit per order'],
            sales_per_customer=row['Sales per customer'],
            delivery_status=row['Delivery Status'],
            late_delivery_risk=row['Late_delivery_risk'],
            category_id=row['Category Id'],
            category_name=row['Category Name'],
            customer_city=row['Customer City'],
            customer_country=row['Customer Country'],
            customer_segment=row['Customer Segment'],
            customer_state=row['Customer State'],
            customer_zipcode=row['Customer Zipcode'],
            department_id=row['Department Id'],
            department_name=row['Department Name'],
            market=row['Market'],
            order_city=row['Order City'],
            order_country=row['Order Country'],
            order_region=row['Order Region'],
            order_date=row['order date (DateOrders)'],
            order_item_product_price=row['Order Item Product Price'],
            order_item_quantity=row['Order Item Quantity'],
            sales=row['Sales'],
            order_item_total=row['Order Item Total'],
            order_profit_per_order=row['Order Profit Per Order'],
            product_name=row['Product Name'],
            shipping_mode=row['Shipping Mode']
        )
        db.session.add(record)
    try:
        db.session.commit()
        print("CSV data loaded successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error loading CSV: {e}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        load_csv_to_db("data/csv/DataCoSupplyChainDataset.csv")