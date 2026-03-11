import os
import subprocess
import pandas as pd
import glob
import re

def run_gnina_task():
    print("="*50)
    target_path = input("请输入工作路径 (直接回车代表当前路径): ").strip()
    if not target_path:
        target_path = os.getcwd()
    
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
        print("错误：未找到有效文件夹。")
        return

    all_results = []
    debug_printed = False

    for task_path in tasks:
        pdb_dir = os.path.join(task_path, "pdb_files")
        mol_dir = os.path.join(task_path, "inference_output")
        proteins = glob.glob(os.path.join(pdb_dir, "*.pdb"))
        ligands = glob.glob(os.path.join(mol_dir, "*.mol2")) + glob.glob(os.path.join(mol_dir, "*.sdf"))

        for prot in proteins:
            for lig in ligands:
                print(f"正在打分: {os.path.basename(lig)} ... ", end="", flush=True)
                
                cmd = ["/usr/local/bin/gnina", "-r", prot, "-l", lig, "--score_only", "--no_gpu"]
                res = subprocess.run(cmd, capture_output=True, text=True)
                
                # 调试用：如果是第一个分子，打印它的原始输出
                if not debug_printed:
                    print("\n--- 调试输出(第一个分子) ---")
                    print(res.stdout)
                    print("--------------------------")
                    debug_printed = True

                cnn_score, cnn_aff = "N/A", "N/A"
                
                # 更加健壮的正则匹配解析
                for line in res.stdout.split('\n'):
                    # 匹配类似 CNNscore: 0.85 或 | CNNscore | 0.85 |
                    score_match = re.search(r"CNNscore:\s*([0-9.]+)", line)
                    aff_match = re.search(r"CNNaffinity:\s*([0-9.]+)", line)
                    
                    if score_match:
                        cnn_score = score_match.group(1)
                    if aff_match:
                        cnn_aff = aff_match.group(1)

                all_results.append({
                    "Folder": os.path.basename(task_path),
                    "Protein": os.path.basename(prot),
                    "Ligand": os.path.basename(lig),
                    "CNNscore": cnn_score,
                    "CNNaffinity": cnn_aff
                })
                print(f"完成")

    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv("gnina_scoring_summary.csv", index=False)
        print(f"\n结果汇总完成！")

if __name__ == "__main__":
    run_gnina_task()
