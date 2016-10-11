#FolderPath
"""
folder_path = {
    "config":"/config" , 
    "log":"/logs" , 
    "result":"/dataResults" , 
    }
"""
folder_path = {
    "config":"/config" , 
    "log":"/logs" , 
    "lib":"/lib" , 
    "result":"/dataResults" , 
    "dsource":"/dataSources" ,
    }


#DataBase
"""
data_base = {
    data_base_name:{
        "hostname":"" , 
        "user":"" , 
        "passwd":"" , 
        } , 
    }
"""
data_base = {
        "oracle":{
            "hostname":"192.168.1.115/orcl" , 
            "user":"c##ht" , 
            "passwd":"ht" , 
            } ,
        }


#DirPath
"""
dir_path = {
    "hdfs_path":"" , 
    "local_path":"" , 
    }
"""
dir_path = {
        "hdfs_path":"" , 
        "local_path":"/home/ployo/data/xdr/s1u_http"
        }


#SparkConfig
"""
"""
spark_config = {
        "spark_url":"spark://192.168.1.111:7077" , 
        "spark_conf_settings":{
            "spark.cores.max":"4" , 
            "spark.executor.memory":"4g" , 
            "spark.default.parallelism":"16" , 
            } , 
        }

