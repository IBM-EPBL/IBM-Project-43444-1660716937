import ibm_db
import ibm_db_dbi
import pandas

dsn_driver = "{IBM DB2 ODBC DRIVER}"
dsn_database = "bludb"
dsn_hostname = "54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud"
dsn_port = "32733"
dsn_protocol = "TCPIP"
dsn_uid = "fmn33477"
dsn_pwd = "JatelsTYIFVJ0iZG"
dsn = (
    "DRIVER={0};"
    "DATABASE={1};"
    "HOSTNAME={2};"
    "PORT={3};"
    "PROTOCOL={4};"
    "UID={5};"
    "PWD={6};"
    "SECURITY=SSL").format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd)


def run(query):
    conn = ibm_db.connect(dsn, "", "")
    print(query)
    create_table = ibm_db.exec_immediate(conn, query)
    return 1


def check(query):
    conn = ibm_db.connect(dsn, "", "")
    print(query)
    try:
        select = ibm_db.exec_immediate(conn, query)
        return ibm_db.num_rows(select)

    except:
        return 0


def view(query):
    conn = ibm_db.connect(dsn, "", "")
    pd_conn = ibm_db_dbi.Connection(conn)
    print(query)
    try:
        select = ibm_db.exec_immediate(conn, query)
        result = []
        dictionary = ibm_db.fetch_assoc(select)
        while dictionary != False:
            result.append(dictionary)
            dictionary = ibm_db.fetch_assoc(select)

        return result

    except:
        return ''