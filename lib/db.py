import psycopg2
from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import URL

load_dotenv()

metadata_obj = MetaData()

def get_psycopg2_connection(dbname: str = "quakemapper"):
    return psycopg2.connect(
        dbname=dbname,
    )


def get_engine(dbname: str = "quakemapper"):
    return create_engine(
        URL.create("postgresql+psycopg2",
            database=dbname),
            echo=False
    )
