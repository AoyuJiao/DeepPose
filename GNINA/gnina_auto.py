import os
import subprocess
import pandas as pd
import glob
import re
from concurrent.futures import ProcessPoolExecutor

def process_single_ligand(prot, lig, task_path):
    """
    处理单个分子的打分任务函数
    """
    cmd = ["/usr/local/bin/gnina", "-r", prot, "-l", lig, "--score_only"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    cnn_score, cnn_aff = "N/A", "N/A"
    
    for line in res.stdout.split('\n'):
        score_match = re.search(r"CNNscore:\s*([0-9.]+)", line)
        aff_match = re.search(r"CNNaffinity:\s*([0-9.]+)", line)
        
        if score_match:
            cnn_score = score_match.group(1)
        if aff_match:
            cnn_aff = aff_match.group(1)

    return {
        "Folder": os.path.basename(task_path),
        "Protein": os.path.basename(prot),
        "Ligand": os.path.basename(lig),
        "CNNscore": cnn_score,
        "CNNaffinity": cnn_aff
    }

def run_gnina_task():
    print("="*50)
    print("DeepPose - GNINA 并行打分工具 (仅限 MOL2)")
    print("="*50)
    
    target_path = input("请输入工作路径 (直接回车代表当前路径): ").strip()
    if not target_path:
        target_path = os.getcwd()
    
    max_workers_input = input("请输入并行进程数 (直接回车代表使用系统核心数): ").strip()
    max_workers = int(max_workers_input) if max_workers_input else None

    tasks = []
    def is_valid_task(p):
        return os.path.exists(os.path.join(p, "pdb_files")) and \
               os.path.exists(os.path.join(p, "inference_output"))

    if is_valid_task(target_path):
        tasks.append(target_path)
    else:
        for entry in os.scandir(target_path):
            if entry.is_dir() and is_valid_task(entry.path):
                tasks.append(entry.path)

    if not tasks:
        print("错误：未找到有效的工作文件夹。")
        return

    job_list = []
    for task_path in tasks:
        pdb_dir = os.path.join(task_path, "pdb_files")
        mol_dir = os.path.join(task_path, "inference_output")
        proteins = glob.glob(os.path.join(pdb_dir, "*.pdb"))
        
        # --- 修改点：仅匹配 .mol2 文件 ---
        ligands = glob.glob(os.path.join(mol_dir, "*.mol2"))
        # ------------------------------

        for prot in proteins:
            for lig in ligands:
                job_list.append((prot, lig, task_path))

    total_jobs = len(job_list)
    if total_jobs == 0:
        print("未在 inference_output 中找到 .mol2 文件，请检查路径。")
        return

    print(f"检测到共计 {total_jobs} 个 .mol2 对接任务，准备开始并行打分...")

    all_results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single_ligand, *job) for job in job_list]
        
        for i, future in enumerate(futures):
            result = future.result()
            all_results.append(result)
            print(f"进度: [{i+1}/{total_jobs}] 完成: {result['Ligand']}", end="\r")

    if all_results:
        df = pd.DataFrame(all_results)
        output_name = "gnina_scoring_summary.csv"
        df.to_csv(output_name, index=False)
        print(f"\n{'='*50}")
        print(f"结果汇总完成！已保存至: {output_name}")

if __name__ == "__main__":
    run_gnina_task()