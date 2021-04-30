from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from datetime import datetime, timedelta
#from airflow.operators.python import PythonOperator
#from airflow.operators.python import pythonoperator
#from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import date

###############################################
# Parameters
###############################################
spark_master = "spark://spark:7077"
spark_app_name = "Spark Hello World"
file_path = "/usr/local/spark/resources/data/airflow.cfg"

###############################################
# DAG Definition
###############################################
now = datetime.now()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(now.year, now.month, now.day),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5)
}

def print_hello(hi_to):
 return 'Hello Wolrd' + hi_to

def getmktdata(stock1):
    
    import yfinance as yf
    start_date = date.today()
    
    end_date = start_date - timedelta(days=1)
    
    tsla_df = yf.download(stock1, start=end_date, end=start_date, interval='1m')
    tsla_df.to_csv("tmp/data/" + date.today().strftime('%Y-%m-%d') + "/data.csv", header = False)
    return True

def opencsvdata():

    import pandas as pd
    df = pd.read_csv("tmp/data/" + date.today().strftime('%Y-%m-%d') + "/data.csv", header = None)
    print(df.head())
    print(df.tail())

    return True


dag = DAG(
        'marketvol',
        default_args=default_args,
        description='A simple DAG',
        schedule_interval=timedelta(days=1),
)

task_0 = BashOperator(
        task_id="task_0",
        #bash_command='''ls''',
        bash_command='''mkdir -p /usr/local/airflow/tmp/data/''' + date.today().strftime('%Y-%m-%d'), #naming the folder with the current day
        
        dag=dag,
    )

b1 = BashOperator(
    task_id='pip3_install_yfinance',
    bash_command='pip3 install yfinance',
    dag=dag, 
)


t1 = PythonOperator(
    task_id='get_the_mktdata_aapl',
    python_callable=getmktdata,
    op_kwargs={'stock1': 'AAPL'},
    dag=dag
)

t2 = PythonOperator(
    task_id='get_the_mktdata_tsla',
    python_callable=getmktdata,
    op_kwargs={'stock1': 'TSLA'},
    dag=dag
)


t3 = PythonOperator(
    task_id='make_t3',
    python_callable=opencsvdata,
    #op_kwargs={'stock1': 'AAPL'},
    dag=dag
)


b1 >> task_0 >> t1
task_0 >> t2
[t1, t2] >> t3
#t2 >> t4
