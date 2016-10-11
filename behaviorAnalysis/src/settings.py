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
        "redis":{
            "host":"192.168.1.111" , 
            "port":"80" , 
            "db":"1" , 
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

#Clusters
clusters = {
        "master":{
            "host":"192.168.1.111" , 
            } ,
        }
