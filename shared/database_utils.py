"""Database utilities for ETL tests."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    create_engine,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Transaction(Base):
    """Transaction table model."""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    discount_percent = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    shipping_country = Column(String(100), nullable=False)
    customer_email = Column(String(200), nullable=False)


class TransactionSummary(Base):
    """Transaction summary table model."""
    
    __tablename__ = "transaction_summary"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False)
    total_transactions = Column(Integer, nullable=False)
    total_revenue = Column(Float, nullable=False)
    avg_order_value = Column(Float, nullable=False)
    total_quantity = Column(Integer, nullable=False)


def get_database_url(
    host: str = "localhost",
    port: int = 5432,
    database: str = "orchestrator_test",
    user: str = "postgres",
    password: str = "postgres",
) -> str:
    """Get PostgreSQL database URL."""
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def create_tables(database_url: str):
    """Create database tables."""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    print("✓ Database tables created successfully!")


def drop_tables(database_url: str):
    """Drop database tables."""
    engine = create_engine(database_url)
    Base.metadata.drop_all(engine)
    print("✓ Database tables dropped successfully!")


def get_engine(database_url: str):
    """Get SQLAlchemy engine."""
    return create_engine(database_url, pool_pre_ping=True)


def get_session(database_url: str):
    """Get database session."""
    engine = get_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()


def truncate_tables(database_url: str):
    """Truncate all tables."""
    engine = get_engine(database_url)
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE transactions CASCADE"))
        conn.execute(text("TRUNCATE TABLE transaction_summary CASCADE"))
        conn.commit()
    print("✓ Tables truncated successfully!")


if __name__ == "__main__":
    import sys
    
    db_url = get_database_url()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "create":
            create_tables(db_url)
        elif command == "drop":
            drop_tables(db_url)
        elif command == "truncate":
            truncate_tables(db_url)
        else:
            print(f"Unknown command: {command}")
            print("Usage: python database_utils.py [create|drop|truncate]")
    else:
        print("Usage: python database_utils.py [create|drop|truncate]")
