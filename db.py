import psycopg2
import sys


def main(argv):
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="password",
        host="localhost",
        port="5432",
    )

    conn.autocommit = True

    cur = conn.cursor()

    cur.execute(
        """
        create database spire;
        """
    )

    cur.close()


if __name__ == "__main__":
    main(sys.argv)
