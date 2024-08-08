import time

import pandas as pd
import json
import sys
import os

# Global variables
EDGES = []
VERTICES = []
HEADER = ["bID_mID_oID", "priviledged_flow", "object_type", "entity_path","read_relation_type", "write_relation_type","write_argv","read_argv"]
FEATURES = pd.DataFrame(columns=HEADER)

ENTITY_COUNTS = {}
'''
HEADER:
    priviledged_flow    : (binary) 1 if there is a flow from low host to container; 0 otherwise.

    * center entity is the object on which the crossnamespace event is happening. There is only one center entity per json file.
'''
CENTER_ENTITY = None
HOST_IPCNS = None
CLUSTER_IPCNS = None
POLICY_NUMBER = None
IDS=None


def daemon(input_path):
    try:
        read_and_process_file(input_path)
    except Exception as e:
        print(f"Error: {e}"}

def read_and_process_file(input_path):
    # 在这里实现读取和处理文件的逻辑
    # 示例：加载数据、处理数据、保存结果等
    print(f"Processing file: {input_path}")
    # Your processing logic here
    main(input_path, extract_priviledge_flow_docker, HOST_IPCNS)

    # 保存结果
    FEATURES.to_csv("/root/features.csv", index=False)
def set_center_entity(filepath):
    global VERTICES, CENTER_ENTITY
    filepath = os.path.basename(filepath)
    ids = filepath.split(".")[0].split("_")  # [:-1]
    ids[1] = "cf:" + ids[1]
    IDS = ids
    print(ids)

    # updating center entity globally
    for v in VERTICES:
        if str(v["annotations"]["boot_id"]) == ids[0] and str(v["annotations"]["cf:machine_id"]) == ids[1] and str(
                v["annotations"]["object_id"]) == ids[2]:
            CENTER_ENTITY = v

    # print(CENTER_ENTITY)


# Function to extract priviledged_flow for kubernetes environment


# Function to extract priviledged_flow for docker environment
def extract_priviledge_flow_docker():
    global VERTICES, EDGES, CENTER_ENTITY, HOST_IPCNS
    read_relation_types = set()  # 新增
    write_relation_types = set()  # 新增
    # contains a list of the tuples of namespaces
    reader_ns = (set(), set(), set(), set(), set())
    writer_ns = (set(), set(), set(), set(), set())

    # Getting ids of reading processes - type == Used
    ids_from_type_used = []
    # Getting ids of writing processes - type == WasGeneratedBy
    ids_to_type_WGB = []

    for e in EDGES:

        # conditions
        to_center_entity = e["to"] == CENTER_ENTITY["id"]

        edge_type_used = e["type"] == "Used"

        if to_center_entity and edge_type_used:
            ids_from_type_used.append(e["from"])
            read_relation_types.add(e['annotations']['relation_type'])

        from_center_entity = e["from"] == CENTER_ENTITY["id"]

        edge_type_WGB = e["type"] == "WasGeneratedBy"

        if from_center_entity and edge_type_WGB:
            ids_to_type_WGB.append(e["to"])
            write_relation_types.add(e['annotations']['relation_type'])

    vertices_by_id = {v["id"]: v for v in VERTICES}
    edges_from_vset = {}
    edges_from_vset2 = {}
    # 预处理 EDGES，构建从 vset 出发的边的字典
    for e in EDGES:
        if e["from"] not in edges_from_vset:
            edges_from_vset[e["from"]] = []
        edges_from_vset[e["from"]].append(e)
    for e in EDGES:
        if e["to"] not in edges_from_vset2:
            edges_from_vset2[e["to"]] = []
        edges_from_vset2[e["to"]].append(e)
        # 初始化集合
    vset = set()
    entity_path = set()
    task_info = []
    task_info2 = []
    process_memory=[]
    process_memory2=[]
    argv = []
    argv2 = []
    # 遍历 VERTICES，只处理符合条件的顶点
    for v in VERTICES:
        if v["annotations"]["object_id"] == CENTER_ENTITY["annotations"]["object_id"]:
            vset.add(v["id"])
    # 遍历 vset 中的每个顶点，查找相应的边和目标顶点
    #print(vset)
    for vid in vset:
        if vid in edges_from_vset:
            for e in edges_from_vset[vid]:
                if e["annotations"]["to_type"] == "path":
                    target_vertex = vertices_by_id.get(e["to"])
                    if target_vertex:
                        entity_path.add(target_vertex["annotations"]["pathname"])
    for vid in vset:
        if vid in edges_from_vset:
            for e in edges_from_vset[vid]:
                if e["annotations"]["to_type"] == "task":
                    target_task = vertices_by_id.get(e["to"])
                    if target_task:
                        if target_task not in task_info:
                            task_info.append(target_task)
                            #假设这个task是正确的
    for vid in vset:
        if vid in edges_from_vset2:
            for e in edges_from_vset2[vid]:
                if e["annotations"]["from_type"] == "task":
                    target_task = vertices_by_id.get(e["from"])
                    if target_task:
                        if target_task not in task_info2:
                            task_info2.append(target_task)

    # print(task_info)
    # 将 task_info 转换为一个包含所有 id 的集合
    task_ids = {task["id"] for task in task_info}
    task_ids2 = {task["id"] for task in task_info2}
    # 将 VERTICES 转换为字典
    vertices_by_id = {v["id"]: v for v in VERTICES}



    # # 遍历 EDGES，查找符合条件的边
    # for e in EDGES:
    #     if e["from"] in task_ids and e["annotations"]["to_type"] == "process_memory":
    #         target_vertex = vertices_by_id.get(e["to"])
    #         if target_vertex:
    #             if target_vertex not in process_memory:
    #                process_memory.append(target_vertex)
    #                #假设这个process_memory是对的
    # # 打印 process_memory 中的每个顶点信息，每个顶点信息占用一行
    # for vertex in process_memory:
    #     print(vertex)


    # 递归查找 process_memory 实体
    find_process_memory_entities(task_ids, vertices_by_id, EDGES, process_memory)
    find_process_memory_entities2(task_ids2, vertices_by_id, EDGES, process_memory2)

    # 打印 process_memory 中的每个顶点信息，每个顶点信息占用一行
    # for vertex in process_memory:
    #     print(vertex)




    # 将 process_memory 转换为一个包含所有 id 的集合
    process_memory_ids = {p["id"] for p in process_memory}
    process_memory_ids2 = {p["id"] for p in process_memory2}

    # 将 VERTICES 转换为字典
    vertices_by_id = {v["id"]: v for v in VERTICES}

    # 遍历 EDGES，查找符合条件的边
    for e in EDGES:
        if e["from"] in process_memory_ids and e["annotations"]["to_type"] == "argv":
            target_vertex = vertices_by_id.get(e["to"])
            if target_vertex:
                if target_vertex["annotations"]["value"] not in argv:
                    argv.append(target_vertex["annotations"]["value"])
    for e in EDGES:
        if e["from"] in process_memory_ids2 and e["annotations"]["to_type"] == "argv":
            target_vertex = vertices_by_id.get(e["to"])
            if target_vertex:
                if target_vertex["annotations"]["value"] not in argv2:
                    argv2.append(target_vertex["annotations"]["value"])

    # 打印 argv 列表中的每个元素，每个元素占用一行
    for arg in argv:
        print(arg)
    for arg in argv2:
        print(arg)
    # for p in process_memory:
    #     for e in EDGES:
    #         if e["from"] in process_memory and e["annotations"]["to_type"]=="argv":
    #             for v in VERTICES:
    #                 if v["id"] == e["to"]:
    #                     argv.append(v["annotations"]["argv"])
    # for t in task_info:
    #     for e in EDGES:
    #         if e["from"] in task_info and e["annotations"]["to_type"]=="process_memory":
    #             for v in VERTICES:
    #                 if v["id"] == e["to"]:
    #                     process_memory.add(v)
    # print(process_memory)



    # vset=set()
    # entity_path=set()
    # for v in VERTICES:
    #     # if v["id"] in pathid and v["annotations"]["object_type"]=="path":
    #     #     print(v["annotations"]["pathname"])
    #     if v["annotations"]["object_id"]==CENTER_ENTITY["annotations"]["object_id"]:
    #         vset.add(v["id"])
    #         for e in EDGES:
    #             if e["from"] in vset and e["annotations"]["to_type"]=="path":
    #                 for v in VERTICES:
    #                     if v["id"] == e["to"]:
    #                         entity_path.add(v["annotations"]["pathname"])
    for v in VERTICES:
        for id in ids_from_type_used:
            if (v['id'] == id):
                r_ns = (v['annotations']['ipcns'],)
                reader_ns[0].add(r_ns[0])
                # read_relation_types.append(v['annotations']['relation_type'])

        for id in ids_to_type_WGB:
            if (v['id'] == id):
                w_ns = (v['annotations']['ipcns'],)
                writer_ns[0].add(w_ns[0])
                # write_relation_types.append(v['annotations']['relation_type'])  # 新增
        # if str(v["annotations"]["boot_id"]) == IDS[0] and str(v["annotations"]["cf:machine_id"]) == IDS[1] and str(
        #         v["annotations"]["object_id"]) == IDS[2]:
        #     crossnamespace_entities = v
        #     print(crossnamespace_entities)


    print(entity_path)
    check_writer_container = False
    check_reader_host = False
    print(str(writer_ns) + " " + str(reader_ns))
    for ns in writer_ns[0]:
        if str(ns) != HOST_IPCNS:
            check_writer_container = True

    for ns in reader_ns[0]:
        # print(str(HOST_IPCNS)+" "+str(ns))
        # print(isinstance(HOST_IPCNS, int))
        # print(isinstance(ns, int))
        if str(ns) == HOST_IPCNS:
            check_reader_host = True
            # print(check_reader_host)

    priviledged_flow = 0

    if check_reader_host and check_writer_container:
        priviledged_flow = 1
    # if priviledged_flow == 1:
    #     for v in VERTICES:
    #         if v["id"] in pathid and v["annotations"]["object_type"]=="path":
    #            print(v["annotations"]["pathname"])

    return priviledged_flow, CENTER_ENTITY["annotations"]["object_type"],entity_path,read_relation_types, write_relation_types,argv,argv2


# Function to load a graph in a JSON format and store its vertices and edges globally
def load_data(filepath):
    global EDGES, VERTICES

    with open(filepath, "r") as f:
        for line in f:
            if "[" in line or "]" in line:
                continue

            if line[0] == ",":
                obj = json.loads(line[1:])
            else:
                obj = json.loads(line)

            if "from_type" in obj["annotations"]:
                EDGES.append(obj)
                # print(EDGES)
            else:
                VERTICES.append(obj)
                # print(VERTICES)


# Function to extract the identifier <boot_id>_<cf:machine_id>_<object_id>
def extract_identifier():
    global CENTER_ENTITY
    return str(CENTER_ENTITY["annotations"]["boot_id"]) + "_" + \
        str(CENTER_ENTITY["annotations"]["cf:machine_id"]).split(":")[1] + "_" + str(
            CENTER_ENTITY["annotations"]["object_id"])

def find_process_memory_entities(task_ids, vertices_by_id, edges, process_memory):
    # 遍历 EDGES，查找符合条件的边
    found_new = False
    for e in edges:
        if e["from"] in task_ids and e["annotations"]["to_type"] == "process_memory":
            target_vertex = vertices_by_id.get(e["to"])
            if target_vertex and target_vertex not in process_memory:
                process_memory.append(target_vertex)
                found_new = True

    # 如果找到新的 process_memory 实体，递归调用
    if found_new:
        new_task_ids = {vertex["id"] for vertex in process_memory}
        find_process_memory_entities(new_task_ids, vertices_by_id, edges, process_memory)
def find_process_memory_entities2(task_ids, vertices_by_id, edges, process_memory):
    # 遍历 EDGES，查找符合条件的边
    found_new = False
    for e in edges:
        if e["to"] in task_ids and e["annotations"]["from_type"] == "process_memory":
            target_vertex = vertices_by_id.get(e["from"])
            if target_vertex and target_vertex not in process_memory:
                process_memory.append(target_vertex)
                found_new = True

    # 如果找到新的 process_memory 实体，递归调用
    if found_new:
        new_task_ids = {vertex["id"] for vertex in process_memory}
        find_process_memory_entities(new_task_ids, vertices_by_id, edges, process_memory)

def main(filepath, extract_priviledge_flow, host_ipcns, cluster_ipcns=None, policy=None):
    global EDGES, VERTICES, FEATURES, HOST_IPCNS, CLUSTER_IPCNS, POLICY_NUMBER

    HOST_IPCNS = host_ipcns
    CLUSTER_IPCNS = cluster_ipcns
    POLICY_NUMBER = policy

    with open(filepath, "r") as f:
        files = f.readlines()
    
    counter = 1
    for file in files:
        # EDGES.clear()
        # VERTICES.clear()
        #print(os.path.basename(file.strip()))
        load_data(file.strip())

        set_center_entity(file.strip())

        priviledged_flow, object_type, entity_path,read_relation_types, write_relation_types,write_argv,read_argv = extract_priviledge_flow()
        bID_mID_oID = extract_identifier()

        data_point = {HEADER[0]: bID_mID_oID,
                      HEADER[1]: priviledged_flow,
                      HEADER[2]: object_type,
                      HEADER[3]: ','.join(entity_path),
                      HEADER[4]: ','.join(read_relation_types),
                      HEADER[5]: ','.join(write_relation_types),
                      HEADER[6]: ','.join(write_argv),
                      HEADER[7]: ','.join(read_argv),
                      }

        FEATURES = FEATURES._append(data_point, ignore_index=True)

        print("********** " + str(counter) + " JSON file(s) processed **********\n")
        counter = counter + 1

    #FEATURES.to_csv("features.csv", index=False)


if __name__ == '__main__':
    exception_docker = "For Docker:\n\trun python3 csv_generator.py docker <filepath> <host_ipcns>"
    exception_kube = "For Kubernetes:\n\trun python3 csv_generator.py kube <filepath> <host_ipcns> <cluster_ipcns> <policy_number>"
    exception_msg = exception_docker + "\n" + exception_kube
    try:
        if len(sys.argv) < 2:
            raise Exception(exception_msg)
        else:

            if sys.argv[1] == "docker":
                if len(sys.argv) == 4:
                    print("Starting...")
                    print("Filepath:", sys.argv[2])
                    print("Host IPCNS:", sys.argv[3])
                    daemon(sys.argv[2])
                    #main(sys.argv[2], extract_priviledge_flow_docker, sys.argv[3])
                else:
                    raise Exception(exception_msg)

            elif sys.argv[1] == "kube":
                if len(sys.argv) == 6:
                    print("Starting...")
                    print("Filepath:", sys.argv[2])
                    print("Host IPCNS:", sys.argv[3])
                    print("Cluster IPCNS:", sys.argv[4])
                    print("Policy number:", sys.argv[5])
                    main(sys.argv[2], extract_priviledge_flow_kubernetes, sys.argv[3], sys.argv[4], sys.argv[5])
                else:
                    raise Exception(exception_msg)

            else:
                raise Exception(exception_msg)


    except KeyboardInterrupt:
        print("Exiting...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
